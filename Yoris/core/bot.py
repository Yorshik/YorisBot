from aiogram import Bot, Dispatcher
import decouple
from aiogram.client.default import DefaultBotProperties


bot = Bot(token=decouple.config('YORIS_TOKEN', default='BOT_TOKEN'), default=DefaultBotProperties(link_preview_is_disabled=True))
dp = Dispatcher()
