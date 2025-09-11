import datetime

from asgiref.sync import sync_to_async
from core.bot import bot
from YorisDB.database.models import Warn


async def remove_warn(warn):
    await bot.send_message(warn.chat_id, f"warn for {warn.user.name} has been removed")
    sync_to_async(Warn.delete)(warn)


async def warn_background():
    now = datetime.datetime.now()
    expired_warns = await sync_to_async(list)(Warn.objects.filter(until_date__lte=now))
    for warn in expired_warns:
        await remove_warn(warn)