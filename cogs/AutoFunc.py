# System Imports
import re
import json

# Discord Imports
import discord
from discord.ext import commands

# Pyrebase Import
import pyrebase

# Firebase Instantiation
with open("json/FirebaseCreds.json", "r") as f:
    firebaseConfig = json.load(f)
    firebase =  pyrebase.initialize_app(firebaseConfig)      
db = firebase.database()
     
# Whitelist Channels from Logging
def whitelist_check(channel_id):
    # Whitelisting Admin and Log Channels from getting Logged
    if channel_id in [882126651025158167,882126651025158169,882126651411021879,882126651411021880, 882126651411021881]:
        return True
    return False

# Return Embed Fields
def return_fields(value_before, value_after):
    return [("Before:", value_before, False), ("+After:", value_after, False)]

# Cog for Auto-Functioning
class AutoFunc(commands.Cog):
    # Cog Instantiation
    def __init__(self, bot):
        # Bot Instantiation
        self.bot = bot

    # Setting Channels On Ready
    async def on_ready(self):
        
        # Message Log Channel
        self.message_log_channel = self.bot.get_channel(882126651411021879)
        
        # Member Log Channel
        self.member_log_channel = self.bot.get_channel(882126651411021880)

    # Defining Variables On Ready
    @commands.Cog.listener()
    async def on_ready(self):
        # Message Log Channel
        self.message_log_channel = self.bot.get_channel(882126651411021879)
        
        # Member Log Channel
        self.member_log_channel = self.bot.get_channel(882126651411021880)

        # Firebase Object
        self.firebase = pyrebase.initialize_app(firebaseConfig)
        
        # Firebase Database Object
        self.db = self.firebase.database()

    # Message Delete Log
    @commands.Cog.listener()
    async def on_message_delete(self, message):
       if whitelist_check(message.channel.id) is not True:
            # Setting up the basic embed.
            embed = discord.Embed(colour=0xF1F1F1)
            embed.set_author(name=f"{message.author.name}#{message.author.discriminator}", icon_url=message.author.avatar_url)
            embed.set_footer(text=f"ID: {message.author.id}")

            # If Plain Message.
            if message.content != "":
                embed.title = f"Message deleted in #{message.channel}"
                embed.description = f"{message.content}"

                # Send Log.
                if message.guild:
                    await self.message_log_channel.send(embed=embed)

            # If Attachments.
            if message.attachments:
                deleted_files = []

                # Looping through Attachments
                for attachment in message.attachments:
                    
                    # Converting Attachment to File
                    try:
                        deleted_img =  await attachment.to_file(use_cached=True)
                        deleted_files.append(deleted_img)

                    # Handling Forbidden Exception
                    except discord.Forbidden:
                        await self.message_log_channel.send("```Access Error while media logging.```")

                    # Handling HTTP Exception
                    except discord.HttpException:
                        await self.message_log_channel.send("```HTTP Exception occured while Logging Media.```")

                # Setting up the Embed
                embed.title = "Media Deleted"
                embed.description = f"the following media was deleted in {message.channel.mention} by {message.author.mention}"

                # Sending Logs
                if message.guild:
                    await self.message_log_channel.send(embed=embed) 
                    await self.message_log_channel.send(files=deleted_files)

    # Message Edit Log
    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        # Whitlisting out channels from logging
        if whitelist_check(message_before.channel.id) is not True:
            # Checking if message was edited.
            if message_before.content != message_after.content:
                # If message in guild
                if Guild := message_before.guild:
                    # Fetching Filtered Substrings List
                    firlteredsubstr = db.child("Filters").child("SubstringFilters").get().val()

                    # Fetching Filtered Strings/Word List
                    filteredstrings = db.child("Filters").child("StringFilters").get().val()

                    # Fecthing Guild Invites List
                    GuildInvites = await Guild.invites()
                    
                # Searching for Filtered Words in Message -- Fix
                if any(re.search(fr"(?i)({word})", message_after.content) for word in firlteredsubstr):
                    await message_after.delete()

                # Searching for Filtered Substrings in Messsage -- Fix
                if any(re.search(fr"(?i)\b({word})\b", message_after.content) for word in filteredstrings):
                    await message_after.delete()

                # Whitelisting Guild Invites 
                elif not any(invite.code in message_after.content for invite in GuildInvites):
                    
                    # Deleting non-guild invites
                    if re.search(r"(?i)\b(discord.gg/)\b", message_after.content):
                        await message_after.delete()

                    # Setting Up The Log Embed
                    embed = discord.Embed(
                        colour=0xF1F1F1,
                        title=f"Message edited in #{message_before.channel}" 
                    )
                    embed.set_author(name=f"{message_before.author.name}#{message_before.author.discriminator}", icon_url=message_before.author.avatar_url)
                    embed.set_footer(text=f"ID: {message_before.author.id}")

                    # Unpacking Fields Tuple and Adding Update Fields
                    for name, value, inline in return_fields(str(message_before.content), str(message_after.content)):
                        embed.add_field(name=name, value=value, inline=inline)

                    # Sending the Log Embed
                    await self.message_log_channel.send(embed=embed)

    # Dealing with on_message
    @commands.Cog.listener()
    async def on_message(self, message):

        # Press F to React F
        if message.content.lower() == "f":
            #F_emoji = "🇫"
            #await message.add_reaction(F_emoji)
            await message.add_reaction("\N{REGIONAL INDICATOR SYMBOL LETTER F}")

        # React with COALI Spin if COALI Bot is mentioned
        if self.bot.user.mentioned_in(message):
            await message.add_reaction("a:COALIspin:882989225245560962")

        # If message is in server
        if Guild := message.guild:

            # Filtered Substrings
            filteredsubstr = db.child("Filters").child("SubstringFilters").get().val()

            # Substrings Filter
            if any(re.search(fr"(?i)({word})", message.content) for word in filteredsubstr):
                await message.delete()

            # Filtered Strings/Words
            filteredstrings = db.child("Filters").child("StringFilters").get().val()

            # String Filter
            if any(re.search(fr"(?i)\b({word})\b", message.content) for word in filteredstrings):
                await message.delete()

            # Fecthing Guild Invites List
            GuildInvites = await Guild.invites()
            
            # Whitelisting Guild Invites
            if not any(invite.code in message.content for invite in GuildInvites):
                    
                    # Deleting non-guild invites
                    if re.search(r"(?i)\b(discord.gg/)\b", message.content):
                        await message.delete()

            # Fetching Emojis in the Message
            Emojis = re.findall(r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>", message.content)

            # Emoji Limiter per Message (To Prevent Spam)
            if len(Emojis) > 4 and (message.channel.id != 714627480459280484):
                await message.delete()
                await message.channel.send("Message deleted to prevent emoji spam.", delete_after=3.0)

    # Logging User Updates
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        
        # Setting up the Base Embed
        embed = discord.Embed(colour=0xF1F1F1)
        embed.set_author(name=f"{after.name}#{after.discriminator}", icon_url=after.avatar_url)
        embed.set_footer(text=f"ID: {after.id}")
        
        # If User Profile Name or Discriminator Change
        if any(((before.name != after.name),(before.discriminator != after.discriminator))):
            embed.title = "User Profile Updated"

            # Unpacking Fields Tuple and Adding Update Fields
            for name, value, inline in return_fields(str(before), str(after)):
                embed.add_field(name=name, value=value, inline=inline)
            
            # Send Log
            await self.member_log_channel.send(embed=embed)

        # If Avatar Change
        if before.avatar_url != after.avatar_url:
            
            # Setting up the log embed.
            embed.title = "Avatar Update"
            embed.description = f"{after.mention}"
            embed.set_thumbnail(url=after.avatar_url)

            # Sending the Log Embed
            await self.member_log_channel.send(embed=embed)

    # Logging Member Updates
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Setting up the Embed
        embed = discord.Embed(colour=0xF1F1F1)
        embed.set_author(name=str(after), icon_url=before.avatar_url)
        embed.set_footer(text=f"ID: {after.id}")
        
        # If Display Name Changes
        if before.display_name != after.display_name:

            # Unpacking Fields Tuple and Adding Update Fields
            for name, value, inline in return_fields(before.display_name, after.display_name):
                embed.add_field(name=name, value=value, inline=inline)

            # Sending the Log Embed
            await self.member_log_channel.send(embed=embed)

        # If Roles Update
        if before.roles != after.roles:
            
            # Getting Roles Difference
            updated_roles = " ".join([role.mention for role in after.roles if role not in  before.roles])
            removed_roles = " ".join([role.mention for role in before.roles if role not in after.roles])

            # If Roles Updated
            if updated_roles != "":
                embed.title = "Roles Updated"
                embed.add_field(name="Updated Role(s):", value=f"{updated_roles}", inline=False)

            # If Roles Removed
            else:
                embed.title = "Roles Removed"
                embed.add_field(name="Removed Role(s):", value=f"{removed_roles}", inline=False)

            # Sending the Log Embed
            await self.member_log_channel.send(embed=embed)            
                    
# Setting Up the Cog
def setup(bot):
    bot.add_cog(AutoFunc(bot))
