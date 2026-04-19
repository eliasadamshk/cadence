from __future__ import annotations

import uuid
from typing import Any

from app.models.board import Board, Card, Column
from app.pm.base import ProjectBoard

STATUSES = ["TODO", "IN_PROGRESS", "IN_REVIEW", "DONE"]


class InMemoryBoard(ProjectBoard):
    def __init__(self) -> None:
        self._cards: dict[str, Card] = {}
        self._next_num = 1

    def _add(self, title: str, assignee: str | None, status: str) -> Card:
        card_id = f"CAD-{self._next_num}"
        self._next_num += 1
        card = Card(id=card_id, title=title, assignee=assignee, status=status)
        self._cards[card_id] = card
        return card

    async def get_board(self) -> Board:
        columns = []
        for status in STATUSES:
            cards = [c for c in self._cards.values() if c.status == status]
            columns.append(Column(id=status, name=status.replace("_", " ").title(), cards=cards))
        return Board(columns=columns)

    async def find_cards(self, query: str) -> list[Card]:
        q = query.lower()
        results = []
        for card in self._cards.values():
            if q in card.title.lower() or (card.assignee and q in card.assignee.lower()):
                results.append(card)
        return results

    async def move_card(self, card_id: str, to_status: str) -> Card:
        card = self._cards[card_id]
        updated = card.model_copy(update={"status": to_status})
        self._cards[card_id] = updated
        return updated

    async def create_card(self, title: str, assignee: str | None, status: str) -> Card:
        return self._add(title, assignee, status)

    async def update_card(self, card_id: str, **fields: Any) -> Card:
        card = self._cards[card_id]
        updated = card.model_copy(update=fields)
        self._cards[card_id] = updated
        return updated
