from aiogram import Bot

from src.env import get_str_env

bot = Bot(get_str_env("TOKEN"))
