from datetime import datetime
from factories.commands.base import BaseCommand
from utils import database_manager, graphics, stats
from aiogram.types import BufferedInputFile
import contexts


class CubesStatsCommand(BaseCommand):
    def __init__(self):
        self.chat = None

    async def execute(self, ctx: contexts.MessageContext):
        buf = await graphics.get_cubes_stats(self.chat)
        photo = BufferedInputFile(buf.getvalue(), f"cubes_stats_{ctx.chat.id}_{datetime.now():%Y%m%d_%H%M%S}.png")
        text = await stats.get_cubes_stats(self.chat)
        await ctx.reply_photo(photo, text=text)


class TerminalCubesStatsCommand(CubesStatsCommand):
    factory_type = "command"
    prefix = "cubes-stats"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        if not self.prefix_used(ctx):
            return False
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True
