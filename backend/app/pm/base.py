from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.models.board import Board, Card, CardStatus


class ProjectBoard(ABC):
    @abstractmethod
    async def get_board(self) -> Board: ...

    @abstractmethod
    async def find_cards(self, query: str) -> list[Card]: ...

    @abstractmethod
    async def move_card(self, card_id: str, to_status: CardStatus) -> Card: ...

    @abstractmethod
    async def create_card(self, title: str, assignee: str | None, status: CardStatus) -> Card: ...

    @abstractmethod
    async def update_card(self, card_id: str, **fields: Any) -> Card: ...

    @abstractmethod
    async def flag_blocker(self, card_id: str, summary: str) -> Card: ...
