# Discord Imports 
import discord
from discord.ext import commands

# System Imports
import json
import time
import pyrebase

# Firebase Instantiation
with open("json/FirebaseCreds.json", "r") as f:
    firebaseConfig = json.load(f)

# Utilities
class Utilities(commands.Cog):
    '''
    Basic Command Utilities.
    '''
    # Instantiation
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Firebase Object
        self.firebase =  pyrebase.initialize_app(firebaseConfig)

        # Firebase Database Object
        self.db = self.firebase.database()

    # Ping Command
    @commands.command(help="Tells the bot's latency speed and heartbeat in miliseconds.")
    async def ping(self, ctx):
        # Bot's Latency
        ping = round(self.bot.latency * 1000)
        # Message Sent
        start = time.perf_counter()
        message = await ctx.send(f':ping_pong: Pong! {ping}ms')
        # Acknowledgement Recieved
        end = time.perf_counter()
        # Acknowledge Time / Heartbeat
        heartbeat = round((end - start) * 1000)
        # Send Final Info
        await message.edit(content=f':ping_pong: Ping: `{ping}ms` \n<a:heartbeat:855102705274191883> Heartbeat: `{heartbeat}ms`')

    # Testing Command
    # @commands.command(aliases=["testing", "t"], help="Replies back with 'Test Successful. Param Passed: {param} and Optional Param: {optional}'. Built purely for testing.")
    # async def test(self, ctx, param, *, optional=None):
    #     await ctx.send(f"Test Successful. Param Passed: {param} and Optional Param: {optional}")
        
    # Links Embed
    @commands.command(help="Displays Social Links.")
    async def links(self, ctx):
        embed = discord.Embed(
            colour=0xF1F1F1, 
            title="__COALI Links__",
            description="<:fblogo:846121379358048267> [__Main Group__](https://coali.org/s/oalevel) \n<:fblogo:846121379358048267> [__University Group__](https://coali.org/s/university) \n<:fblogo:846121379358048267> [__Shitposting Group__](https://coali.org/s/shitposting) \n:globe_with_meridians: [__Website__](https://coali.org/) \n<:discord:846121909782577173> [__Discord__](https://coali.org/s/discord) "
            )

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/846125403734540328.png")

        await ctx.send(embed=embed)

    # Show Filter
    @commands.command(aliases=["filteredwords", "wordfilters", "showwords"], help="Shows the list of filtered words. \nUse `?addword <word>` to add a filter and `?removeword` to remove, if you're an admin.")
    @commands.has_permissions(ban_members=True)
    async def wordfilter(self, ctx):

        # Filtered Substrings
        filteredsubstrings = "  **||**  ".join(self.db.child("Filters").child("SubstringFilters").get().val())
        
        # Filtered Strings/Words
        filteredstrings = "  **||**  ".join(self.db.child("Filters").child("StringFilters").get().val())

        print(filteredstrings)
        print(filteredsubstrings)
        print(self.db.child("Filters").child("SubstringFilters").get().val())
        print(self.db.child("Filters").child("StringFilters").get().val())
        
        # Setting up the Embed
        embed = discord.Embed(colour=0xF1F1F1, title="String/Substring Filters")
        embed.add_field(name="Filtered Substrings", value=filteredsubstrings, inline=False)
        embed.add_field(name="Filtered Strings", value=filteredstrings, inline=False)

        # Sending the Word Filter Embed in DMs
        await ctx.author.send(embed=embed, delete_after=30.0)
        await ctx.send(":white_check_mark: An Embed containing all the String/Substring Filters has been sent to your DMs.", delete_after=4.0)

    # Add Word Filter
    @commands.command(help="Adds the String/Substring to the Filters. \n\u3164\n`<mode>` --> Type of Filter. Can either be **sub** (substring) or **str** (string/word). \n`<word>` --> String/Substring to be added to filters.")
    @commands.has_permissions(administrator=True)
    async def addword(self, ctx, mode, *, word):
        
        # Pulling Filter Data and Assigning Variables
        Filters = self.db.child("Filters").get().val()
        StringFilters = Filters["StringFilters"]
        SubstringFilters = Filters["SubstringFilters"] 
        
        # String/Word Mode
        if mode.lower().startswith('str'):
            
            # If Word Already in filters
            if word in StringFilters:
                await ctx.send(f"The string/word \"{word}\" is already being filtered.")
            
            # If Not, then Updating the New Word into the Filters DB
            else:
                StringFilters.append(word)
                self.db.child("Filters").update({"StringFilters":StringFilters})
                await ctx.send(f":white_check_mark: Filter Update Successful. \n\"{word}\" String/Word is now being filtered.")
        
        # Substring Mode
        elif mode.lower().startswith('sub'):
            
            # If Substing already in Filters
            if word in SubstringFilters:
                await ctx.send(f"The substring \"{word}\" is already being filtered.")
            
            # If Not, then Updating the New Substring into the FIlters DB
            else:
                SubstringFilters.append(word)
                self.db.child("Filters").update({"SubstringFilters":SubstringFilters})
                await ctx.send(f":white_check_mark: Filter Update Successful. \n\"{word}\" Substring is now being filtered.")

        # If Wrong Mode Entered
        else:
            await ctx.send("Wrong Mode Entered. Enter `str` to filter strings and `sub` to filter substrings.", delete_after=3.0)

    # Pinning Messages
    @commands.command(aliases=["pinthis"], help="Pins the Message that was replied to or is provided as an ID. \nIf a message is replied with this command (without a message id) then the message is pinned. If a message id is provided then the message with that id will be pinned. \n\u3164\n**Note:** Message ID is given more priority than the replied Message if both are provided.")
    @commands.has_permissions(manage_messages=True)
    async def pin(self, ctx, pin_message: discord.Message = None):
        # Pin the Replied Message if there was no Message ID provided.
        if pin_message ==  None:
            pin_message = await ctx.fetch_message(ctx.message.reference.message_id)
            
            # If no reply provided.
            if pin_message == None:
                await ctx.send("No Message was replied to neither a Message ID was provided. Kindly provide the required parameters.", delete_after=4.0)
                return
                
        # Pin the Message
        await pin_message.pin(reason=f"Message pinned by {ctx.author}.")
	
# Setting up the Cog.
def setup(bot):
	bot.add_cog(Utilities(bot))
