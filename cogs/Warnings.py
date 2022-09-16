import discord
import json
import pyrebase 
import datetime
import asyncio
from discord.ext import commands
from discord.utils import get

with open("json/FirebaseCreds.json", "r") as FirebaseCreds:
	config = json.load(FirebaseCreds)
	firebase = pyrebase.initialize_app(config)
db = firebase.database()

class Warnings(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	
	async def cog_command_error(self, ctx, error):
		if hasattr(ctx.command, 'on_error'):
			return

		error = getattr(error, 'original', error)

		if isinstance(error, commands.MissingPermissions):
			await ctx.send("<:redtick:847843079938506812> You don't have the required permissions to use this command.")
		elif isinstance(error, commands.MissingRequiredArgument):
			if error.param.name == 'member':
				await ctx.send("`member` parameter missing. Please specify a member to use command. ")
		elif isinstance(error, commands.MemberNotFound):
			await ctx.send("<:redtick:847843079938506812> Please provide a valid member id or member object.")

		else:
			raise error

	@commands.command(name="warn", help="**Moderation Command** \nWarns a naughty member. \nUse `c.warn <member> <reason>` \n \u3164 \n **Note:** Specifying reason is compulsory. And that after every 3 warns, the member is auto-muted for 8 hours.")
	@commands.has_any_role("Server Admin", "Discord Mods", "Trial Mods")
	async def warn(self, ctx, member:discord.Member, *, reason=""):
		if reason == "":
			await ctx.send("<:redtick:847843079938506812> You can't warn a member without a reason. \nKindly provide a reason to warn.")
			return

		if member.id == ctx.author.id:
			await ctx.send("I'm warning you, don't warn yourself!")
			return

		if member.id == ctx.me.id:
			await ctx.send("Don't warn the bot.")
			return

		if ctx.guild.roles.index(member.roles[-1]) >= ctx.guild.roles.index(ctx.author.roles[-1]):
			await ctx.send("Can't warn someone higher or equal to in role hierarchy.")
			return

		member_id = f"{member.id}"
		members = db.child("Warns").get().val()

		ctx_time = datetime.datetime.now().strftime("%d-%m-%Y")

		entry_value = f"{ctx.author.name}#{ctx.author.discriminator}${ctx_time}${reason}$warn"

		if members == None or member_id not in members.keys():
			data = [entry_value]
			db.child("Warns").child(member_id).set(data)

		else:
			data = members[member_id]
			data.append(entry_value)
			db.child("Warns").update({member_id:data})

		count_suffixes = {"1":"1st", "2":"2nd", "3":"3rd"}
		warn_count = str(len(data))

		if warn_count in count_suffixes.keys():
			warn_count = count_suffixes[warn_count]
		else:
			warn_count += 'th'

		await ctx.send(f"**{member.name}#{member.discriminator}** has been warned. This is their {warn_count} warning.")

		embed = discord.Embed(
			colour=0xF1F1F1,
			title="warn | Member Warned",
			description=f"**Warn Number:** {len(data)}\n**Offender:** {member.name}#{member.discriminator} {member.mention} \n**Reason:** {reason}\n**Responsible Moderator:** {ctx.author.name}#{ctx.author.discriminator}"
		)
		embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)		
		embed.set_footer(text=f"ID: {member.id}")


		try:
			log_channel = self.bot.get_channel(882126651411021881) # 882126651411021881

			await log_channel.send(embed=embed)
			await member.send(f"You were warned in COALI Discord. Reason: {reason}")
		except:
			pass

		if len(data) != 0 and len(data)%3 == 0:
			muted = discord.utils.get(ctx.guild.roles, name="Muted")
			await member.add_roles(muted)
			await ctx.send(f"**Auto-mod action:** {member.mention} muted for **8h**. Warns reached auto-mod limits.")

			
			embed = discord.Embed(
				colour=0xF1F1F1,
				title="auto-mute | Member Muted",
				description=f"{member.mention} has been muted for **8h** \n**Reason:** Auto-mod action. Warns reached auto-mod limits. \n**Muted By:** {ctx.author.mention}"
			)
			embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
			embed.set_footer(text=f"ID: {member.id}") 
			await log_channel.send(embed=embed)

			await asyncio.sleep(28800)

			try:
				# Add Log here too.
				await member.remove_roles(muted)
				
				embed = discord.Embed(
				colour=0xF1F1F1,
				title="auto-unmute | Member Unmuted",
				description=f"{member.mention} has been unmuted. \nAuto-mute period over."
				)
				embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
				embed.set_footer(text=f"ID: {member.id}")

				await log_channel.send(embed=embed)

			except:
				pass


	@commands.command(aliases=["warns", "warnings", "modlog"], help="**Moderation Command** \nLists the amount of warnings a member has. \nUse `c.warnings [member]` to use command.")
	@commands.has_any_role("Server Admin", "Discord Mods", "Trial Mods")
	async def modlogs(self, ctx, member:discord.Member):
		member_id = f"{member.id}"
		members = db.child("Warns").get().val()

		if members == None or member_id not in members.keys():
			await ctx.send("No warnings found for this member.")

		else:
			warnings = members[member_id]
			if len(warnings) == 1:
				embed = discord.Embed(colour=0xF1F1F1,title=f"{len(warnings)} modlog found")
			else:
				embed = discord.Embed(colour=0xF1F1F1,title=f"{len(warnings)} modlogs found")			

			for element in list(enumerate(members[member_id], start = 1)):
				n, key = element
				responsible_moderator, ctx_time, reason, mode = key.split('$')

				embed.add_field(name=f"#{n} | {mode} | {ctx_time}", value=f"Responsible Moderator: {responsible_moderator} \nReason: {reason}")
				
			embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)			
			await ctx.send(embed=embed)

	@commands.command(aliases=["wr", "modlogremove"], help="**Moderation Command** \nUse to remove a specific warning from a member's set of warnings. \nUse `c.warnremove|wr <member> <warn_number>` to use command. \n\u3164\n**Note:** `warn_number` is the warning number for the member, which can be obtained by using the `c.warns` command. Use `c.help warns` to know more.")
	@commands.has_any_role("Server Admin", "Discord Mods", "Trial Mods")
	async def warnremove(self, ctx, member:discord.Member, warn_number):
		if ctx.guild.roles.index(member.roles[-1]) >= ctx.guild.roles.index(ctx.author.roles[-1]):
			await ctx.send("Can't remove warn for someone higher or equal to in role hierarchy.")
			return
		
		member_id = f"{member.id}"
		members = db.child("Warns").get().val()

		try:
			warn_number = int(warn_number)
		except:
			await ctx.send("<:redtick:847843079938506812> Warning Number should be an integer.")
			return

		if members == None or member_id not in members.keys():
			await ctx.send("Member not found.")
			return


		else:
			try:
				warnings = members[member_id]
				warnings.pop(warn_number-1)
			except IndexError:
				await ctx.send("No warning found at the given position.")
				return

			db.child("Warns").update({member_id:warnings})

			await ctx.send(f"Warning at position {warn_number} successfully removed for **{member.name}#{member.discriminator}**.")

	@commands.command(aliases=["modlogreset"], help="**Moderation Command** \nResets the warnings a member has. \nUse `c.warnreset [member]`")
	@commands.has_any_role("Server Admin", "Discord Mods", "Trial Mods")
	async def warnreset(self, ctx, member:discord.Member):
		if ctx.guild.roles.index(member.roles[-1]) >= ctx.guild.roles.index(ctx.author.roles[-1]):
			await ctx.send("Can't reset warns for someone higher or equal to in role hierarchy.")
			return

		member_id = f"{member.id}"
		members = db.child("Warns").get().val()

		if members == None or member_id not in members.keys():
			await ctx.send("Member not found.")

		else:	
			db.child("Warns").child(f"{member.id}").remove()
			await ctx.send(f"Warnings for **{member.name}#{member.discriminator}** successfuly reset.")

def setup(bot):
	bot.add_cog(Warnings(bot))

