import discord
from discord.ext import commands
import json
import asyncio
import pyrebase

with open("json/FirebaseCreds.json", "r") as f:
    firebaseConfig = json.load(f)

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        self.firebase = pyrebase.initialize_app(firebaseConfig)
        self.db = self.firebase.database()

        #CONFIGURATION
        #Guild and starboard channel
        guild = self.bot.get_guild(882126649687175199) 
        self.starboard_channel = discord.utils.get(guild.channels, name="coaliboard")

        #Basic star emoji and reaction count
        self.coali_emoji = discord.utils.get(guild.emojis, name='COALI')
        self.coali_reactions = 3

        #Emoji change when reaction count is higher
        self.spinning_emoji = discord.utils.get(guild.emojis, name='COALIspin')
        self.coali_spin_reactions = 5 #SHOULD BE GREATER OR EQUAL TO MIN REACTIONS



    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        reaction = discord.utils.get(message.reactions, emoji=self.coali_emoji)

        if payload.emoji == self.coali_emoji:
            if reaction and payload.member.id != message.author.id:
                total_count = reaction.count

                if total_count >= self.coali_reactions and total_count < self.coali_spin_reactions:
                    messageids = self.db.child("Starboard").child("message-ids").get()
                    starredmessageids = self.db.child("Starboard").child("starredmessage-ids").get()

                    messageidlist = messageids.val()
                    starredmessageidlist = starredmessageids.val()

                    if not payload.message_id in messageidlist:

                        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

                        embed = discord.Embed(title="Starred Message", description = f"{message.content}" or "An embed.", colour=0xF1F1F1)
                        if len(message.attachments):
                            embed = discord.Embed(title="Starred Message", description = f"{message.content}\n{message.attachments[0].url}" , colour=0xF1F1F1)
                            embed.set_image(url=message.attachments[0].url)                        
                        embed.add_field(name="Source", value=f"[Jump!]({message.jump_url})", inline=False)
                        embed.set_author(name=f"{message.author.name}", icon_url=message.author.avatar_url)
                        embed.set_footer(text=f"{message.id}")

                        starredmessage = await self.starboard_channel.send(f"{self.coali_emoji} **{total_count}** <#{payload.channel_id}>", embed=embed)

                        messageidlist.append(payload.message_id)
                        starredmessageidlist.append(starredmessage.id)

                        self.db.child("Starboard").update({"message-ids": messageidlist})
                        self.db.child("Starboard").update({"starredmessage-ids": starredmessageidlist})

                        await asyncio.sleep(0.5)

                    else:

                        index = messageidlist.index(payload.message_id)
                        already_starredmessage_id = starredmessageidlist[index]

                        starredmessage = await self.bot.get_channel(self.starboard_channel.id).fetch_message(already_starredmessage_id)

                        embed = discord.Embed(title="Starred Message", description = f"{message.content}" or "An embed.", colour=0xF1F1F1)
                        if len(message.attachments):
                            embed = discord.Embed(title="Starred Message", description = f"{message.content}\n{message.attachments[0].url}" , colour=0xF1F1F1)
                            embed.set_image(url=message.attachments[0].url)                        
                        embed.add_field(name="Source", value=f"[Jump!]({message.jump_url})", inline=False)
                        embed.set_author(name=f"{message.author.name}", icon_url=message.author.avatar_url)
                        embed.set_footer(text=f"{message.id}")
                    

                        await starredmessage.edit(content=f"{self.coali_emoji} **{total_count}** <#{payload.channel_id}>")
                        await starredmessage.edit(embed=embed)

                elif total_count >= self.coali_spin_reactions:

                    messageids = self.db.child("Starboard").child("message-ids").get()
                    starredmessageids = self.db.child("Starboard").child("starredmessage-ids").get()

                    messageidlist = messageids.val()
                    starredmessageidlist = starredmessageids.val()

                    if not payload.message_id in messageidlist:

                        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

                        embed = discord.Embed(title="Starred Message", description = f"{message.content}" or "An embed.", colour=0xF1F1F1)
                        if len(message.attachments):
                            embed = discord.Embed(title="Starred Message", description = f"{message.content}\n{message.attachments[0].url}" , colour=0xF1F1F1)
                            embed.set_image(url=message.attachments[0].url)                        
                        embed.add_field(name="Source", value=f"[Jump!]({message.jump_url})", inline=False)
                        embed.set_author(name=f"{message.author.name}", icon_url=message.author.avatar_url)
                        embed.set_footer(text=f"{message.id}")

                        starredmessage = await self.starboard_channel.send(f"{self.spinning_emoji} **{total_count}** <#{payload.channel_id}>", embed=embed)

                        messageidlist.append(payload.message_id)
                        starredmessageidlist.append(starredmessage.id)

                        self.db.child("Starboard").update({"message-ids": messageidlist})
                        self.db.child("Starboard").update({"starredmessage-ids": starredmessageidlist})

                        await asyncio.sleep(0.5)

                    else:
                        index = messageidlist.index(payload.message_id)
                        already_starredmessage_id = starredmessageidlist[index]

                        starredmessage = await self.bot.get_channel(self.starboard_channel.id).fetch_message(already_starredmessage_id)

                        embed = discord.Embed(title="Starred Message", description = f"{message.content}" or "An embed.", colour=0xF1F1F1)
                        if len(message.attachments):
                            embed = discord.Embed(title="Starred Message", description = f"{message.content}\n{message.attachments[0].url}" , colour=0xF1F1F1)
                            embed.set_image(url=message.attachments[0].url)                        
                        embed.add_field(name="Source", value=f"[Jump!]({message.jump_url})", inline=False)
                        embed.set_author(name=f"{message.author.name}", icon_url=message.author.avatar_url)
                        embed.set_footer(text=f"{message.id}")

                        await starredmessage.edit(content=f"{self.spinning_emoji} **{total_count}** <#{payload.channel_id}>")
                        await starredmessage.edit(embed=embed)
                else:
                    pass
            else:
                await message.remove_reaction(payload.emoji, payload.member)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

        reaction = discord.utils.get(message.reactions, emoji=self.coali_emoji)

        if payload.emoji == self.coali_emoji:

            if reaction is not None:
                total_count = reaction.count

                if total_count < self.coali_reactions:
                    messageids = self.db.child("Starboard").child("message-ids").get()
                    starredmessageids = self.db.child("Starboard").child("starredmessage-ids").get()

                    messageidlist = messageids.val()
                    starredmessageidlist = starredmessageids.val()

                    if payload.message_id in messageidlist:

                        index = messageidlist.index(payload.message_id)
                        already_starredmessage_id = starredmessageidlist[index]

                        starredmessage = await self.bot.get_channel(self.starboard_channel.id).fetch_message(already_starredmessage_id)
                        
                        await starredmessage.delete()

                        del messageidlist[index]
                        del starredmessageidlist[index]

                        self.db.child("Starboard").update({"message-ids": messageidlist})
                        self.db.child("Starboard").update({"starredmessage-ids": starredmessageidlist})

                        await asyncio.sleep(0.5)

                elif total_count >= self.coali_reactions and total_count < self.coali_spin_reactions:
                    
                    messageids = self.db.child("Starboard").child("message-ids").get()
                    starredmessageids = self.db.child("Starboard").child("starredmessage-ids").get()

                    messageidlist = messageids.val()
                    starredmessageidlist = starredmessageids.val()

                    if payload.message_id in messageidlist:

                        index = messageidlist.index(payload.message_id)
                        already_starredmessage_id = starredmessageidlist[index]

                        starredmessage = await self.bot.get_channel(self.starboard_channel.id).fetch_message(already_starredmessage_id)

                        embed = discord.Embed(title="Starred Message", description = f"{message.content}" or "An embed.", colour=0xF1F1F1)
                        if len(message.attachments):
                            embed = discord.Embed(title="Starred Message", description = f"{message.content}\n{message.attachments[0].url}" , colour=0xF1F1F1)
                            embed.set_image(url=message.attachments[0].url)                        
                        embed.add_field(name="Source", value=f"[Jump!]({message.jump_url})", inline=False)
                        embed.set_author(name=f"{message.author.name}", icon_url=message.author.avatar_url)
                        embed.set_footer(text=f"{message.id}")

                        await starredmessage.edit(content=f"{self.coali_emoji} **{total_count}** <#{payload.channel_id}>")
                        await starredmessage.edit(embed=embed)

                elif total_count >= self.coali_spin_reactions:

                    messageids = self.db.child("Starboard").child("message-ids").get()
                    starredmessageids = self.db.child("Starboard").child("starredmessage-ids").get()

                    messageidlist = messageids.val()
                    starredmessageidlist = starredmessageids.val()

                    if payload.message_id in messageidlist:

                        index = messageidlist.index(payload.message_id)
                        already_starredmessage_id = starredmessageidlist[index]

                        starredmessage = await self.bot.get_channel(self.starboard_channel.id).fetch_message(already_starredmessage_id)

                        embed = discord.Embed(title="Starred Message", description = f"{message.content}" or "An embed.", colour=0xF1F1F1)
                        if len(message.attachments):
                            embed = discord.Embed(title="Starred Message", description = f"{message.content}\n{message.attachments[0].url}" , colour=0xF1F1F1)
                            embed.set_image(url=message.attachments[0].url)                        
                        embed.add_field(name="Source", value=f"[Jump!]({message.jump_url})", inline=False)
                        embed.set_author(name=f"{message.author.name}", icon_url=message.author.avatar_url)
                        embed.set_footer(text=f"{message.id}")

                        await starredmessage.edit(content=f"{self.spinning_emoji} **{total_count}** <#{payload.channel_id}>")
                        await starredmessage.edit(embed=embed)
            else:
                messageids = self.db.child("Starboard").child("message-ids").get()
                starredmessageids = self.db.child("Starboard").child("starredmessage-ids").get()

                messageidlist = messageids.val()
                starredmessageidlist = starredmessageids.val()

                if payload.message_id in messageidlist:

                    index = messageidlist.index(payload.message_id)
                    already_starredmessage_id = starredmessageidlist[index]

                    starredmessage = await self.bot.get_channel(self.starboard_channel.id).fetch_message(already_starredmessage_id)
                    
                    await starredmessage.delete()

                    del messageidlist[index]
                    del starredmessageidlist[index]

                    self.db.child("Starboard").update({"message-ids": messageidlist})
                    self.db.child("Starboard").update({"starredmessage-ids": starredmessageidlist})

                    await asyncio.sleep(0.5)

def setup(bot):
    bot.add_cog(Starboard(bot))