import YorisDB.database.models as yoris_models
import aiogram
from aiogram.types import Message
from asgiref.sync import sync_to_async
import decouple
from django.core.cache import cache
from django.db.models import Q
from django.forms.models import model_to_dict

CACHE_TIMEOUT = decouple.config("CACHE_TIMEOUT", cast=int, default=3600)


@sync_to_async
def get_prefixes(chat_id):
    key = f"prefixes:{chat_id}"
    prefixes = cache.get(key)
    if prefixes is not None:
        return prefixes
    prefixes = list(
        yoris_models.Prefix.objects.filter(chat_id=chat_id).values_list(
            "name", flat=True
        )
    )
    cache.set(key, prefixes, CACHE_TIMEOUT)
    return prefixes


@sync_to_async
def add_prefix(chat_id, prefix):
    yoris_models.Prefix.objects.create(chat_id=chat_id, prefix=prefix)
    key = f"prefixes:{chat_id}"
    cache.delete(key)


@sync_to_async
def remove_prefix(chat_id, prefix):
    yoris_models.Prefix.objects.filter(chat_id=chat_id, prefix=prefix).delete()
    key = f"prefixes:{chat_id}"
    cache.delete(key)


@sync_to_async
def command_require_prefix(chat_id, command):
    return False


@sync_to_async
def update_chat(msg: Message):
    chat_id = msg.chat.id
    key = f"chat:{chat_id}"

    updated = {
        "id": chat_id,
        "name": msg.chat.title,
        "username": msg.chat.username,
        "type": msg.chat.type,
    }
    cached = cache.get(key)

    if not cached:
        chat_obj = yoris_models.Chat.objects.filter(id=chat_id).first()
        if chat_obj:
            cached = {
                "chat_id": chat_obj.id,
                "name": chat_obj.name,
                "username": chat_obj.username,
                "type": chat_obj.type,
            }
        else:
            chat_obj = yoris_models.Chat.objects.create(
                name=updated["name"],
                username=updated["username"],
                id=chat_id,
                type=updated["type"],
            )
            cached = model_to_dict(chat_obj)
    else:
        for field in ["name", "username", "type"]:
            if cached[field] != updated[field]:
                yoris_models.Chat.objects.filter(id=chat_id).update(**updated)
                cached.update(updated)
    cache.set(key, cached, CACHE_TIMEOUT)


@sync_to_async
def update_user(msg: Message):
    print("start update_user")
    user_id = msg.from_user.id
    key = f"user:{user_id}"

    updated = {
        "id": user_id,
        "first_name": msg.from_user.first_name,
        "last_name": msg.from_user.last_name,
        "username": msg.from_user.username,
    }
    cached = cache.get(key)

    if not cached:
        print("not cached")
        user_obj = yoris_models.User.objects.filter(id=user_id).first()
        if user_obj:
            print("found user")
            cached = {
                "user_id": user_obj.id,
                "first_name": user_obj.first_name,
                "last_name": user_obj.last_name,
                "username": user_obj.username,
            }
        else:
            print("user not found")
            user_obj = yoris_models.User.objects.create(
                first_name=updated["first_name"],
                last_name=updated["last_name"],
                username=updated["username"],
                id=user_id,
            )
            cached = model_to_dict(user_obj)
    else:
        print("cached")
        for field in ["first_name", "last_name", "username"]:
            if cached[field] != updated[field]:
                yoris_models.User.objects.filter(id=user_id).update(**updated)
                cached.update(updated)
    print("end update_user")
    cache.set(key, cached, CACHE_TIMEOUT)


@sync_to_async
def update_chat_member(msg: Message, chat_member):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    key = f"chat_member:{chat_id}:{user_id}"

    is_tg_admin = chat_member.status in ("administrator", "creator")
    tg_admin_title = None
    if is_tg_admin:
        tg_admin_title = getattr(chat_member, "custom_title", None) or "admin"
        if tg_admin_title and len(tg_admin_title) > 20:
            tg_admin_title = tg_admin_title[:20]
    updated = {
        "user": yoris_models.User.objects.filter(id=user_id).first(),
        "chat": yoris_models.Chat.objects.filter(id=chat_id).first(),
        "is_tg_admin": is_tg_admin,
        "tg_admin_title": tg_admin_title,
        "status": chat_member.status,
    }
    cached = cache.get(key)
    if not cached:
        cm_obj = yoris_models.ChatMember.objects.filter(
            user_id=user_id, chat_id=chat_id
        ).first()
        if cm_obj:
            cached = model_to_dict(cm_obj)
        else:
            cm_obj = yoris_models.ChatMember.objects.create(**updated)
            cached = model_to_dict(cm_obj)
    else:
        need_update = False
        for field in ["is_tg_admin", "tg_admin_title", "status"]:
            if cached.get(field) != updated[field]:
                need_update = True
                break
        if need_update:
            yoris_models.ChatMember.objects.filter(
                user_id=user_id, chat_id=chat_id
            ).update(
                is_tg_admin=updated["is_tg_admin"],
                tg_admin_title=updated["tg_admin_title"],
                status=updated["status"],
            )
            cached.update(
                {
                    "is_tg_admin": updated["is_tg_admin"],
                    "tg_admin_title": updated["tg_admin_title"],
                    "status": updated["status"],
                }
            )
    cache.set(key, cached, CACHE_TIMEOUT)


@sync_to_async
def add_stats(msg: Message):
    chat_member = yoris_models.ChatMember.objects.get(
        chat_id=msg.chat.id, user_id=msg.from_user.id
    )
    return yoris_models.Activity.objects.create(
        member=chat_member,
        chat=chat_member.chat,
        user=chat_member.user,
    )


@sync_to_async
def get_chat_member(username_id: str | int):
    q = Q()
    if isinstance(username_id, int) or (
        isinstance(username_id, str) and username_id.isdigit()
    ):
        q |= Q(user_id=int(username_id))
    q |= Q(user__username=username_id)
    return (
        yoris_models.ChatMember.objects.select_related(
            "user", "chat", "spouse", "clan", "main_club"
        )
        .filter(q)
        .first()
    )


@sync_to_async
def get_chat(username_id: str | int):
    q = Q()
    if isinstance(username_id, int) or (
        isinstance(username_id, str) and username_id.isdigit()
    ):
        q |= Q(id=username_id)
    q |= Q(username=username_id)
    return yoris_models.Chat.objects.filter(q).first()


@sync_to_async
def get_user(username_id: str | int):
    q = Q()
    if isinstance(username_id, int) or (
        isinstance(username_id, str) and username_id.isdigit()
    ):
        q |= Q(id=username_id)
    q |= Q(username=username_id)
    print(q)
    return yoris_models.User.objects.filter(q).first()


@sync_to_async
def set_mute_period(chat: yoris_models.Chat, period: int):
    chat.mute_period = period
    chat.save()


@sync_to_async
def get_mute_period(chat: yoris_models.Chat):
    return chat.mute_period


@sync_to_async
def get_warn_period(chat: yoris_models.Chat):
    return chat.warn_period


@sync_to_async
def create_mute(chat, user, author, until_date, reason, was_admin, tg_admin_title):
    yoris_models.Mute.objects.create(
        chat=chat,
        user=user,
        author=author,
        until_date=until_date,
        reason=reason,
        was_admin=was_admin,
        tg_admin_title=tg_admin_title,
    )


@sync_to_async
def create_warn(chat, author, user, until_date, reason):
    yoris_models.Warn.objects.create(
        chat=chat,
        author=author,
        user=user,
        until_date=until_date,
        reason=reason,
    )


@sync_to_async
def delete_mute(chat: yoris_models.Chat, user):
    yoris_models.Mute.objects.filter(chat=chat, user=user).delete()


@sync_to_async
def get_mute(chat: yoris_models.Chat, user):
    return yoris_models.Mute.objects.filter(chat=chat, user=user).first()


@sync_to_async
def get_mutes(chat: yoris_models.Chat):
    return list(
        yoris_models.Mute.objects.select_related("user", "author").filter(chat=chat)
    )


@sync_to_async
def get_user_warn_count(user: yoris_models.User):
    return yoris_models.Warn.objects.filter(user=user).count()


@sync_to_async
def text_trigger(chat: yoris_models.Chat, text: str, answer: str):
    yoris_models.TextTrigger.objects.create(chat=chat, text=text, answer=answer)
    print("Created a trigger")


@sync_to_async
def get_text_triggers(chat: yoris_models.Chat):
    return list(yoris_models.TextTrigger.objects.filter(chat=chat))


@sync_to_async
def check_trigger_id(chat: yoris_models.Chat, id: int):
    return yoris_models.TextTrigger.objects.filter(chat=chat, id=id) is not None
@sync_to_async
def check_trigger_bytext(chat: yoris_models.Chat, text: str):
    return yoris_models.TextTrigger.objects.filter(chat=chat, answer = text) is not None



@sync_to_async
def delete_trigger(chat: yoris_models.Chat, id: int | None, answer: str):
    if id is not None:
        yoris_models.TextTrigger.objects.filter(chat=chat, id=id).delete()
    elif not yoris_models.TextTrigger.objects.filter(chat=chat, answer=answer).exists():
        return
    yoris_models.TextTrigger.objects.filter(chat=chat, answer=answer).delete()
