from src.db.client import client
from src.db.models import Player, player_adapter


async def get_player(chat_id: int) -> Player | None:
    res = await client.table("player").select("*").eq("chat_id", chat_id).execute()
    if not res.data:
        return None
    player = player_adapter.validate_python(res.data[0])
    return player


async def create_player(chat_id: int) -> None:
    await client.table("player").insert({"chat_id": chat_id}).execute()


async def set_name(chat_id: int, name: str) -> None:
    await client.table("player").update({"name": name}).eq("chat_id", chat_id).execute()


async def set_positive(chat_id: int, positive: str) -> None:
    await (
        client.table("player")
        .update({"positive": positive})
        .eq("chat_id", chat_id)
        .execute()
    )


async def set_negative(chat_id: int, negative: str) -> None:
    await (
        client.table("player")
        .update({"negative": negative})
        .eq("chat_id", chat_id)
        .execute()
    )
