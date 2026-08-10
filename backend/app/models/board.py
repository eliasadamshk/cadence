from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

CardStatus = Literal["TODO", "IN_PROGRESS", "IN_REVIEW", "DONE"]


class Card(BaseModel):
    id: str
    title: str
    assignee: str | None = None
    status: CardStatus
    blocker: str | None = None


class Column(BaseModel):
    id: CardStatus
    name: str
    cards: list[Card] = Field(default_factory=list)


class Board(BaseModel):
    columns: list[Column]

    def to_flat_cards(self) -> list[Card]:
        return [card for col in self.columns for card in col.cards]
