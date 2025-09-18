import argparse
import json
import shlex
import asyncio
import decouple
from aiogram.types import BufferedInputFile
from numpy.testing.print_coercion_tables import print_coercion_table

from utils import graphics, stats
import contexts
import database_manager
import parse_message
from factories.commands.base import CommandBase
from django.core.cache import cache
from django_redis.cache import RedisCache
from typing import cast

cache = cast(RedisCache, cache)
CACHE_TIMEOUT = decouple.config("CACHE_TIMEOUT", cast=int, default=3600)


class CubeCommand(CommandBase):
    def __init__(self):
        self.user = None
        self.chat = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text
        if not text.startswith('cubes'):
            return False
        args = text[len("cubes"):].strip()
        parser = argparse.ArgumentParser(prog="cubes", add_help=False)
        parser.add_argument("-user")
        try:
            _ = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        extracted_user = await parse_message.extract_user(ctx)
        self.user = await database_manager.get_user(extracted_user)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True

    async def execute(self, ctx: contexts.MessageContext):
        key = f"cubes:{self.chat.id}:{ctx.from_user.id}"
        value = json.loads(cache.get(key) or "{}")
        if value:
            value = {int(key): value for key, value in value.items()}
        if self.user.id in value:
            if value[self.user.id] == "pending":
                await ctx.reply(f"You already invited {self.user.name} to play cubes")
                return
            if value[self.user.id] == "playing":
                await ctx.reply(f"You are already playing with {self.user.name}")
                return
        value[self.user.id] = {
            "status": "pending"
        }
        cache.set(key, json.dumps(value), timeout=CACHE_TIMEOUT)
        await ctx.reply(f"{self.user.name}, {ctx.from_user.full_name()} invited you to play cubes")


class WhoCubesCommand(CommandBase):
    def __init__(self):
        self.user = None
        self.chat = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text
        if not text.startswith('who-cubes'):
            return False
        extracted_user = await parse_message.extract_user(ctx)
        self.user = await database_manager.get_user(extracted_user)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True

    async def execute(self, ctx: contexts.MessageContext):
        text = f"{ctx.from_user.full_name()} asks if anyone wants to play cubes. Write <code>cubes -user @{ctx.from_user.id}</code> to play with them"

        invited_users = get_invited_users(self.chat.id, ctx.from_user.id)
        if invited_users:
            text += "\n\n"
            users = await database_manager.get_users(map(int, invited_users))
            for user in users:
                text += f"You have request from {user.name} to play cubes\nCommand to play: <code>cubes-yes -user @{user.id}</code>\n"
        await ctx.reply(text, parse_mode="HTML")


class CubesYesCommand(CommandBase):
    def __init__(self):
        self.author = None
        self.user = None
        self.chat = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text
        if not text.startswith('cubes-yes'):
            return False
        args = text[len("cubes-yes"):].strip()
        parser = argparse.ArgumentParser(prog="cubes-yes", add_help=False)
        parser.add_argument("-user")
        try:
            _ = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        extracted_user = await parse_message.extract_user(ctx)
        if not extracted_user:
            self.user = None
        else:
            self.user = await database_manager.get_user(extracted_user)
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True

    async def execute(self, ctx: contexts.MessageContext):
        second_player = self.author
        if self.user:
            key = f"cubes:{self.chat.id}:{self.user.id}"
            user_cache = json.loads(cache.get(key) or "{}")
            if str(self.author.id) not in user_cache:
                await ctx.reply(f"{self.user.name} didn't invite you to play cubes")
                return
            if user_cache[str(self.author.id)]["status"] == "playing":
                await ctx.reply(f"You are already playing cubes with {self.user.name}")
                return
            user_cache[str(self.author.id)]["status"] = "playing"
            cache.set(key, json.dumps(user_cache), timeout=CACHE_TIMEOUT)
            first_player = self.user
        else:
            invited_authors = get_invited_users(self.chat.id, self.author.id)
            if not invited_authors:
                await ctx.reply(f"Now one invited you to play cubes")
                return
            first_author_id = invited_authors[0]
            first_player = await database_manager.get_user(int(first_author_id))
            key = f"cubes:{self.chat.id}:{first_player.id}"
            user_cache = json.loads(cache.get(key) or "{}")
            if str(second_player.id) in user_cache:
                user_cache[str(second_player.id)]["status"] = "playing"
                cache.set(key, json.dumps(user_cache), timeout=CACHE_TIMEOUT)
        await play_cubes(first_player, second_player, ctx, self.chat)


class CubesNoCommand(CommandBase):
    def __init__(self):
        self.author = None
        self.user = None
        self.chat = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text
        if not text.startswith('cubes-no'):
            return False
        args = text[len("cubes-no"):].strip()
        parser = argparse.ArgumentParser(prog="cubes-no", add_help=False)
        parser.add_argument("-user")
        try:
            _ = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        extracted_user = await parse_message.extract_user(ctx)
        if not extracted_user:
            self.user = None
        else:
            self.user = await database_manager.get_user(extracted_user)
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True

    async def execute(self, ctx: contexts.MessageContext):
        if self.user:
            key = f"cubes:{self.chat.id}:{self.user.id}"
            user_cache = json.loads(cache.get(key, "{}"))
            if str(self.author.id) not in user_cache or user_cache[str(self.author.id)]["status"] != "pending":
                await ctx.reply(f"{self.user.name} didn't invite you to play cubes.")
                return
            del user_cache[str(self.author.id)]
            cache.set(key, json.dumps(user_cache), timeout=CACHE_TIMEOUT)

            await ctx.reply(f"You declined invitation to play cubes from {self.user.name}.")

        else:
            invited_authors = get_invited_users(self.chat.id, self.author.id)
            if not invited_authors:
                await ctx.reply("No one invited you to play cubes.")
                return
            first_author_id = invited_authors[0]
            first_player = await database_manager.get_user(int(first_author_id))
            key = f"cubes:{self.chat.id}:{first_player.id}"
            user_cache = json.loads(cache.get(key, "{}"))
            if str(self.author.id) in user_cache:
                del user_cache[str(self.author.id)]
                cache.set(key, json.dumps(user_cache), timeout=CACHE_TIMEOUT)

            await ctx.reply(f"You declined invitation from {first_player.name}.")


class CubesStatsCommand(CommandBase):
    def __init__(self):
        self.chat = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text
        if not text.startswith('cubes-stats'):
            return False
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True

    async def execute(self, ctx: contexts.MessageContext):
        buf = await graphics.get_cubes_stats(self.chat)
        photo = BufferedInputFile(buf.getvalue(), "image.png")
        text = await stats.get_cubes_stats(self.chat)
        await ctx.reply_photo(photo, text=text)


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
        result_text += f"{winner.name} wins!\n{await execute_trigger(loser)}"
    user_cache = json.loads(cache.get(f"cubes:{ctx.chat.id}:{first_player.id}", "{}"))
    del user_cache[str(second_player.id)]
    cache.set(json.dumps(user_cache), json.dumps(user_cache), timeout=CACHE_TIMEOUT)
    await ctx.answer(result_text)
    print("adding cubes stats")
    cubes_stats = await database_manager.add_cube_stats(
        chat=chat,
        player1=first_player,
        player2=second_player,
        winner=winner,
        loser=loser,
        is_draw=draw,
    )
    print(f"added cubes stats: {cubes_stats}")


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


async def execute_trigger(loser):
    return f"{loser.name} obtains nothing because triggers are not working lmao. TODO: realize cube trigger"


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
