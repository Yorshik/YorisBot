from factories.commands.base import BaseCommand
import contexts
from utils import cubes, database_manager, parse_message
from utils.i18n import translate as _


class CubesWhoCommand(BaseCommand):
    def __init__(self):
        self.author = None
        self.chat = None

    async def execute(self, ctx: contexts.MessageContext):
        text = _("{name} asks if anyone wants to play cubes. Write <code>cubes -user @{id}</code> to play with them", ctx=ctx, name=self.author.name, id=self.author.id)

        invited_users = cubes.get_invited_users(self.chat.id, self.author.id)
        if invited_users:
            text += "\n\n"
            users = await database_manager.get_users(map(int, invited_users))
            for user in users:
                text += _("You have request from {name} to play cubes\nCommand to play: <code>cubes-yes -user @{id}</code>\n", user=user.name, id=user.id)
        await ctx.reply(text, parse_mode="HTML")


class TerminalCubesWhoCommand(CubesWhoCommand):
    factory_type = "command"
    prefix = ["who-cubes", "cubes-who"]

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        if not self.prefix_used(ctx):
            return False
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True
