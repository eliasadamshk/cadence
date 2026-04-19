from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ExtractedAction(BaseModel):
    kind: Literal["MOVE_CARD", "CREATE_CARD", "UPDATE_CARD", "FLAG_BLOCKER"]
    card_id: str | None = None
    title: str | None = None
    assignee: str | None = None
    to_status: str | None = None
    summary: str
    source_text: str
