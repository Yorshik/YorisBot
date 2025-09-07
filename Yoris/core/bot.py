from aiogram import Bot, Dispatcher
import decouple

bot = Bot(token=decouple.config('YORIS_TOKEN', default='BOT_TOKEN'))
dp = Dispatcher()
