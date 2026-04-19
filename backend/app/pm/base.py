from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.models.board import Board, Card


class ProjectBoard(ABC):
    @abstractmethod
    async def get_board(self) -> Board: ...

    @abstractmethod
    async def find_cards(self, query: str) -> list[Card]: ...

    @abstractmethod
    async def move_card(self, card_id: str, to_status: str) -> Card: ...

    @abstractmethod
    async def create_card(self, title: str, assignee: str | None, status: str) -> Card: ...

    @abstractmethod
    async def update_card(self, card_id: str, **fields: Any) -> Card: ...
