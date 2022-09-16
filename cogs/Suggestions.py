import discord
from discord.ext import commands


class Suggestions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases=["s"],description="Sends your suggestion to <#882126651025158165> for it to be considered. \nUse `c.suggest <suggestion>` or `c.s <suggestion>` to submit your suggestion. ")
	async def suggest(self, ctx, *, suggestion):

		suggestion_channel = self.bot.get_channel(882126651025158165)

		embed = discord.Embed(
		colour = discord.Colour(0xF1F1F1),
		title = f'Suggestion Recieved!',
		description = f"A suggestion was sent by {ctx.author.mention} (id: {ctx.author.id}) from <#{ctx.channel.id}> channel. \n\u3164\n"
		)

		embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
		embed.add_field(name="The Suggestion was:", value=f"```{suggestion}```\n\u3164")
		embed.set_footer(text=f"Upvote this message to support the suggestion. \nDownvote this message to reject the suggestion.")
		
		msg = await suggestion_channel.send(embed=embed)

		try:
			await msg.add_reaction("<:upvote:847843531724947478>")
			await msg.add_reaction("<:downvote:847843560258404372>")

		except:
			await ctx.send("Error adding reactions.")

		await ctx.send(f"{ctx.author.mention} suggestion successfully sent to <#882126651025158165>. :white_check_mark:")

def setup(bot):
	bot.add_cog(Suggestions(bot))