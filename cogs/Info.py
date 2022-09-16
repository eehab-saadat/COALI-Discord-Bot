# Discord Imports 
import discord
from discord.ext import commands

# Sytem Imports
import sys 
import psutil
from platform import system
from datetime import datetime
from collections import Counter

# Fucntion for Calculating Bot Uptime
def uptime(bot):
    # Calculating Bot Uptime
    delta_uptime = datetime.utcnow() - bot.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    # Adding Time Suffixes
    suffixed_times = [time for time in [f"{days} days", f"{hours} hours", f"{minutes} minutes", f"{seconds} seconds"] if time[0] != "0"]
    
    # Humanizing and Formatting Uptime Data
    uptime=""
    for i in range(len(suffixed_times)):
        if i == 0:
            uptime = f"{suffixed_times[i]}"
        elif i > 0 and i != (len(suffixed_times)-1):
            uptime += f", {suffixed_times[i]}"
        else:
            uptime += f" & {suffixed_times[i]}"
    
    # Returning Humaized Uptime Data
    return uptime

class Info(commands.Cog):
    # Cog Instantiation
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()

    # Bot About Command
    @commands.command()
    async def about(self, ctx):
        # Initializing the Embed
        embed = discord.Embed(colour=0xF1F1F1)
        embed.set_author(name=str(ctx.me), icon_url=ctx.me.avatar_url)
        embed.set_thumbnail(url=ctx.me.avatar_url)

        # Fetching the Developers' Member Object
        developers = ""
        for owner_id in self.bot.owner_ids:
            bot_owner = self.bot.get_user(owner_id)
            developers += f"! {bot_owner} ({bot_owner.id}) \n"
        
        # Adding the Developers Field
        embed.add_field(name="<:developer:854949366100000768> Developers", value=f"```{developers}```", inline=False)

        # Adding Uptime Field
        embed.add_field(name="<:online:854949586971787274> Uptime", value=f"```{uptime(self.bot)}```", inline=False)

        # Adding System Name
        embed.add_field(name="System",value=f"```{system()}```", inline=False)

        # Collecting all System Info
        sys_info = {
            # CPU Information
            "cpu_usage" : self.process.memory_full_info().uss / 1024 ** 2, # CPU Process Usage in MiB
            "cpu_usage_per" : self.process.cpu_percent() / psutil.cpu_count(), # CPU Usage Percentage
            "cpu_freq" : psutil.cpu_freq(percpu=False).current / 1000, # CPU Clock Speed in GHZ
            # RAM Information
            "used_ram" : (psutil.virtual_memory().total - psutil.virtual_memory().available) / 1024 ** 3, # Used RAM in GiB
            "total_ram" : psutil.virtual_memory().total / 1024 ** 3, # Total RAM in GiB
            "used_ram_per" :  psutil.virtual_memory().percent, # Total RAM Usage Percentage
            # Disk Information
            "used_disk" : psutil.disk_usage('/').used / 1024 ** 3, # Total Disk Usage in GiB
            "total_disk" : psutil.disk_usage('/').total / 1024 ** 3, # Toal Disk Usage in GiB
            "used_disk_per" : psutil.disk_usage('/').percent # Disk Usage Percentage
        }
        
        # Function for Displaying Boxes
        def boxes(percent):
            blue_boxes = int(percent // 20)
            white_boxes = 5 - blue_boxes
            return "🟦" * blue_boxes + "⬜" * white_boxes

        # Adding CPU Info Field
        embed.add_field(name="CPU Usage", value=f"```{sys_info['cpu_usage_per']:.2f} % \n{sys_info['cpu_freq']:.2f} GHz \n{boxes(sys_info['cpu_usage_per'])}```")
        # Adding RAM Info Field
        embed.add_field(name="RAM Usage", value=f"```{sys_info['used_ram_per']:.2f} % \n{sys_info['used_ram']:.2f}/{sys_info['total_ram']:.2f} GiB \n{boxes(sys_info['used_ram_per'])}```")
        # Adding Disk Info Field
        embed.add_field(name="Disk Usage", value=f"```{sys_info['used_disk_per']:.2f} % \n{sys_info['used_disk']:.2f}/{sys_info['total_disk']:.2f} GiB \n{boxes(sys_info['used_disk_per'])}```", inline=False)
        # Adding Python Version Field
        embed.add_field(name="<:python:854949939799916584> Python Version", value=f"```{sys.version.split()[0]}```")
        # Adding Discord Version Field
        embed.add_field(name="<:dpy:854580325769281537> Discord.py Version", value=f"```{discord.__version__}```")
        # Adding Bot's Latency Field
        embed.add_field(name="<:pulse:855113247057641493> Ping", value=f"```{round(self.bot.latency * 1000)} ms```", inline=False)
        # Adding Command Count Field
        embed.add_field(name="<:plus:854679080896823296> Command Count", value=f"```{len(self.bot.commands)} Commands```", inline=False)
        # Adding Bot Creation Date in Footer
        embed.set_footer(text='Created').timestamp = ctx.me.created_at

        # Sending the Embed
        await ctx.send(embed=embed)
    
    
    # Server Info Command
    @commands.command(aliases=["serverabout", "guildinfo"], help="Renders Information about the Server in Context.")
    async def serverinfo(self, ctx):
        # Declaring Variables
        guild = ctx.guild
        channel_info = []
        key_to_emoji = {
            discord.TextChannel: '<:text_channel:854579659973853194>',
            discord.VoiceChannel: '<:voice_channel:854579466864558090>',
        }
        
        # Initialising Embed with Title as Server Name
        embed = discord.Embed(
            title= guild.name,
            description=f"**ID:** {guild.id} \n**Owner:** {guild.owner}", 
            colour=0xF1F1F1
        )
        
        # Setting up the Embed Thumbnail as the Server Icon
        embed.set_thumbnail(url=guild.icon_url)

        # Features Field
        if guild.features:
            features = "\n".join([f"<:greenTick:854579817793978389>: {(feature.title()).replace('_',' ')}" for feature in guild.features])
            embed.add_field(name="Features", value=f"{features}", inline=False)

        # Fetching Everyone Perms
        everyone = guild.default_role
        everyone_perms = everyone.permissions.value
        
        # Declaring Channel Counters
        secret = Counter()
        totals = Counter()

        # Incrementing Secret Channels
        for channel in guild.channels:
            allow, deny = channel.overwrites_for(everyone).pair()
            perms = discord.Permissions((everyone_perms & ~deny.value) | allow.value)
            channel_type = type(channel)
            totals[channel_type] += 1
            if not perms.read_messages:
                secret[channel_type] += 1
            elif isinstance(channel, discord.VoiceChannel) and (not perms.connect or not perms.speak):
                secret[channel_type] += 1

        # Formatting Channel Information
        for key, total in totals.items():
            secrets = secret[key]
            try:
                emoji = key_to_emoji[key]
            except KeyError:
                continue

            if secrets:
                channel_info.append(f'{emoji} {total} (:lock: {secrets} locked)')
            else:
                channel_info.append(f'{emoji} {total}')

        # Adding the Channels Information
        embed.add_field(name='Channels', value='\n'.join(channel_info), inline=True)

        # Adding Boosting Information
        if guild.premium_tier != 0:
            boost_emoji = "<:serverboost:854649241652953129>"
            boosts = f'{boost_emoji} Level {guild.premium_tier}\n{boost_emoji} {guild.premium_subscription_count} boosts'
            last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
            if last_boost.premium_since is not None:
                boosts = f'{boosts} \n{boost_emoji} Boosters Count: {len(guild.premium_subscribers)} \n{boost_emoji} Last Boost: {last_boost} ({last_boost.premium_since.strftime("%d %b, %Y | %I:%M %p")})'
            embed.add_field(name='Boosts <:heartboost:854649239732355132>', value=boosts, inline=False)

        # Adding Members Information
        emotes = ["<:plus:854679080896823296>","<:human:854678611219316787>","<a:RobotFace:854678610715607060>"]
        bots = sum(member.bot for member in guild.members)
        humans = guild.member_count - bots
        formatted_count = f"{emotes[0]} Total: {guild.member_count} \n{emotes[1]} Humans: {humans} \n {emotes[2]} Bots: {bots} "
        embed.add_field(name='Members', value=formatted_count, inline=False)

        # Declaring Emoji Counters
        emoji_stats = Counter()

        # Counting Emojis
        for emoji in guild.emojis:
            # Counting Animated Emojis
            if emoji.animated:
                emoji_stats["animated"] += 1
                emoji_stats["animated_disabled"] += not emoji.available
            # Counting Static Emojis
            else:
                emoji_stats["regular"] += 1
                emoji_stats["disabled"] += not emoji.available

        # Formatting Information
        fmt = f"Regular: {emoji_stats['regular']}/{guild.emoji_limit}\n" \
              f"Animated: {emoji_stats['animated']}/{guild.emoji_limit}\n" \

        # Adding Disabled Emoji Info if Applicable
        if emoji_stats["disabled"] or emoji_stats["animated_disabled"]:
            fmt = f"{fmt}Disabled: {emoji_stats['disabled']} regular & {emoji_stats['animated_disabled']} animated\n"
        
        fmt = f'{fmt}Total Emojis: {len(guild.emojis)}/{guild.emoji_limit*2}'
        
        # Adding the Emoji Information Field
        embed.add_field(name='Emojis', value=fmt, inline=False)

        # Adding Guild Creation Date in Footer
        embed.set_footer(text='Created').timestamp = guild.created_at

        # Sending the Info Embed
        await ctx.send(embed=embed)

# Setting up the Cog.
def setup(bot):
	bot.add_cog(Info(bot))