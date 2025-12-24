import asyncio

from supabase import create_async_client

from src.env import get_str_env

url = get_str_env("SUPABASE_URL")
key = get_str_env("SUPABASE_KEY")

client = asyncio.run(create_async_client(url, key))
