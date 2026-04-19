from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import WebSocket

from app.core.config import settings
from app.models.messages import (
    ActionExtractedMsg,
    BoardStateMsg,
    TranscriptFinalMsg,
    TranscriptPartialMsg,
)
from app.pm.base import ProjectBoard
from app.services.assemblyai import AssemblyAIRealtime
from app.services.llm import extract_actions
from app.services.transcript_buffer import TranscriptBuffer

log = logging.getLogger(__name__)


class MeetingSession:
    def __init__(self, ws: WebSocket, board: ProjectBoard):
        self._ws = ws
        self._board = board
        self._speaker_map: dict[str, str] = {}
        self._aai: AssemblyAIRealtime | None = None
        self._buffer: TranscriptBuffer | None = None

    async def start(self):
        board = await self._board.get_board()
        keyterms = []
        for card in board.to_flat_cards():
            keyterms.append(card.title)
            if card.assignee:
                keyterms.append(card.assignee)
        keyterms = list(dict.fromkeys(keyterms))

        self._aai = AssemblyAIRealtime(
            api_key=settings.assemblyai_api_key,
            on_partial=self._on_partial,
            on_final=self._on_final,
            keyterms=keyterms,
        )
        await self._aai.connect()

        self._buffer = TranscriptBuffer(on_flush=self._on_flush)
        self._buffer.start()

        await self._send(BoardStateMsg(board=board.model_dump()))

    async def stop(self):
        if self._buffer:
            self._buffer.stop()
        if self._aai:
            await self._aai.close()

    async def handle_audio(self, base64_audio: str):
        if self._aai:
            await self._aai.send_audio(base64_audio)

    def update_speaker_map(self, mapping: dict[str, str]):
        self._speaker_map = mapping

    async def _on_partial(self, text: str, speaker: str | None):
        await self._send(TranscriptPartialMsg(text=text, speaker=speaker))

    async def _on_final(self, uid: str, text: str, speaker: str, timestamp: float):
        display_speaker = self._speaker_map.get(speaker, speaker)
        await self._send(TranscriptFinalMsg(
            id=uid, text=text, speaker=speaker, timestamp=timestamp
        ))
        if self._buffer:
            await self._buffer.add(display_speaker, text, timestamp)

    async def _on_flush(self, segment: str, previous_context: str):
        board = await self._board.get_board()
        board_json = json.dumps(board.model_dump(), indent=2)

        try:
            actions = await extract_actions(
                transcript_segment=segment,
                previous_context=previous_context,
                board_state_json=board_json,
                speaker_map=self._speaker_map,
                api_key=settings.openrouter_api_key,
                model=settings.openrouter_model,
            )
        except Exception as e:
            log.error("LLM extraction failed: %s", e)
            return

        for action in actions:
            try:
                await self._apply_action(action)
                await self._send(ActionExtractedMsg(action=action))
            except Exception as e:
                log.error("Failed to apply action %s: %s", action.kind, e)

        if actions:
            updated_board = await self._board.get_board()
            await self._send(BoardStateMsg(board=updated_board.model_dump()))

    async def _apply_action(self, action: Any):
        if action.kind == "MOVE_CARD" and action.card_id and action.to_status:
            await self._board.move_card(action.card_id, action.to_status)
        elif action.kind == "CREATE_CARD" and action.title:
            await self._board.create_card(
                action.title, action.assignee, action.to_status or "TODO"
            )
        elif action.kind == "UPDATE_CARD" and action.card_id:
            fields = {}
            if action.assignee:
                fields["assignee"] = action.assignee
            if action.to_status:
                fields["status"] = action.to_status
            if fields:
                await self._board.update_card(action.card_id, **fields)

    async def _send(self, msg: Any):
        await self._ws.send_json(msg.model_dump())
