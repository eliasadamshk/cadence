from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.models.board import CardStatus


class ExtractedAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["MOVE_CARD", "CREATE_CARD", "UPDATE_CARD", "FLAG_BLOCKER"]
    card_id: str | None
    title: str | None
    assignee: str | None
    to_status: CardStatus | None
    summary: str
    source_text: str


class ExtractedActions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actions: list[ExtractedAction]
