import asyncio

import contexts
from main import factory_dispatcher

from django_redis.cache import RedisCache
import decouple
import json

from utils import database_manager
from django.core.cache import cache
from typing import cast


cache = cast(RedisCache, cache)
CACHE_TIMEOUT = decouple.config("CACHE_TIMEOUT", cast=int, default=3600)


async def play_cubes(first_player, second_player, ctx, chat):
    await ctx.answer(f"{first_player.name} rolls the dice")
    first = await ctx.answer_dice()
    await asyncio.sleep(4)
    await ctx.answer(f"{second_player.name} rolls the dice")
    second = await ctx.answer_dice()
    await asyncio.sleep(4)
    winner = None
    loser = None
    result_text = f"{get_emoji(first.dice.value)} {first_player.name}\n{get_emoji(second.dice.value)} {second_player.name}\n\n"
    draw = False
    if first.dice.value > second.dice.value:
        winner = first_player
        loser = second_player
    elif second.dice.value > first.dice.value:
        winner = second_player
        loser = first_player
    elif first.dice.value == second.dice.value:
        result_text += f"draw. No one wins"
        draw = True
    if winner:
        result_text += f"{winner.name} wins!\n\n{await execute_trigger(ctx, loser)}"
    user_cache = json.loads(cache.get(f"cubes:{ctx.chat.id}:{first_player.id}", "{}"))
    del user_cache[str(second_player.id)]
    cache.set(json.dumps(user_cache), json.dumps(user_cache), timeout=CACHE_TIMEOUT)
    await ctx.answer(result_text)
    cubes_stats = await database_manager.add_cube_stats(
        chat=chat,
        player1=first_player,
        player2=second_player,
        winner=winner,
        loser=loser,
        is_draw=draw,
    )


def get_emoji(value):
    match value:
        case 1:
            return "1️⃣"
        case 2:
            return "2️⃣"
        case 3:
            return "3️⃣"
        case 4:
            return "4️⃣"
        case 5:
            return "5️⃣"
        case 6:
            return "6️⃣"


async def execute_trigger(ctx: contexts.MessageContext, loser):
    chat = await database_manager.get_chat(ctx.chat.id)
    trigger = await database_manager.get_trigger(chat=chat, type="cube")
    if not trigger or not trigger.is_enabled:
        return "Cube trigger is disabled or it does not exist"
    cube_reaction, ending = trigger.cube_reaction[:-2], trigger.cube_reaction[-2:]
    cube_reaction = cube_reaction.replace("@user", f"@{loser.id}")
    await ctx.answer(cube_reaction)
    if ending == ":1":
        the_bot = await ctx.bot.get_me()
        from_user = contexts.base_context.User(
            id=the_bot.id,
            username=the_bot.username,
            first_name=the_bot.first_name,
            last_name=the_bot.last_name,
            is_bot=True,
        )
        context = contexts.MessageContext(
            text=cube_reaction,
            from_user=from_user,
            chat=chat,
            type=ctx.type,
            bot=ctx.bot,
            is_via_bot=False,
        )
        await factory_dispatcher.command_factory.handle(context)
    return f"Reaction: {trigger.cube_reaction}\nDon't worry, it's only beta test of cube trigger"


def get_invited_users(chat_id, user_id):
    invites = []
    pattern = f"cubes:{chat_id}:*"
    keys = cache.keys(pattern)
    for key in keys:
        try:
            author_id = key.split(":")[-1]
            invited_users = json.loads(cache.get(key, '{}'))
            if str(user_id) in invited_users:
                if invited_users[str(user_id)]["status"] == "pending":
                    invites.append(author_id)
        except Exception as e:
            print(f"Error while getting invited users of {user_id}: {e}")
    return invites
