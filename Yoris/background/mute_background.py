import datetime

from asgiref.sync import sync_to_async

from core.bot import bot
from YorisDB.database.models import Mute
from aiogram.types import ChatPermissions

async def unmute_user(mute: Mute):
    try:
        await bot.restrict_chat_member(
            mute.chat_id,
            mute.user_id,
            permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True
        ),
        )
        if mute.was_admin:
            await bot.promote_chat_member(
            mute.chat_id,
            mute.user_id,
                can_change_info=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_promote_members=True,
                can_manage_chat=True,
                can_manage_video_chats=True,
                custom_title=mute.tg_admin_title
            )
        await sync_to_async(mute.delete)()
    except Exception as e:
        print(e)


async def mute_background():
    now = datetime.datetime.now()
    expired_mutes = await sync_to_async(list)(Mute.objects.filter(until_date__lte=now))
    for mute in expired_mutes:
        await unmute_user(mute)
