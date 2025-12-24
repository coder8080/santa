import asyncio
import logging
from random import shuffle

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from redis.asyncio.client import Redis

from env import get_int_env
from src.bot import bot
from src.db.actions import (
    create_player,
    get_all_players,
    get_player,
    set_name,
    set_negative,
    set_positive,
    set_target,
)

ADMIN_CHAT_ID = get_int_env("ADMIN_CHAT_ID")

router = Router()


class Form(StatesGroup):
    idle = State()
    name = State()
    positive = State()
    negative = State()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    assert message.text is not None
    parts = message.text.split()
    correct_code = len(parts) == 2 and parts[1] == "123"
    player = await get_player(message.chat.id)
    if not correct_code and player is None:
        await message.answer(
            "Извините, этот бот пока приватный. Вы можете написать админу: @coder8080"
        )
        return

    assert message.from_user
    if player is None:
        await create_player(message.chat.id)
    await state.set_state(Form.name)
    name = f"{message.from_user.first_name} {message.from_user.last_name}"
    builder = ReplyKeyboardBuilder()
    builder.button(text=name)
    markup = builder.as_markup(resize_keyboard=True)
    await message.answer("Привет. Напиши свое имя", reply_markup=markup)


@router.message(Form.name)
async def save_name(message: Message, state: FSMContext) -> None:
    assert message.text
    await set_name(message.chat.id, message.text)
    await state.set_state(Form.positive)
    await message.answer(
        "Напиши, что хочешь получить", reply_markup=ReplyKeyboardRemove()
    )


@router.message(Form.positive)
async def save_positive(message: Message, state: FSMContext) -> None:
    assert message.text
    await set_positive(message.chat.id, message.text)
    await state.set_state(Form.negative)
    await message.answer("Теперь напиши, что не стоит дарить")


@router.message(Form.negative)
async def save_negative(message: Message, state: FSMContext) -> None:
    assert message.text
    await set_negative(message.chat.id, message.text)
    await state.set_state(Form.idle)
    player = await get_player(message.chat.id)
    assert player
    await message.answer(
        f"Вот что сохранено:\n\nИмя: {player.name or '-'}\n"
        f"Дарить: {player.positive or '-'}\n"
        f"Не дарить: {player.negative or ''}\n\n"
        "Чтобы заполнить анкету заново, напиши /start\n"
        "Если все правильно, жди начала игры"
    )


@router.message(Command("check"), F.chat.id == ADMIN_CHAT_ID)
async def check(message: Message):
    all_players = await get_all_players()
    for player in all_players:
        if not player.name:
            await message.answer(
                f"Неизвестно имя пользователя {player.chat_id}"
            )
        if not player.positive:
            await message.answer(f"Неизвестно + {player.name}")
        if not player.negative:
            await message.answer(f"Неизвестно - {player.name}")
    await message.answer(f"Всего {len(all_players)}")


def check_arr(arr: list[int]):
    for i in range(len(arr)):
        if i == arr[i]:
            return False
    return True


@router.message(Command("play"), F.chat.id == ADMIN_CHAT_ID)
async def play(message: Message):
    all_players = await get_all_players()
    arr = list(range(len(all_players)))
    while not check_arr(arr):
        shuffle(arr)
    for i in range(len(arr)):
        await set_target(all_players[i].id, arr[i])
        target = all_players[arr[i]]
        await bot.send_message(
            all_players[i].chat_id,
            (
                f"Вы дарите порадок {target.name}.\n"
                f"Дарить: {target.positive}\n"
                f"Не дарить: {target.negative}"
            ),
        )
    await message.answer("Все сообщения отправлены")


async def main():
    logging.basicConfig(level=logging.INFO)
    storage = RedisStorage(redis=Redis(host="redis", port=6379))
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
