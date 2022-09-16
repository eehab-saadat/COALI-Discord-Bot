# Import Statements
import discord
import typing
from discord.ext import commands, tasks
from discord.utils import get

# EmojiManipulation Cog
class EmojiManipulation(commands.Cog):

	# Client Instantiation
	def __init__(self,bot):
		self.bot = bot

	# Commands Grouping
	@commands.group(invoke_without_command=False)
	@commands.guild_only()
	@commands.has_any_role("Server Admin", "Discord Mods", "Trial Mods")
	async def emoji(self, ctx: commands.Context):
		'''
		Emoji Manipulation Commands.
		'''
		pass

	# Note --- Add auto-resizing via img library to lower file size than 256.0 kb
	# Emoji Steal
	@emoji.command(aliases=["create"],  help="Steals the emoji that you specify. \n\u3164\n**General Format:**\n`<prefix>emoji steal [target_emoji] [emoji_name]` \n\u3164\n**Paramater Info:** \n`target_emoji` --> The emoji you want to add to the server. Should be an emoji. If left empty, `emoji_name` param becomes compulsory and should be provided whereas a '.png', '.jpg' or '.gif' file to be made the new emoji should be attatched too.\n`emoji_name` --> The name that you want the new emoji to have. This param is optional. If left empty, emoji would be added with the default name. \n\u3164\n**Aliases:** `create`. ")
	async def steal(self, ctx, stolen_emoji: typing.Union[discord.PartialEmoji, discord.Emoji, str]=None, emoji_name: str=""):
		# Checking Data Type
		if type(stolen_emoji) == str:
			emoji_name = stolen_emoji

		# If Emoji is Provided
		if stolen_emoji is not None and  type(stolen_emoji) != str:
			# Reading Emoji Url
			stolen_emoji_url = stolen_emoji.url
			img = await stolen_emoji_url.read()

			# Setting Emoji Name
			if emoji_name == "":
				emoji_name = stolen_emoji.name

		# If No Emoji is Provided		
		else:
			# Checking Attachment Length
			if len(ctx.message.attachments) == 1:
				if ctx.message.attachments[0].filename[-4:] in [".jpg",".png",".gif"]:
					if ctx.message.attachments[0].size > 256000:
						await ctx.send("File cannot be larger than 256.0 kb.")
						return
					stolen_emoji_url = ctx.message.attachments[0].url
					img = await ctx.message.attachments[0].read()
				else:
					await ctx.send("Format not supported. File can only be in '.jpg', '.png' and '.gif' formats.")
					return

			elif len(ctx.message.attachments) > 1:
				await ctx.send("Please attatch only one file.")
				return

			else:
				await ctx.send("Provide an emoji or an emoji file please.")
				return

			# Checking if name provided.
			if emoji_name == "":
				await ctx.send("Please provide with a name for the emoji first.")
				return

		# Guild Emoji Lists
		guild_emoji_urls = list(map(lambda guild_emoji: guild_emoji.url, ctx.guild.emojis))
		guild_emoji_names = list(map(lambda guild_emoji: guild_emoji.name, ctx.guild.emojis))
		
		# Check if the emoji name already in guild emojis.
		if emoji_name in guild_emoji_names:
			await ctx.send(f"Emoji with the name \"{emoji_name}\" already exists in guild emojis.")
			return

		# Check if the emoji url exists in guild emojis.
		if stolen_emoji_url in guild_emoji_urls:
			await ctx.send("Emoji already exists in guild emojis.")
			return 

		# Uploading Emoji to Guild
		try:
			uploaded_emoji = await ctx.guild.create_custom_emoji(
				name=emoji_name, image=img, reason=f"Emoji stole done by {ctx.author.name}#{ctx.author.discriminator}."
			)

		# Handling Forbidden Permissions Exception
		except discord.Forbidden as e:
			await ctx.send("No permission to add emojis.")
			raise PermissionError("No permission to add emojis.") from e

		# Handling HTTPException
		except discord.HTTPException as e:
			await ctx.send("HTTPException Occurred.")
			raise e

		# Send Confirmation
		# Animated Emoji 
		if uploaded_emoji.animated is True:
			await ctx.send(f"<a:{uploaded_emoji.name}:{uploaded_emoji.id}> added successfully with name \"{uploaded_emoji.name}\".")
		# Non-Animated Emoji
		else:
			await ctx.send(f"<:{uploaded_emoji.name}:{uploaded_emoji.id}> added successfully with name \"{uploaded_emoji.name}\".")

	# Error Handling
	@steal.error
	async def steal_error_handler(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			if error.param.name == 'stolen_emoji':
				await ctx.send("Provide an emoji please.")
				return
		
		if isinstance(error, commands.BadUnionArgument):
			await ctx.send("Failed to convert the given emoji.")
			return

		raise error

	# Emoji Deleteion
	@emoji.command(aliases=["remove"],  help="Deletes the emoji that you specify. \n\u3164\n**General Format:**\n`<prefix>emoji delete [target_emoji]` \n\u3164\n**Paramater Info:** \n`target_emoji` --> The emoji you want to remove from the server. Should be an emoji that exists in the guild or the name of that emoji (case sensitive). \n\u3164\n**Aliases:** `remove`.")
	async def delete(self, ctx, target_emoji: typing.Union[discord.Emoji, str]):
		# If Emoji Name Given
		if type(target_emoji) == str:
			target_emoji = discord.utils.get(ctx.guild.emojis, name=f"{target_emoji}")

			if target_emoji == None:
				await ctx.send("Error404: Requested emoji not found.")
				return
		
		# If Emoji Object Given
		else:
			if target_emoji not in ctx.guild.emojis:
				await ctx.send("Error404: Requeted emoji not found.")
				return
		
		# Delete Emoji
		await target_emoji.delete(reason=f"Emoji deletion requested by {ctx.author.name}#{ctx.author.discriminator}.")

		# Send Confirmation
		await ctx.send(":white_check_mark: Emoji successfully deleted.")

	# Error Handling
	@delete.error
	async def delete_error_handler(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			if error.param.name == 'target_emoji':
				await ctx.send("Provide an emoji or the name of a valid emoji please.")
		
		if isinstance(error, commands.BadUnionArgument):
			await ctx.send("Failed to convert the given emoji.")

	# Emoji Info
	@emoji.command(aliases=["info", "detail"], help="Provides the essential info about a guild emoji that you requested. \n\u3164\n**General Format:**\n`<prefix>emoji info [target_emoji]` \n\u3164\n**Paramater Info:** \n`target_emoji` --> The emoji you want to fetch the info for. Should be an emoji that exists in the guild or the name of that emoji (case sensitive). \n\u3164\n**Aliases:** `detail`, `details`.")
	async def details(self, ctx, target_emoji: typing.Union[discord.Emoji, str]):
		# If Emoji Name Given
		if type(target_emoji) == str:
			target_emoji = discord.utils.get(ctx.guild.emojis, name=f"{target_emoji}")

			if target_emoji == None:
				await ctx.send("Error404: Requested emoji not found.")
				return
		
		# If Emoji Object Given
		else:
			if target_emoji not in ctx.guild.emojis:
				await ctx.send("Error404: Requeted emoji not found.")
				return
		
		# Some Extra Working
		target_emoji =  await ctx.guild.fetch_emoji(target_emoji.id)
		emoji_created_at = target_emoji.created_at.strftime("%d-%m-%Y")

		# Form Embed
		embed = discord.Embed(colour=0xF1F1F1)
		embed.set_author(name='Emoji Information', icon_url=ctx.me.avatar_url)
		embed.add_field(name="Emoji Name:", value=f"{target_emoji.name}", inline=False)
		embed.add_field(name="Emoji Id:", value=f"{target_emoji.id}", inline=False)
		embed.add_field(name="Animated Status:", value=f"{target_emoji.animated}", inline=False)
		embed.add_field(name="Emoji Created at:", value=f"{emoji_created_at}")
		embed.add_field(name="Emoji Created by:", value=f"{target_emoji.user.name}#{target_emoji.user.discriminator}", inline=False)
		embed.add_field(name="Emoji Url:", value=f"{target_emoji.url}")
		embed.set_footer(text=f"Requested by {ctx.author.name}#{ctx.author.discriminator}")
		embed.set_image(url=f'{target_emoji.url}')

		# Send Embed
		await ctx.send(embed=embed)

	# Error Handler
	@details.error
	async def details_error_handler(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			if error.param.name == 'target_emoji':
				await ctx.send("Provide an emoji or the name of a valid emoji please.")
		
		if isinstance(error, commands.BadUnionArgument):
			await ctx.send("Failed to convert the given emoji.")

# Setup Function
def setup(bot):
	bot.add_cog(EmojiManipulation(bot))