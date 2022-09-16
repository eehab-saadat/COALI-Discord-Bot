# System Imports
import os
import json
import sys

# Discord Imports
import discord
from discord.ext import commands
from discord.utils import get

# System Imports
from datetime import datetime
# Defining Intents
intents = discord.Intents.default()
intents.members = True

# Bot Instantiation
bot = commands.Bot(command_prefix = commands.when_mentioned_or("c.",".","?"), intents=intents, owner_ids={369653880101011456})
# bot = commands.Bot(command_prefix = commands.when_mentioned_or("//"), intents=intents, owner_ids={369653880101011456})

# Instantiating Bot Launch Time
bot.launch_time = datetime.utcnow()

# Loading Discord Bot Token
with open("json/BotToken.json", "r") as BotToken:
    Variables = json.load(BotToken)
    TOKEN = Variables["DISCORD_TOKEN"]

# Cog Loader
for cog in os.listdir("./cogs"):
    if cog.endswith(".py"):
        bot.load_extension(f"cogs.{cog[:-3]}")

bot.load_extension('jishaku')

# on_ready event
@bot.event
async def on_ready():
    # Declaring COALI Discord as Guild.
    Guild = bot.get_guild(882126649687175199)

    # Printing Out Connection Prompts
    print("Connection successfully established.")
    print(f"{str(bot.user)} has been successfully connected to {Guild.name} (id: {Guild.id}).\n")

    # Printing out System Version Info
    print(f"System Python Version: {sys.version}")
    print(f"Discord.py Running Version: {discord.__version__}\n")

# Function for Updating Bot Presence. 
async def update_presence():
    # Wait till bot ready.
    await bot.wait_until_ready()

    # Declaring COALI Discord as Guild. 
    Guild = bot.get_guild(882126649687175199)

    # Counting Guild Members
    MemberCount = len(Guild.members)

    # Changing Bot Presence and Activity
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(f"in COALI Discord with {MemberCount} students!"))

# Creating a Loop Task
bot.loop.create_task(update_presence())

# Running the Bot Client.
bot.run(TOKEN)