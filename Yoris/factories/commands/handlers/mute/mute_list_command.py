from factories.commands.base import BaseCommand
import datetime
from utils import database_manager
import contexts
from utils.i18n import translate as _

class MuteListCommand(BaseCommand):
    async def execute(self, ctx: contexts.MessageContext):
        chat = await database_manager.get_chat(ctx.chat.id)
        mutes = await database_manager.get_mutes(chat)
        if not mutes:
            await ctx.reply(_("No one is muted", ctx=ctx))
            return
        text = _("Mutes of this chat:\n\n", ctx=ctx)
        for mute in mutes:
            text += _(
                "{name} is muted\n"
                "Expires in {minutes} minutes\n"
                "Muted by {author}\n"
                "{reason_part}",
                ctx=ctx,
                name=mute.user.name,
                minutes=int((mute.until_date - datetime.datetime.now()).total_seconds() / 60),
                author=mute.author.name,
                reason_part=f"Reason: {mute.reason}" if mute.reason else "",
            )
            text += f"\n"
        await ctx.reply(text)


class TerminalFriendlyMuteListCommand(MuteListCommand):
    factory_type = "command"
    prefix = ["mute-list", "mutes", "муты", "мутлист"]

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        return bool(self.prefix_used(ctx))
