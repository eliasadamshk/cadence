from __future__ import annotations

from pydantic import BaseModel


class Utterance(BaseModel):
    id: str
    text: str
    speaker: str  # "A", "B", etc.
    timestamp: float  # epoch ms
