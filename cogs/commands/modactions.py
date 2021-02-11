import datetime
import traceback
import typing

import cogs.utils.logging as logging
import discord
import humanize
import pytimeparse
from discord.ext import commands


class ModActions(commands.Cog):
    """This cog handles all the possible moderator actions.
    - Kick
    - Ban
    - Unban
    - Mute
    - Unmute
    - Purge
    """

    def __init__(self, bot):
        self.bot = bot

    async def check_permissions(self, ctx, user: typing.Union[discord.Member, int] = None):
        if ctx.guild.id != self.bot.guild_id:
            raise commands.BadArgument("This command cannot be used here.")

        if isinstance(user, discord.Member):
            if user.id == ctx.author.id:
                await ctx.message.add_reaction("🤔")
                raise commands.BadArgument("You can't call that on yourself.")
            if user.id == self.bot.user.id:
                await ctx.message.add_reaction("🤔")
                raise commands.BadArgument("You can't call that on me :(")

        # must be at least a mod
        mod_role = ctx.guild.get_role(self.bot.role_mod)
        if mod_role is None:
            raise commands.BadArgument("Moderator role not found.")
        if mod_role not in ctx.author.roles:
            raise commands.BadArgument(
                "You do not have permission to use this command.")
        if user:
            if isinstance(user, discord.Member):
                if user.top_role >= ctx.author.top_role:
                    raise commands.BadArgument(
                        message=f"{user.mention}'s top role is the same or higher than yours!")
            
    @commands.guild_only()
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.command(name="kick")
    async def kick(self, ctx: commands.Context, user: discord.Member, *, reason: str = "No reason.") -> None:
        """Kick a user (mod only)

        Example usage:
        --------------
        `!kick <@user/ID> <reason (optional)>`

        Parameters
        ----------
        user : discord.Member
            User to kick
        reason : str, optional
            Reason for kick, by default "No reason."

        """

        await self.check_permissions(ctx, user)

        reason = discord.utils.escape_markdown(reason)
        reason = discord.utils.escape_mentions(reason)

        log = await logging.prepare_kick_log(ctx.author, user, reason)

        try:
            await user.send(f"You were kicked from {ctx.guild.name}", embed=log)
        except Exception:
            pass

        await user.kick(reason=reason)

        await ctx.message.reply(embed=log, delete_after=10)
        await ctx.message.delete(delay=10)

        public_chan = ctx.guild.get_channel(
            self.bot.channel_public)
        if public_chan:
            log.remove_author()
            log.set_thumbnail(url=user.avatar_url)
            await public_chan.send(embed=log)

    @commands.guild_only()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.command(name="ban")
    async def ban(self, ctx: commands.Context, user: typing.Union[discord.Member, int], *, reason: str = "No reason."):
        """Ban a user (mod only)

        Example usage:
        --------------
        `!ban <@user/ID> <reason (optional)>`

        Parameters
        ----------
        user : typing.Union[discord.Member, int]
            The user to be banned, doesn't have to be part of the guild
        reason : str, optional
            Reason for ban, by default "No reason."

        """

        await self.check_permissions(ctx, user)

        reason = discord.utils.escape_markdown(reason)
        reason = discord.utils.escape_mentions(reason)

        # if the ID given is of a user who isn't in the guild, try to fetch the profile
        if isinstance(user, int):
            try:
                user = await self.bot.fetch_user(user)
            except discord.NotFound:
                raise commands.BadArgument(
                    f"Couldn't find user with ID {user}")

        log = await logging.prepare_ban_log(ctx.author, user, reason)

        try:
            await user.send(f"You were banned from {ctx.guild.name}", embed=log)
        except Exception:
            pass

        if isinstance(user, discord.Member):
            await user.ban(reason=reason)
        else:
            # hackban for user not currently in guild
            await ctx.guild.ban(discord.Object(id=user.id))

        await ctx.message.reply(embed=log, delete_after=10)
        await ctx.message.delete(delay=10)

        public_chan = ctx.guild.get_channel(
            self.bot.channel_public)
        if public_chan:
            log.remove_author()
            log.set_thumbnail(url=user.avatar_url)
            await public_chan.send(embed=log)

    @commands.guild_only()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.command(name="unban")
    async def unban(self, ctx: commands.Context, user: int, *, reason: str = "No reason.") -> None:
        """Unban a user (must use ID) (mod only)

        Example usage:
        --------------
        `!unban <user ID> <reason (optional)> `

        Parameters
        ----------
        user : int
            ID of the user to unban
        reason : str, optional
            Reason for unban, by default "No reason."

        """

        await self.check_permissions(ctx)

        reason = discord.utils.escape_markdown(reason)
        reason = discord.utils.escape_mentions(reason)

        try:
            user = await self.bot.fetch_user(user)
        except discord.NotFound:
            raise commands.BadArgument(f"Couldn't find user with ID {user}")

        try:
            await ctx.guild.unban(discord.Object(id=user.id), reason=reason)
        except discord.NotFound:
            raise commands.BadArgument(f"{user} is not banned.")

        log = await logging.prepare_unban_log(ctx.author, user, reason)
        await ctx.message.reply(embed=log, delete_after=10)
        await ctx.message.delete(delay=10)

        public_chan = ctx.guild.get_channel(
            self.bot.channel_public)
        if public_chan:
            log.remove_author()
            log.set_thumbnail(url=user.avatar_url)
            await public_chan.send(embed=log)

    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.command(name="purge")
    async def purge(self, ctx: commands.Context, limit: int = 0) -> None:
        """Purge messages from current channel (mod only)

        Example usage:
        --------------
        `!purge <number of messages>`

        Parameters
        ----------
        limit : int, optional
            Number of messages to purge, must be > 0, by default 0 for error handling

        """

        await self.check_permissions(ctx)

        if limit <= 0:
            raise commands.BadArgument(
                "Number of messages to purge must be greater than 0")
        if limit > 100:
            limit = 100

        msgs = await ctx.channel.history(limit=limit+1).flatten()

        await ctx.channel.purge(limit=limit+1)
        await ctx.send(f'Purged {len(msgs)} messages.', delete_after=10)

    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.command(name="purgeuser")
    async def purgeuser(self, ctx: commands.Context, user: discord.Member, limit: int = 0) -> None:
        """Purge a specific user's messages from current channel (mod only)

        Example usage:
        --------------
        `!purgeuser @user <number of messages>`

        Parameters
        ----------
        user : discord.Member        
            user to purge messages of
        limit : int, optional
            Number of messages to purge, must be > 0, by default 0 for error handling

        """

        await self.check_permissions(ctx, user)

        if limit <= 0:
            raise commands.BadArgument(
                "Number of messages to purge must be greater than 0")
        if limit > 100:
            limit = 100

        msgs = await user.history(limit=limit+1).flatten()
        await ctx.channel.delete_messages(messages=msgs)
        await ctx.message.delete()
        await ctx.send(f'Purged {len(msgs)} messages.', delete_after=10)

    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.command(name="mute")
    async def mute(self, ctx: commands.Context, user: discord.Member, dur: str = "", *, reason: str = "No reason.") -> None:
        """Mute a user (mod only)

        Example usage:
        --------------
        `!mute <@user/ID> <duration> <reason (optional)>`

        Parameters
        ----------
        user : discord.Member
            Member to mute
        dur : str
            Duration of mute (i.e 1h, 10m, 1d)
        reason : str, optional
            Reason for mute, by default "No reason."

        """
        await self.check_permissions(ctx, user)

        reason = discord.utils.escape_markdown(reason)
        reason = discord.utils.escape_mentions(reason)

        now = datetime.datetime.now()
        delta = pytimeparse.parse(dur)

        if delta is None:
            if reason == "No reason." and dur == "":
                reason = "No reason."
            elif reason == "No reason.":
                reason = dur
            else:
                reason = f"{dur} {reason}"

        mute_role = self.bot.role_mute
        mute_role = ctx.guild.get_role(mute_role)

        if mute_role in user.roles:
            raise commands.BadArgument("This user is already muted.")
        
        punishment = None
        # until = None
        if delta:
            try:
                time = now + datetime.timedelta(seconds=delta)
                # until = time
                punishment = humanize.naturaldelta(
                    time - now, minimum_unit="seconds")
                self.bot.tasks.schedule_unmute(user.id, time)
            except Exception:
                raise commands.BadArgument(
                    "An error occured, this user is probably already muted")
        else:
            punishment = "PERMANENT"

        await user.add_roles(mute_role)

        log = await logging.prepare_mute_log(ctx.author, user, reason, punishment)
        await ctx.message.reply(embed=log, delete_after=10)
        await ctx.message.delete(delay=10)

        log.remove_author()
        log.set_thumbnail(url=user.avatar_url)
        dmed = True
        try:
            await user.send(f"You have been muted in {ctx.guild.name}", embed=log)
        except Exception:
            dmed = False

        public_chan = ctx.guild.get_channel(
            self.bot.channel_public)
        if public_chan:
            await public_chan.send(user.mention if not dmed else "", embed=log)


    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.command(name="unmute")
    async def unmute(self, ctx: commands.Context, user: discord.Member, *, reason: str = "No reason.") -> None:
        """Unmute a user (mod only)

        Example usage:
        --------------
       ` !unmute <@user/ID> <reason (optional)>`

        Parameters
        ----------
        user : discord.Member
            Member to unmute
        reason : str, optional
            Reason for unmute, by default "No reason."

        """

        await self.check_permissions(ctx, user)

        mute_role = self.bot.role_mute
        mute_role = ctx.guild.get_role(mute_role)
        await user.remove_roles(mute_role)

        try:
            self.bot.tasks.cancel_unmute(user.id)
        except Exception:
            pass

        log = await logging.prepare_unmute_log(ctx.author, user, reason)

        await ctx.message.reply(embed=log, delete_after=10)
        await ctx.message.delete(delay=10)

        dmed = True
        try:
            await user.send(f"You have been unmuted in {ctx.guild.name}", embed=log)
        except Exception:
            dmed = False

        public_chan = ctx.guild.get_channel(
            self.bot.channel_public)
        if public_chan:
            log.remove_author()
            log.set_thumbnail(url=user.avatar_url)
            await public_chan.send(user.mention if not dmed else "", embed=log)

    @unmute.error
    @mute.error
    @unban.error
    @ban.error
    @purge.error
    @purgeuser.error
    @kick.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, error)
            traceback.print_exc()


def setup(bot):
    bot.add_cog(ModActions(bot))
