# Discord Imports 
import discord
from discord.ext import commands

# Custom Help Command Class
class COALI_Help(commands.HelpCommand):
    # Error Handler
    async def on_help_command_error(self, ctx, error):
        raise error

    # Function to return command formate.
    def get_command_signature(self, command):
        """Returns command formate: <prefix> <*parent command> <command> <*args>"""
        
        # Variable Declaration
        ctx = self.context
        prefix = ctx.prefix

        # Formatted Return Prompts
        if not command.signature and not command.parent:
            return f"`{prefix}{command.name}`"
        if command.signature and not command.parent:
            return f"`{prefix}{command.name}` `{command.signature}`"
        if not command.signature and command.parent:
            return f"`{prefix}{command.parent}` `{command.name}`"
        else:
            return f"`{prefix}{command.parent}` `{command.name}` `{command.signature}`"

    # Function to return help for a command.
    def get_help(self, command, brief=True):
        """Function to return help for a command. Returns the "short_doc" if brief is True, else the longer help if False."""
        real_help = command.help or "This command is not documented."
        return real_help if not brief else command.short_doc or real_help

    # Main Help
    # <prefix>help
    async def send_bot_help(self, mapping):
        # Setting up Context
        ctx = self.context
        
        # Instantiating Embed.
        embed = discord.Embed(
            colour=0xF1F1F1,
            title="COALI Help",
            description=f"```diff\n- Type \"help [command]\" or \"help [cog]\" \n- for more information about a command or cog \n+ [] = optional argument \n+ <> = required argument```" \
                        f"```py\nBot_Prefix = [\"c.\",\".\",\"?\"]```" \
            )

        # Adding Fields
        for cog, commands in mapping.items():
            
            # Getting Cog's Name
            cog_name = getattr(cog, "qualified_name", "No Category")

            # Skipping Help Cog from being includined in the Help Embed.
            if cog_name == "Help":
                continue

            # Adding Command Names to the Field.
            command_names = [f"`{command.name}`" for command in commands]
            if command_names:
                embed.add_field(name=f"__{cog_name} ({len(commands)} Commands)__", value= "> " + " ".join(command_names), inline=False)

        # Setting up the Embed Footer.
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        # Sending the Help Embed.
        await ctx.send(embed=embed)

    # Command Help
    # <prefix>help <command>
    async def send_command_help(self, command):
        # Setting up context
        ctx = self.context

        # Instantiating Embed
        embed = discord.Embed(
            colour=0xF1F1F1, 
            title=f"{self.get_command_signature(command)}" 
            )

        # Adding the Command Help.
        embed.add_field(name="Description", value=f"{self.get_help(command, brief=False)}", inline=False)
        
        # Adding Aliases to Help, if exists.
        if aliases := command.aliases:
            embed.add_field(name="Aliases", value=f'{" | ".join(f"`{x}`" for x in aliases)}', inline=False)

        # If it's a Group Command, mentioning its Sub-Commands in Help.
        # if isinstance(command, commands.Group):
        #     subcommand = command.commands
        #     value = "\n".join(self.get_command_signature(c) for c in subcommand)
        #     embed.add_field(name="Subcommand(s)", value=value)

        # Setting up the Embed Footer.
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        # Sending the Command Help.
        await ctx.send(embed=embed)


    # <prefix>help <group>
    async def send_group_help(self, group):
        # Setting up context
        ctx = self.context

        # Instantiating Embed
        embed = discord.Embed(
            colour=0xF1F1F1, 
            title=f"{self.get_command_signature(group)}" 
            )

        # Adding the Command Help.
        embed.add_field(name="Description", value=f"{self.get_help(group, brief=False)}", inline=False)
        
        # Adding Aliases to Help, if exists.
        if aliases := group.aliases:
            embed.add_field(name="Aliases", value=f'{" | ".join(f"`{x}`" for x in aliases)}', inline=False)

        # Mentioning its Sub-Commands in Help.
        subcommand = group.commands
        value = "\n".join(self.get_command_signature(c) for c in subcommand)
        embed.add_field(name="Subcommand(s)", value=value)

        # Setting up the Embed Footer.
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        # Sending the Command Help.
        await ctx.send(embed=embed)


    async def send_cog_help(self, cog):
         # Setting up context
        ctx = self.context

        # Instantiating Embed
        embed = discord.Embed(
            colour=0xF1F1F1, 
            title=f"Category Help | {cog.qualified_name}", 
            description=f"{cog.description}"
            )

        # Setting up the Embed Footer.
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        # Sending the Command Help.
        await ctx.send(embed=embed)

class Help(commands.Cog):
    # Instantiating
    def __init__(self, bot):
        self.bot = bot

        # Storing Main Help Command in Variable
        self.bot._original_help_command = bot.help_command

        # Assigning New Help Command to the Bot Help Command
        bot.help_command = COALI_Help()
    
        # Setting this Cog as the Help Command Cog
        bot.help_command.cog = self

    # Event Triggers at Cog Unload
    def cog_unload(self):
        # Setting back Original Help Command if the Current Cog Unloads.
        self.bot.help_command = self.bot._original_help_command

# Setting this Cog Up
def setup(bot):
    bot.add_cog(Help(bot)) 

