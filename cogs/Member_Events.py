import discord
from discord.ext import commands
from random import choice

class Member_Events(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		welcome_channel = self.bot.get_channel(882126650106585095)
		embed = discord.Embed(
			colour=0xF1F1F1,
			description=f"**Greetings {member.mention}!**\n \u3164 \nTo gain access to the server properly, follow these instructions:\n:one: In <#882126650601537589>, you select your Academic Level.\n:two: You select your subjects from <#882126650601537590> by reacting to emojis specified to unlock subject channels. \n:three: In <#882126650601537591>, you choose optional roles according to your interests by reacting to appropriate emojis underneath messages. \n \u3164 \n<:COALI:847740917402304512> COALI Discord")
		
		responselst = [f'{member.mention} just joined the server - glhf!', f'{member.mention} just joined. Everyone look busy!', f'{member.mention} just joined. Can I get a heal?', f'{member.mention} joined your party.', f'{member.mention} joined. You must construct additional pylons.', f'Ermagherd. {member.mention} is here.', f'Welcome {member.mention}. Stay awhile and listen.', f'Welcome {member.mention}. We were expecting you ( ͡° ͜ʖ ͡°)', f'Welcome {member.mention}. We hope you brought pizza.', f'Welcome {member.mention}. Leave your weapons by the door.', f'A wild {member.mention} appeared.', f'Swoooosh. {member.mention} just landed.', f'Brace yourselves. {member.mention} just joined the server.', f'{member.mention} just joined... or did they?', f'{member.mention} just arrived. Seems OP - please nerf.', f'{member.mention} just slid into the server.', f'A {member.mention} has spawned in the server.', f'Big {member.mention} showed up!', f'Where’s {member.mention}? In the server!', f'{member.mention} hopped into the server. Kangaroo!!', f'{member.mention} just showed up. Hold my beer.', f'Challenger approaching - {member.mention} has appeared!', f"It's a bird! It's a plane! Nevermind, it's just {member.mention}.", f"It's {member.mention}! Praise the sun! \\\\[T]/", f'Never gonna give {member.mention} up. Never gonna let {member.mention} down.', f'{member.mention} has joined the battle bus.', f"Cheers, love! {member.mention}'s here!", f'Hey! Listen! {member.mention} has joined!', f"We've been expecting you {member.mention}", f"It's dangerous to go alone, take {member.mention}!", f"{member.mention} has joined the server! It's super effective!", f'{member.mention} is here, as the prophecy foretold.', f"{member.mention} has arrived. Party's over.", f'Ready player {member.mention}', f'{member.mention} is here to kick butt and chew bubblegum. And {member.mention} is all out of gum.', f"Hello. Is it {member.mention} you're looking for?", f'{member.mention} has joined. Stay a while and listen!', f'Roses are red, violets are blue, {member.mention} joined this server with you.']

		
		await welcome_channel.send(f"<a:ShinyArrow:847834101180137543> **{choice(responselst)}**",embed=embed)

		# Initial Message
		
		await member.send(f":wave: Hey {member.name}! \n\u3164\nWelcome to <:COALI:847740917402304512> **COALI Discord**, the official Discord Server for the largest Cambridge International Group on Facebook. \nWe are primarily focused on  __**O-Levels, A-Levels and IGCSE**__ for <:Cambridge:757126846977671209> **Cambridge Assessment International Education**; however other exam boards are also welcome! \n\u3164\n**-----------------------------** \nA few important channels in the server include but are not limited to the following: \n\u3164\n<#882209099721359391> \nIf you're a newbie to discord, you're **recommended** to read and view this channel as it helps as a server walkthrough and a guide to discord as a whole! \n\u3164\n<#882126650601537589> \nEmoji react time! You react to emojis, you get the particular \"role\". \nSelect your **academic level** in this channel to advance into the server (you gain access to the rest of the main channels). \nNext, choose your **optional interests and subjects** respectively in <#882126650601537591> and <#882126650601537590> when you gain access to them to unlock specific channels. \n\u3164\n<#882126651411021883> \nIntroduce yourself and have a nice chat with the wonderful student community we have here! \n**-----------------------------** \n\u3164\n<:COALI:847740917402304512> **COALI** \n \u3164 \n:globe_with_meridians: **Website:** \n<https://COALI.org> \n<:fblogo:846121379358048267> **Facebook Group:** \n<https://coali.org/s/oalevel> \n<:discord:846121909782577173> **Discord Server:**\n<https://coali.org/s/discord> \n \u3164 \nHope you have a great time here! :slight_smile:")

		member_log_channel = self.bot.get_channel(882126651411021880) 

		embed = discord.Embed(title="Member joined",
                        description=f"""
{member.mention}
Member no. **{member_log_channel.guild.member_count:,d}**
Created at {member.created_at.strftime("%d/%m/%Y %H:%M:%S")} UTC
""",
                        colour=0xF1F1F1)
		embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
		embed.set_footer(text=f"ID: {member.id}") 

		await member_log_channel.send(embed=embed)


	@commands.Cog.listener()
	async def on_member_remove(self, member: discord.Member):

		member_log_channel = self.bot.get_channel(882126651411021880) # 695677276766994514

		roles = [role for role in member.roles if role != member_log_channel.guild.default_role]

		embed = discord.Embed(title="Member left",
                        description=f"""
{member.mention}
**Roles: {len(roles)}** """ + " ".join([role.mention for role in roles][::-1]) + f"""
Joined at {member.joined_at.strftime("%d/%m/%Y %H:%M:%S")} UTC
""",
                        colour=0xF1F1F1)
		embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
		embed.set_footer(text=f"ID: {member.id}") 

		await member_log_channel.send(embed=embed)

def setup(bot):
	bot.add_cog(Member_Events(bot))
