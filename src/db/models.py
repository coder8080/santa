from datetime import datetime

from pydantic import BaseModel, Field, TypeAdapter


class Player(BaseModel):
    id: int = Field()
    created_at: datetime = Field()
    chat_id: int = Field()
    positive: str | None = Field()
    negative: str | None = Field()
    target: int | None = Field()
    name: str | None = Field()


player_adapter = TypeAdapter(Player)
player_list_adapter = TypeAdapter(list[Player])
