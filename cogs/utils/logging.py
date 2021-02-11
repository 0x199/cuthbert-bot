import discord
from datetime import datetime

async def prepare_ban_log(author, user, reason):
    embed = discord.Embed(title="Member Banned")
    embed.color = discord.Color.blue()
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)
    embed.set_footer(text=f"{user.id}")
    embed.timestamp = datetime.now()
    return embed


async def prepare_unban_log(author, user, reason):
    embed = discord.Embed(title="Member Unbanned")
    embed.color = discord.Color.blurple()
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.id})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)
    embed.set_footer(text=f"{user.id}")
    embed.timestamp = datetime.now()
    return embed


async def prepare_kick_log(author, user, reason, date):
    embed = discord.Embed(title="Member Kicked")
    embed.color = discord.Color.green()
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text=f"{user.id}")
    embed.timestamp = datetime.now()
    return embed


async def prepare_mute_log(author, user, reason, punishment):
    embed = discord.Embed(title="Member Muted")
    embed.color = discord.Color.red()
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Duration", value=punishment, inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)
    embed.set_footer(text=f"{user.id}")
    embed.timestamp = datetime.now()
    return embed


async def prepare_unmute_log(author, user, reason):
    embed = discord.Embed(title="Member Unmuted")
    embed.color = discord.Color.green()
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)
    embed.set_footer(text=f"{user.id}")
    embed.timestamp = datetime.now()
    return embed
