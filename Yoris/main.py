import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YorisDB.YorisDB.settings')
django.setup()


import asyncio
from aiogram import types
from core.bot import bot, dp
from core.scheduler import start_scheduler
from factories import dispatcher

factory_dispatcher = dispatcher.Dispatcher()


@dp.message()
async def universal_handler(message: types.Message):
    await factory_dispatcher.dispatch(message, bot)


async def main():
    start_scheduler()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
