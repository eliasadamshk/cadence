from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from app.models.actions import ExtractedAction


# --- Client → Server ---

class AudioDataMsg(BaseModel):
    type: Literal["audio_data"] = "audio_data"
    data: str  # base64-encoded PCM16


class SpeakerMapMsg(BaseModel):
    type: Literal["speaker_map"] = "speaker_map"
    map: dict[str, str]


class ControlMsg(BaseModel):
    type: Literal["start_recording", "stop_recording"]


# --- Server → Client ---

class TranscriptPartialMsg(BaseModel):
    type: Literal["transcript_partial"] = "transcript_partial"
    text: str
    speaker: str | None = None


class TranscriptFinalMsg(BaseModel):
    type: Literal["transcript_final"] = "transcript_final"
    id: str
    text: str
    speaker: str
    timestamp: float


class ActionExtractedMsg(BaseModel):
    type: Literal["action_extracted"] = "action_extracted"
    action: ExtractedAction


class BoardStateMsg(BaseModel):
    type: Literal["board_state"] = "board_state"
    board: dict[str, Any]


class ErrorMsg(BaseModel):
    type: Literal["error"] = "error"
    message: str
