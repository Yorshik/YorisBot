import asyncio

from background import mute_background, warn_background


async def start_scheduler():
    while True:
        await mute_background.mute_background()
        await warn_background.warn_background()
        await asyncio.sleep(60)
