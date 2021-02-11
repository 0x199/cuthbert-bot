import logging
import os

import discord
from cogs.utils.tasks import Tasks
from discord.ext import commands
from dotenv import find_dotenv, load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = ['!']

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_extensions = [
                    'cogs.commands.modactions',
                    # 'cogs.commands.mod.modutils',
                    # 'cogs.commands.misc.admin',
                    # 'cogs.commands.misc.genius',
                    # 'cogs.commands.misc.misc',
                    # 'cogs.commands.misc.subnews',
                    # 'cogs.commands.misc.stonks',
                    # 'cogs.commands.misc.giveaway',
                    # 'cogs.commands.info.devices',
                    'cogs.commands.help',
                    # 'cogs.commands.info.stats',
                    # 'cogs.commands.info.tags',
                    # 'cogs.commands.info.userinfo',
                    # 'cogs.commands.mod.filter',
                    # 'cogs.monitors.birthday',
                    # 'cogs.monitors.boosteremojis',
                    'cogs.commands.logs',
                    # 'cogs.monitors.logging',
                    # 'cogs.monitors.reactionroles',
                    # 'cogs.monitors.xp',
]

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.presences = True
mentions = discord.AllowedMentions(everyone=False, users=True, roles=False)

bot = commands.Bot(command_prefix=get_prefix,
                   intents=intents, allowed_mentions=mentions)
bot.max_messages = 10000


async def send_error(ctx, error):
    embed = discord.Embed(title=":(\nYour command ran into a problem")
    embed.color = discord.Color.red()
    embed.description = discord.utils.escape_markdown(f'{error}')
    await ctx.send(embed=embed, delete_after=8)


# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    bot.tasks = Tasks(bot)
    bot.channel_public = int(os.environ.get("CHANNEL_PUBLIC_LOGS"))
    bot.channel_private = int(os.environ.get("CHANNEL_PRIVATE_LOGS"))
    bot.role_mod = int(os.environ.get("ROLE_MODERATOR"))
    bot.role_mute = int(os.environ.get("ROLE_MUTE"))
    bot.guild_id = int(os.environ.get("GUILD_ID"))
    bot.send_error = send_error
    bot.remove_command("help")
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    await bot.wait_until_ready()

    print(
        f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    print(f'Successfully logged in and booted...!')


bot.run(os.environ.get("CUTHBERT_TOKEN"), bot=True, reconnect=True)
