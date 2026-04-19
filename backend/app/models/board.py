from __future__ import annotations

from pydantic import BaseModel


class Card(BaseModel):
    id: str
    title: str
    assignee: str | None = None
    status: str  # TODO, IN_PROGRESS, IN_REVIEW, DONE


class Column(BaseModel):
    id: str
    name: str
    cards: list[Card] = []


class Board(BaseModel):
    columns: list[Column]

    def to_flat_cards(self) -> list[Card]:
        return [card for col in self.columns for card in col.cards]
