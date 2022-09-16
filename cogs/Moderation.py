import discord
import asyncio
import re
from discord.ext import commands, tasks
from discord.ext.commands import UserConverter
from discord.utils import get
import json 
import pyrebase
import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta


with open("json/FirebaseCreds.json", "r") as f:
    firebaseConfig = json.load(f)


conv_dict = {
    'w': 'weeks',
    'd': 'days',
    'h': 'hours',
    'm': 'minutes',
    's': 'seconds',
}

pat = r'[0-9]+[s|m|h|d|w]{1}'


class Moderation(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.mute_task = self.check_current_mutes.start()

    def cog_unload(self):
        self.mute_task.cancel()

    @tasks.loop(minutes=5)
    async def check_current_mutes(self):
        currentTime = datetime.datetime.now()	
        mutes = self.db.child("Mutes").get()
        if mutes.val() == None:
            return

        for key, value in mutes.val().items():

            unmuteTime = parser.parse(value['mutedAt']) + relativedelta(seconds=value['muteDuration'])

            if currentTime >= unmuteTime:
                try:
                    guild = self.bot.get_guild(882126649687175199) # 882126649687175199
                    member = guild.get_member(value['_id'])

                    role = discord.utils.get(guild.roles, name="Muted")
                    if role in member.roles:
                        await member.remove_roles(role)
                        
                        embed = discord.Embed(
                            colour=0xF1F1F1,
                            title="unmute | Member Unmuted",
                            description=f"{member.mention} has been unmuted. \nAuto-unmute for mute made **{value['textDuration']}**ago \nMuted By:** <@{value['mutedBy']}>**"
                        )
                        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
                        embed.set_footer(text=f"ID: {member.id}")

                        self.db.child("Mutes").child(member.id).remove()

                        for channel_id in [882126651411021881]:
                            embed_channel = self.bot.get_channel(channel_id)
                            await embed_channel.send(embed=embed)

                    else:
                        self.db.child("Mutes").child(member.id).remove()	

                except:
                    self.db.child("Mutes").child(value['_id']).remove()


    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):

        self.firebase = pyrebase.initialize_app(firebaseConfig)
        self.db = self.firebase.database()


    # Cog error handler
    async def cog_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("<:redtick:847843079938506812> You don't have the required permissions to use this command.")

        else:
            raise error
    
    # Purge
    @commands.command(name = 'purge', help = '**Moderation Command** \nPurges the messages in a channel.\nUse `c.purge [*amount]`\n `amount` is an integer and an optional param. Leaving it empty would delete the default amount of messages, which is set to 5.')
    @commands.has_permissions(manage_messages = True)
    async def purge(self, ctx, amount = 5):
        await ctx.channel.purge(limit=amount+1)

        if ctx.channel.id not in [882126651025158167,882126651025158169,882126651411021879,882126651411021880, 882126651411021881]:
            
            embed = discord.Embed(
                colour=0xF1F1F1,
                title="Messages Purged",
                description=f"{amount} messages were purged in <#{ctx.channel.id}> by {ctx.author.mention}."
            )

            log_channel = self.bot.get_channel(882126651411021879)

            await log_channel.send(embed=embed)


    # Kick
    @commands.command(name = 'kick', help = '**Moderation Command** \nKicks a member. \nUse `c.kick [member] [reason]`\n`member` param can either be a member id or a member ping. `reason` is a required param for recording purposes.')
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member : discord.Member, *, reason = "Not Specified"):
        if member == None or member == ctx.message.author:
            await ctx.send("You cannot kick yourself!")
            return
        elif ctx.guild.roles.index(member.roles[-1]) >= ctx.guild.roles.index(ctx.author.roles[-1]):
            await ctx.send("Can't kick someone higher or equal to in role hierarchy.")
            return

        try:
            await member.send(f"You were kicked from COALI Discord. Reason: {reason}")
        except:
            pass

        await member.kick(reason=reason)
        embed = discord.Embed(
            colour=0xF1F1F1,
            title="Member Kicked!",
            description=f"**Kicked {member.display_name}!** \n**Reason:** {reason} \n**Kicked By:** {ctx.author.mention}"
        )
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
        embed.set_footer(text=f"ID: {member.id}")
        
        for channel_id in [ctx.channel.id,882126651411021881]:
            embed_channel = self.bot.get_channel(channel_id)
            await embed_channel.send(embed=embed)

    # Ban
    @commands.command(name = 'ban', help = '**Moderation Command** \nBans a member.\nUse `c.ban [member] [reason]`\n`member` param can either be a member id or a member ping. `reason` is a required param for recording purposes.')
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member : discord.Member, *, reason = "Not Specified"):
        if member == None or member == ctx.message.author:
            await ctx.send("You cannot ban yourself!")
            return
        elif ctx.guild.roles.index(member.roles[-1]) >= ctx.guild.roles.index(ctx.author.roles[-1]):
            await ctx.send("Can't ban someone higher or equal to in role hierarchy.")
            return

        try:
            await member.send(f"You were banned from COALI Discord. Reason: {reason} \n For appeals, contact eebs#0027 or indirectly through a server member.")
        except:
            pass


        await member.ban(reason=reason)
        embed = discord.Embed(
            colour=0xF1F1F1,
            title="Member Banned!",
            description=f"**Banned {member.display_name}!** \n**Member ID:** {member.id} \n**Reason:** {reason} \n**Banned By:** {ctx.author.mention}"
        )
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
        embed.set_footer(text=f"ID: {member.id}")

        for channel_id in [ctx.channel.id,882126651411021881]:
            embed_channel = self.bot.get_channel(channel_id)
            await embed_channel.send(embed=embed)
    
    # Hackban
    @commands.command(name="hackban", help= "**Moderation Command** \nBans a member which either exists or doesn't exists in the server. Also deletes the messages done by the member in last 7 days. \n\u3164\n**General Format:** \n`<prefix>hackban [member_id] [*reason]` \n\u3164\n**Parameters**: \n`member_id` --> Is the id of the member you want to ban. Can only be an integer. \n`reason` --> The reason for why you want to ban. Is a multiword string and is optional, but recommended.")
    @commands.has_guild_permissions(ban_members=True)
    async def hackban(self, ctx, member_id:int, *, reason:str):
        # Fetch Member
        try:
            member = await ctx.guild.fetch_member(member_id)
        except:
            pass

        # Necessary Checks
        if member == None:
            pass
        elif member == ctx.message.author:
            await ctx.send("You cannot ban yourself!")
            return
        elif ctx.guild.roles.index(member.roles[-1]) >= ctx.guild.roles.index(ctx.author.roles[-1]):
            await ctx.send("Can't ban someone higher or equal to in role hierarchy.")
            return
        
        # Hackbanning
        try:
            await ctx.guild.ban(discord.Object(id=member_id), reason=reason, delete_message_days=7)
        
        # Handling HTTPEXception
        except discord.HTTPException:
            await ctx.send("Failed to ban the person.")
            return

        # Log Embed
        embed = discord.Embed(
            colour=0xF1F1F1,
            title="ban | Member Hack Banned!",
            description=f"**Member ID:** {member_id} \n**Reason:** {reason} \n**Banned By:** {ctx.author.mention}"
        )

        embed.set_footer(text=f"ID: {member_id}")

        # Sending Log Embed
        for channel_id in [ctx.channel.id,882126651411021881]:
            embed_channel = self.bot.get_channel(channel_id)
            await embed_channel.send(embed=embed)
        
    @hackban.error
    async def hackban_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'member_id':
                await ctx.send("Kindly provide a valid member id to ban.")
    
        elif isinstance(error, commands.BadArgument):
            await ctx.send("<:redtick:847843079938506812> `member_id` can only be an integer. Check if you provided a valid member id.")


    # Unban
    @commands.command(name = 'unban', help = '**Moderation Command** \nUnbans a member. \nUse `c.unban [member]`\n`member` param can either be a member id or a member ping.')
    @commands.has_guild_permissions(ban_members = True)
    async def unban(self, ctx, member_id:int):

        member = discord.Object(id=member_id) # user ID
        try:
            await ctx.guild.unban(member)
        except discord.NotFound:
            await ctx.send("Member not found.")
            return
            
        await ctx.send("Member Unbanned.")
        
        # embed = discord.Embed(
        # 	colour=0xF1F1F1,
        # 	title="Member Unbanned",
        # 	description=f"<@{member.id}> has been unbanned by {ctx.author.mention}"
        # )
        # embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
        # embed.set_footer(text=f"ID: {member.id}")
        
        # for channel_id in [ctx.channel.id,882126651411021881]:
        # 	embed_channel = self.bot.get_channel(channel_id)
        # 	await embed_channel.send(embed=embed)

    # Mute
    @commands.command(name = 'mute', help = '**Moderation Command** \nMutes a member.\nUse `c.mute [member] [*time period] [reason]`\n `member` param can either be a member id or a member ping.\n`duration` is a time expression which represents the time for which the member is to be muted for, and can be left for an indefinite mute.\n`reason` is a required param for recording purposes.')
    @commands.has_guild_permissions(ban_members = True)
    async def mute(self, ctx, member: discord.Member, timeduration: str = "0s", *, reason: str = "Not specified"):

        if member == ctx.author:
            await ctx.send("You can't mute yourself!")
            return	
        elif ctx.guild.roles.index(member.roles[-1]) >= ctx.guild.roles.index(ctx.author.roles[-1]):
            await ctx.send("Can't mute someone higher or equal to in role hierarchy.")
            return
        elif member == None:
            return


        if timeduration:
            TimeDict = {conv_dict[p[-1]]: int(p[:-1]) for p in re.findall(pat, timeduration)}
            textDuration = ""
            try:
                if TimeDict['weeks'] == 1:
                    time_w = f"{TimeDict['weeks']} week "
                else:
                    time_w = f"{TimeDict['weeks']} weeks "
                textDuration += time_w
            except KeyError:
                pass
            try:
                if TimeDict['days'] == 1:            
                    time_d = f"{TimeDict['days']} day "
                else:
                    time_d = f"{TimeDict['days']} days "
                textDuration += time_d
            except KeyError:
                pass 
            try: 
                if TimeDict['hours'] == 1:            
                    time_h = f"{TimeDict['hours']} hour "
                else:
                    time_h = f"{TimeDict['hours']} hours "
                textDuration += time_h
            except KeyError:
                pass            
            try:     
                if TimeDict['minutes'] == 1:               
                    time_m = f"{TimeDict['minutes']} minute "
                else:
                    time_m = f"{TimeDict['minutes']} minutes "
                textDuration += time_m             
            except KeyError:
                pass
            try:        
                if TimeDict['seconds'] == 1:            
                    time_s = f"{TimeDict['seconds']} second "
                else:
                    time_s = f"{TimeDict['seconds']} seconds "
                textDuration += time_s
            except KeyError:
                pass
            MuteTime = int(datetime.timedelta(**TimeDict).total_seconds())
        else:
            pass

        role = discord.utils.get(ctx.guild.roles, name="Muted") 
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`.")
            return

        data = {
            '_id': member.id,
            'mutedAt': str(datetime.datetime.now()),
            'muteDuration': MuteTime or None,
            'mutedBy': ctx.author.id,
            'textDuration': textDuration,
        }


        if MuteTime >= 300: # time is large so it stores in db (unmute task loops with intervals)
            self.db.child("Mutes").child(member.id).set(data)
            await member.add_roles(role)

            embed = discord.Embed(
                colour=0xF1F1F1,
                title="mute | Member Muted",
                description=f"{member.mention} has been muted for **{textDuration}** \n**Reason:** {reason} \n**Muted By:** {ctx.author.mention}"
            )
            embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
            embed.set_footer(text=f"ID: {member.id}")

            #Add to modlog
            member_id = f"{member.id}"
            members = self.db.child("Warns").get().val()

            ctx_time = datetime.datetime.now().strftime("%d-%m-%Y")

            entry_value = f"{ctx.author.name}#{ctx.author.discriminator}${ctx_time}${reason}$mute"

            if members == None or member_id not in members.keys():
                data = [entry_value]
                self.db.child("Warns").child(member_id).set(data)

            else:
                data = members[member_id]
                data.append(entry_value)
                self.db.child("Warns").update({member_id:data})

            try:
                await member.send(f"You were muted for {textDuration} in COALI Discord. Reason: {reason}")
            except:
                pass

            for channel_id in [ctx.channel.id,882126651411021881]: #882126651411021881
                embed_channel = self.bot.get_channel(channel_id)
                await embed_channel.send(embed=embed)

        elif MuteTime < 300 and MuteTime > 0: #time is small, but why mute for small times?

            await member.add_roles(role)

            embed = discord.Embed(
                colour=0xF1F1F1,
                title="mute | Member Muted",
                description=f"{member.mention} has been muted for **{textDuration}** \n**Reason:** {reason} \n**Muted By:** {ctx.author.mention}"
            )
            embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
            embed.set_footer(text=f"ID: {member.id}")

            try:
                await member.send(f"You were muted for {textDuration} in COALI Discord. Reason: {reason}")
            except:
                pass

            for channel_id in [ctx.channel.id,882126651411021881]: #882126651411021881
                embed_channel = self.bot.get_channel(channel_id)
                await embed_channel.send(embed=embed)

            await asyncio.sleep(int(MuteTime))

            if role in member.roles:
                await member.remove_roles(role)

                embed = discord.Embed(
                    colour=0xF1F1F1,
                    title="unmute | Member Unmuted",
                    description=f"{member.mention} has been unmuted. \n**Auto-unmute for mute made {textDuration} ago** \nMuted By:** {ctx.author.mention}**"
                )
                embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
                embed.set_footer(text=f"ID: {member.id}")

                for channel_id in [882126651411021881]: # 882126651411021881
                    embed_channel = self.bot.get_channel(channel_id)
                    await embed_channel.send(embed=embed)

        elif MuteTime == 0: #time not provided, but reason is (the first argument is treated as time)
            await member.add_roles(role)

            if timeduration == "0s":
                ind_reason = reason
            elif timeduration != "0s" and reason != "Not specified":
                ind_reason = timeduration + " " + reason
            elif timeduration != "0s" and reason == "Not specified":
                ind_reason = timeduration

            embed = discord.Embed(
                colour=0xF1F1F1,
                title="mute | Member Muted",
                description=f"{member.mention} has been muted indefinitely.\n**Reason:** {ind_reason}\n**Muted By:** {ctx.author.mention}"
            )
            embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
            embed.set_footer(text=f"ID: {member.id}")

            #Add to modlog
            member_id = f"{member.id}"
            members = self.db.child("Warns").get().val()

            ctx_time = datetime.datetime.now().strftime("%d-%m-%Y")

            entry_value = f"{ctx.author.name}#{ctx.author.discriminator}${ctx_time}${reason}$mute"

            if members == None or member_id not in members.keys():
                data = [entry_value]
                self.db.child("Warns").child(member_id).set(data)

            else:
                data = members[member_id]
                data.append(entry_value)
                self.db.child("Warns").update({member_id:data})

            try:
                await member.send(f"You were muted indefinitely in COALI Discord. Reason: {ind_reason}")
            except:
                pass

            for channel_id in [ctx.channel.id,882126651411021881]: #882126651411021881
                embed_channel = self.bot.get_channel(channel_id)
                await embed_channel.send(embed=embed)


    # Unmute
    @commands.command(name = 'unmute', help = '**Moderation Command** \nUnmutes a member.\nUse `c.unmute [member]`\n`member` param can either be a member id or a member ping.')
    @commands.has_permissions(ban_members = True)
    async def unmute(self, ctx, member: discord.Member):
        role = get(ctx.guild.roles, name = 'Muted')

        if role in member.roles:
            await member.remove_roles(role)

            embed = discord.Embed(
                colour=0xF1F1F1,
                title="un-mute | Member Unmuted",
                description=f"{member.mention} has been unmuted. \n**Unmuted by:** {ctx.author.mention}"
            )
            embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
            embed.set_footer(text=f"ID: {member.id}")

            for channel_id in [ctx.channel.id,882126651411021881]: #882126651411021881
                embed_channel = self.bot.get_channel(channel_id)
                await embed_channel.send(embed=embed)

        mutes = self.db.child("Mutes").get()
        if mutes.val() == None:
            return

        for key, value in mutes.val().items():
            if member.id == value['_id']:
                self.db.child("Mutes").child(member.id).remove()

    # Channel Lock
    @commands.command(name = 'lock', help="**Moderation Command** \nLocks the channel.\nUse `c.lock [*channel]`\n`channel` can either be a channel id or a channel mention and is an optional param. Leaving it empty would simply lock the channel in context.")
    @commands.has_any_role("Server Admin", "Discord Mods", "Trial Mods")
    # @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel:discord.TextChannel=None):
        if channel == None:
            channel = ctx.channel

        role = ctx.guild.default_role

        if channel.overwrites_for(role).send_messages is False:
            await ctx.send("This channel is already locked down.")
            return
        
        perms = channel.overwrites_for(role)
        perms.send_messages = False
        await channel.set_permissions(role, overwrite=perms, reason=f"Lockdown Issued by {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})")

        await ctx.send(f":white_check_mark: Locked down **{channel.name}**.")

        embed = discord.Embed(
                colour=0xF1F1F1,
                title="Channel Locked",
                description=f"Lockdown for <#{channel.id}> issued by {ctx.author.mention}."
            )
        embed.set_footer(text=f"ID: {ctx.author.id}")

        log_channel = self.bot.get_channel(882126651411021881)

        await log_channel.send(embed=embed)

    # Channel Unlock
    @commands.command(name = 'unlock', help="**Moderation Command** \nUnlocks a locked channel.\nUse `c.unlock [*channel]`\n`channel` can either be a channel id or a channel mention and is an optional param. Leaving it empty would simply unlock the channel in context.")
    @commands.has_any_role("Server Admin", "Discord Mods", "Trial Mods")
    # @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel:discord.TextChannel=None):
        if channel == None:
            channel = ctx.channel

        role = ctx.guild.default_role
        
        if channel.overwrites_for(role).send_messages is not False:
            await ctx.send("This channel is not locked down.")
            return

        perms = channel.overwrites_for(role)
        perms.send_messages = None
        await channel.set_permissions(role, overwrite=perms, reason=f"Lockdown Removal Issued by {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})")

        await ctx.send(f":white_check_mark: Unlocked **{channel.name}**.")

        embed = discord.Embed(
                colour=0xF1F1F1,
                title="Channel Unlocked",
                description=f"Lockdown Removal for <#{channel.id}> issued by {ctx.author.mention}."
            )
        embed.set_footer(text=f"ID: {ctx.author.id}")

        log_channel = self.bot.get_channel(882126651411021881)

        await log_channel.send(embed=embed)

    # Channel Move
    @commands.command(name = 'movechannel', aliases=["shiftchannel", "shift"], help="**Moderation Command** \nLocks the channel to aid shifting to another channel, then unlocks.\nUse `c.movechannel [channel]`\n`channel` can either be a channel id or a channel mention and is a required param.")
    @commands.has_any_role("Server Admin", "Discord Mods", "Trial Mods")
    async def movechannel(self, ctx, channel:discord.TextChannel=None):
        await ctx.message.delete()
        if channel == None or channel == ctx.channel:
            return

        await ctx.send(f"A staff member has asked to shift the conversation to {channel.mention}. Please move to the requested channel.")        
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        embed = discord.Embed(
                colour=0xF1F1F1,
                title="Channel Shifting",
                description=f"Channel shifting from {ctx.channel.mention} to {channel.mention} requested by {ctx.author.mention}."
            )
        embed.set_footer(text=f"ID: {ctx.author.id}")

        log_channel = self.bot.get_channel(882126651411021881)

        await log_channel.send(embed=embed)

        await asyncio.sleep(10)
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)



    # Channel Slowmode
    @commands.command(name = 'slowmode', aliases=["slomo"], help="**Moderation Command** \nUse `c.slowmode [enable/disable] [duration]`\nEdits slowmode for the channel in context. Can either enable or disable slowmode. `duration` is a time expression (an optional param). Maximum duration is 6 hours or its unitary equivalent. Default set to 5s.")
    @commands.has_any_role("Server Admin", "Discord Mods", "Trial Mods")
    # @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, mode="enable", timeduration="5s"):
        try:
            time = int(datetime.timedelta(**{conv_dict[p[-1]]: int(p[:-1]) for p in re.findall(pat, timeduration)}).total_seconds())
            mode_time = int(datetime.timedelta(**{conv_dict[p[-1]]: int(p[:-1]) for p in re.findall(pat, mode)}).total_seconds())
        except ValueError:
            await ctx.send("<:redtick:847843079938506812> Slowmode duration should be a positive integer.")
            return
        except KeyError:
            await ctx.send("<:redtick:847843079938506812> Provide the time in the correct format. That's right, smh.")
            return

        if mode == "enable":
            if time > 0 and time <= 21600:
                await ctx.channel.edit(slowmode_delay=time)
                await ctx.send(f":white_check_mark: Slowmode enabled and set to {timeduration}")
                slomo_prompt = f"Slowmode enabled in <#{ctx.channel.id}> and set to {timeduration} by {ctx.author.mention}."

            else:
                await ctx.send("<:redtick:847843079938506812> You need to give a valid time duaration. At max slowmode can be set to `6h`. Should be greater than `0s`.")
                return

        elif mode == "disable":
            await ctx.channel.edit(slowmode_delay=0)
            await ctx.send(":white_check_mark: Slowmode disabled.")
            slomo_prompt = f"Slowmode disabled in <#{ctx.channel.id}> by {ctx.author.mention}."

        elif mode != "enable" and mode != "disable" and isinstance(mode_time, int):
            if mode_time > 0 and mode_time <= 21600:
                await ctx.channel.edit(slowmode_delay=mode_time)
                await ctx.send(f":white_check_mark: Slowmode enabled and set to {mode}")
                slomo_prompt = f"Slowmode enabled in <#{ctx.channel.id}> and set to {mode} by {ctx.author.mention}."

            else:
                await ctx.send("<:redtick:847843079938506812> You need to give a valid time duaration. At max slowmode can be set to `6h`. Should be greater than `0s`.")
                return

        else:
            await ctx.send("<:redtick:847843079938506812> Incorrect command usage. \nUse `c.slowmode <enable/disable> <duration>` to use command. \nWhere: \n `s` --> *Seconds* \n `m` --> *Minutes* \n `h` --> *Hours*")
            return

        embed = discord.Embed(
                colour=0xF1F1F1,
                description=f"{slomo_prompt}"
            )
        embed.set_footer(text=f"ID: {ctx.author.id}")

        log_channel = self.bot.get_channel(882126651411021881)

        await log_channel.send(embed=embed)

    # Error Handler
    @slowmode.error
    async def slowmode_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'mode':
                await ctx.send("<:redtick:847843079938506812> Incorrect command usage. \n\nUse `c.slowmode <enable/disable> <duration>` to use command. \nWhere: \n `s` --> *Seconds* \n `m` --> *Minutes* \n `h` --> *Hours*")

    # # Modbreak Command
    # @commands.command(aliases=["modbreak","givebreak"], help="Gives the mod a break role. Strips him off all duties. \nUse `<prefix>wantbreak` to take break. \n**Aliases:** `givebreak`, `modbreak`.")
    # @commands.has_role("Discord Mods")
    # async def wantbreak(self, ctx):
    #     # Remove Mod Role
    #     modrole = ctx.guild.get_role(695627434820632607)
    #     await ctx.author.remove_roles(modrole)

    #     # Add Mods On Break Role
    #     breakrole = ctx.guild.get_role(811534215433682975)
    #     await ctx.author.add_roles(breakrole) 

    #     # Send Confirmation
    #     await ctx.send(":white_check_mark: Break Role successfully given. Enjoy your vacation! :))")

    #     # Log Embed
    #     embed = discord.Embed(
    #             colour=0xC3C3C3,
    #             title="Mod Break Taken",
    #             description=f"{ctx.author.mention} has been barred off all mod duties due to taking a break. Happy Vacation. :))"
    #         )
    #     embed.set_footer(text=f"ID: {ctx.author.id}")

    #     # Send Logs
    #     log_channel = self.bot.get_channel(882126651411021881)
    #     await log_channel.send(embed=embed)

    # # Modbreak Over Command
    # @commands.command(aliases=["endbreak","breakend"], help="Ends the mod break. Gives you back the Mod role. \nUse `<prefix>breakover` to end break. \n**Aliases:** `endbreak`, `breakend`.")
    # @commands.has_role("Mod on break")
    # async def breakover(self, ctx):
    #     # Remove Break Role
    #     breakrole = ctx.guild.get_role(811534215433682975)
    #     await ctx.author.remove_roles(breakrole)

    #     # Add Mods Role
    #     modrole = ctx.guild.get_role(695627434820632607)
    #     await ctx.author.add_roles(modrole) 

    #     # Send Confirmation
    #     await ctx.send(":white_check_mark: Break Ended. Welcome back!")

    #     # Send Log Embed
    #     embed = discord.Embed(
    #             colour=0xC3C3C3,
    #             title="Mod Break Ended",
    #             description=f"{ctx.author.mention} has been awarded back all mod duties due to coming back from a break. Welcome back! :))"
    #         )
    #     embed.set_footer(text=f"ID: {ctx.author.id}")

    #     # Send Logs
    #     log_channel = self.bot.get_channel(882126651411021881)
    #     await log_channel.send(embed=embed)

    # Server Lockdown Invoke
    @commands.command(aliases=["lockdown","sl","lockinvoke"], help="**Moderation Command**\nUse to lock the whole server. \n\u3164\n**General Format:**\n`<prefix>serverlock` \n\u3164\n**Aliases:**`lockdown`,`sl` and `lockinvoke`. \n\u3164\n**Note:** Use this command with extreme caution as it locks down the whole server!")
    @commands.has_any_role("Server Admin", "Discord Mods", "Trial Mods")
    async def serverlock(self, ctx):
        # Checking if server already unlocked
        if ctx.guild.default_role.permissions.send_messages is False:
            await ctx.send("Server already locked.")
            return 
        
        # Server Locked
        try:
            everyone_perms = ctx.guild.default_role.permissions
            everyone_perms.send_messages=False

            await ctx.guild.default_role.edit(permissions=everyone_perms, reason=f"Server Lockdown imposed by {ctx.author}")
        
        # Handling Forbidden Permissions Exception
        except discord.Forbidden as e:
            await ctx.send("I don't have the required permissions to do this.")
            return

        # Handling HTTPException
        except discord.HTTPException as e:
            await ctx.send("HTTPException Occurred.")
            raise e

        # Send Confirmation
        await ctx.send(":lock: Server Locked.")

        # Context Time
        ctx_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M GMT+5")

        # Log Embed
        embed = discord.Embed(
                colour=0xC3C3C3,
                title="Server Lockdown Imposed",
                description=f"Server Lockdown imposed by {ctx.author.name}#{ctx.author.discriminator} {ctx.author.mention}"
            )
        embed.set_footer(text=f"Invoke Time: {ctx_time}")

        # Send Logs
        log_channel = self.bot.get_channel(882126651411021881)
        await log_channel.send(embed=embed)

    # Server Lockdown Revoke
    @commands.command(aliases=["opendown","su","lockrevoke"], help="**Moderation Command**\nUse to unlock the whole server (if locked down). \n\u3164\n**General Format:**\n`<prefix>serverunlock` \n\u3164\n**Aliases:**`opendown`,`su` and `lockrevoke`.")
    @commands.has_any_role("Server Admin", "Discord Mods", "Trial Mods")
    async def serverunlock(self, ctx):
        # Checking if server already unlocked
        if ctx.guild.default_role.permissions.send_messages is True:
            await ctx.send("No lockdown to unlock. ¯\_(ツ)_/¯")
            return 

        # Server Unlocked
        try:
            everyone_perms = ctx.guild.default_role.permissions
            everyone_perms.send_messages=True

            await ctx.guild.default_role.edit(permissions=everyone_perms, reason=f"Server Lockdown revoked by {ctx.author}")
        
        # Handling Forbidden Permissions Exception
        except discord.Forbidden as e:
            await ctx.send("I don't have the required permissions to do this.")
            return

        # Handling HTTPException
        except discord.HTTPException as e:
            await ctx.send("HTTPException Occurred.")
            raise e

        # Send Confirmation
        await ctx.send(":unlock: Server Unlocked.")

        # Context Time
        ctx_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M GMT+5")

        # Log Embed
        embed = discord.Embed(
                colour=0xC3C3C3,
                title="Server Lockdown Revoked",
                description=f"Server Lockdown revoked by {ctx.author.name}#{ctx.author.discriminator} {ctx.author.mention}"
            )
        embed.set_footer(text=f"Invoke Time: {ctx_time}")

        # Send Logs
        log_channel = self.bot.get_channel(882126651411021881)
        await log_channel.send(embed=embed)

    # Command to Verify College GCs -- Verifiers Exclusive
    @commands.command(aliases=["verified"], help="Gives the specified `member` access to the specified `college`-gc text channel. \n\u3164\n`member` --> Discord Member Object. Can be a member ping or a member id. \n`college` --> Can be any college from alpha, cedar and nixor. This is a string and is case insensitive. \n\u3164\n**Note:** Only the ones with the `Verifiers` role will be able to use this command. \n\u3164\n**Aliases:**\n`verified`")
    @commands.has_role("Verifiers")
    async def verify(self, ctx, member: discord.Member, college:str):
        # If Member Not Found
        if member == None:
            await ctx.send("Member not found.")

        # The Respective College Role
        college_role = discord.utils.get(ctx.guild.roles, name=college.capitalize())
        # The Respective College Channel
        college_channel = discord.utils.get(ctx.guild.channels, name=f"{college.lower()}-gc")

        # If College Role Found
        if college_role != None:
            # If College Channel Found
            if college_channel != None:
                
                # Add the Role
                await member.add_roles(college_role)
                # Confirmation Message
                await ctx.send(f":white_check_mark: **{member.name}** has been successfully given the **{college.capitalize()}** role.")
                # Ping in chat
                await college_channel.send(f"<a:ShinyArrow:847834101180137543> {member.mention} just joined the gc! Welcome him here!")
            
            # Channel not found
            else:
                # cedar gc
                if college.lower() == "cedar":
                    college_channel = discord.utils.get(ctx.guild.channels, name=f"unofficial-{college.lower()}-gc")
                    # Add the Role
                    await member.add_roles(college_role)
                    # Confirmation Message
                    await ctx.send(f":white_check_mark: **{member.name}** has been successfully given the **{college.capitalize()}** role.")
                    # Ping in chat
                    await college_channel.send(f"<a:ShinyArrow:847834101180137543> {member.mention} just joined the gc! Welcome him here!")
                else:
                    await ctx.send("Error: Unable to find the gc channel.")

        # Role not found.
        else:
            await ctx.send("Error: College Role not found.")

    # Error Handler
    @verify.error
    async def verify_eh(self, ctx, error):
        # Missing Args
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'member':
                await ctx.send("`member` param missing. Please provide a member ping or member id.")
            elif error.param.name:
                await ctx.send("`college` param missing. Please provide a college name. Can be any from alpha, cedar and nixor. This is case insensitive.")
        
        # Missing Roles
        if isinstance(error, commands.MissingRole):
            await ctx.send("You need `Verifier` role to use this command.") 

    # Add Roles
    @commands.command(aliases=["ar"], help="**Moderation Command** \nAdds the specified role to a given member. \nUse `c.add_role <member> <role> [*reason]`")
    @commands.has_permissions(administrator = True)
    async def add_role(self, ctx, member: discord.Member, role: discord.Role, *, reason=""):
        if role in member.roles:
            embed = discord.Embed(colour=0xF1F1F1, description=f"Cannot add role. {member.mention} already has the {role.mention} role.")
            await ctx.send(embed=embed)
            return

        try:
            await member.add_roles(role)
        
        except discord.Forbidden:
            await ctx.send("Can't add role to someone higher in the hierarchy.")

        except:
            await ctx.send("<:redtick:847843079938506812> **Error**. Make sure you put the parameters in order. \nUse `c.add_role <member> <role> [*reason]`")

        acknowledgement = f"{role.mention} role has been successfully added to {member.mention} by {ctx.author.name}."

        if reason == "":
            embed = discord.Embed(colour=0xF1F1F1, description=acknowledgement)

        else:
            embed = discord.Embed(colour=0xF1F1F1, description=f"{acknowledgement} \n\u3614\n**Reason:** {reason}")

    
        log_embed = discord.Embed(
            colour=0xF1F1F1,
            title="Role Added",
            description=f"{role.mention} role added to {member.mention} by {ctx.author.mention}."
        )
    
        log_embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
        log_embed.set_footer(text=f"ID: {member.id}")

        log_channel = self.bot.get_channel(882126651411021881)

        await ctx.send(content=":white_check_mark: Done.", embed=embed)
        await log_channel.send(embed=log_embed)

    # add_role error handler
    @add_role.error
    async def ar_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'member':
                await ctx.send("<:redtick:847843079938506812> You need to specify a member to add the roles to. \nUse `c.add_role <member> <role> [*reason]` to use the command correctly.")
            elif error.param.name == 'role':
                await ctx.send("<:redtick:847843079938506812> You need to specify a role to add to the member. \nUse `c.add_role <member> <role> [*reason]` to use the command correctly.")

        elif isinstance(error, commands.BadArgument):
            await ctx.send("<:redtick:847843079938506812> Something went wrong processing that. Check if you gave the parameters properly and in an appropriate way/order.")


    # Remove Roles
    @commands.command(aliases=["rr"], help="**Moderation Command** \nRemoves the specified role from a given member. \nUse `c.remove_role <member> <role> [*reason]`")
    @commands.has_permissions(administrator = True)
    async def remove_role(self, ctx, member: discord.Member, role: discord.Role, *, reason=""):
        if role not in member.roles:
            embed = discord.Embed(colour=0xF1F1F1, description=f"Cannot remove role. {member.mention} already doesn't has the {role.mention} role.")
            await ctx.send(embed=embed)
            return

        try:
            await member.remove_roles(role)
        
        except discord.Forbidden:
            await ctx.send("<:redtick:847843079938506812> Can't add role to someone higher in the hierarchy.")

        except:
            await ctx.send("<:redtick:847843079938506812> **Error**. Make sure you put the parameters in order. \nUse `c.add_role <member> <role> [*reason]`")

        acknowledgement = f"{role.mention} role has been successfully removed from {member.mention} by {ctx.author.name}."

        if reason == "":
            embed = discord.Embed(colour=0xF1F1F1, description=acknowledgement)

        else:
            embed = discord.Embed(colour=0xF1F1F1, description=f"{acknowledgement} \n\u3164\n**Reason:** {reason}")

        log_embed = discord.Embed(
            colour=0xF1F1F1,
            title="Role Removed",
            description=f"{role.mention} role removed from {member.mention} by {ctx.author.mention}."
        )

        
        log_embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
        log_embed.set_footer(text=f"ID: {member.id}")

        log_channel = self.bot.get_channel(882126651411021881)

        await ctx.send(content=":white_check_mark: Done.", embed=embed)
        await log_channel.send(embed=log_embed)

    # remove_role error handler
    @remove_role.error
    async def ar_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'member':
                await ctx.send("<:redtick:847843079938506812> You need to specify a member to remove the roles from. \nUse `c.remove_role <member> <role> [*reason]` to use the command correctly.")
            elif error.param.name == 'role':
                await ctx.send("<:redtick:847843079938506812> You need to specify a role to remove from the member. \nUse `c.remove_role <member> <role> [*reason]` to use the command correctly.")
        
        elif isinstance(error, commands.BadArgument):
            await ctx.send("<:redtick:847843079938506812> Something went wrong processing that. Check if you gave the parameters properly and in an appropriate way/order.")

    # Add Role Filters
    @commands.command(aliases=["filter"], help="**Moderation Command** \nAdds/Removes filter roles from members.\nUse `c.filter add/remove [filter_name] [member]`\n**Filter Names:** \n```'serious' ---> Filter the member out of serious channel. \n'reaction' ---> Filter the member out for adding reactions in general channels. \n'vc' ---> Filter the member out of VCs.\n'attachment' ---> Filter the member from sending attachments in general channels.\n``` \n*(Note: You must use the above mentioned keywords to add appropriate filters to the member.)*")
    @commands.has_any_role("Server Admin", "Discord Mods", "Trial Mods")
    async def toggle_filter(self, ctx, prompt:str, filter_name:str, member: discord.Member):
        filters_dict = {"serious":882126649687175204, "reaction":882126649687175203, "vc":882126649687175202, "attachment":882126649687175201}
        filter_name = filter_name.lower()
        
        # add filter
        if prompt == "add":
            # check for filter
            if filter_name in filters_dict.keys():
                filter_role = ctx.guild.get_role(filters_dict[filter_name])
                # check if filter role exists
                if filter_role == None:
                    await ctx.send('Error404: Filter not found.')
                # check if filter already exists
                if filter_role not in member.roles:
                    await member.add_roles(filter_role)
                    await ctx.send(":white_check_mark: Filter Added.")
                    embed_title = f"Filter Added | {filter_name.capitalize()}"
                    embed_description = f"{filter_name.capitalize()} filter was added to {member.mention}. \n**Responsible Moderator:** {ctx.author.name}#{ctx.author.discriminator}"
                else:
                    await ctx.send(f"The member already has the {filter_name} filter enabled.")
                    return  	
            else:
                await ctx.send("Error404: Filter not found.")
                return 

        # remove filter
        elif prompt == "remove":
            # check for filter
            if filter_name in filters_dict.keys():
                filter_role = ctx.guild.get_role(filters_dict[filter_name])
                # check if filter role exists
                if filter_role == None:
                    await ctx.send('Error404: Filter not found.')
                    return
                # check if filter already exists
                if filter_role in member.roles:
                    await member.remove_roles(filter_role)
                    await ctx.send(":white_check_mark: Filter Removed.")
                    embed_title = f"Filter Removed | {filter_name.capitalize()}"
                    embed_description = f"{filter_name.capitalize()} filter was removed from {member.mention}. \n**Responsible Moderator:** {ctx.author.name}#{ctx.author.discriminator}"

                else:
                    await ctx.send(f"The member already has the {filter_name} filter disabled.")
                    return  	
            else:
                await ctx.send("Error404: Filter not found.")
                return
        else:
            await ctx.send("Wrong action described. Make sure you use the command in the following format: \n`c.filter add/remove [filter_name] [member]`")
            return

        # logging
        log_embed = discord.Embed(colour = 0xF1F1F1, title = embed_title, description = embed_description)
        log_channel = self.bot.get_channel(882126651411021881)

        await log_channel.send(embed=log_embed)
    
    # Error Handler
    @toggle_filter.error
    async def toggle_filter_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'prompt':
                await ctx.send("Please provide an action `(add/remove)`. \nMake sure you use the command in the following format: \n`c.filter add/remove [filter_name] [member]`")
            elif error.param.name == "filter_name":
                await ctx.send("Please provide a filter name. Can be either `serious`,`vc`, `reaction` or `attachment`.")
            elif error.param.name == 'member':
                await ctx.send("Kindly provide a member to add filter to. Can be an id or the member ping. \nMake sure you use the command in the following format: \n`c.filter add/remove [filter_name] [member]`")

# Setup Function
def setup(bot):
    bot.add_cog(Moderation(bot))
