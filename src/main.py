import asyncio
import logging

from aiogram import Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.bot import bot

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello world")


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
