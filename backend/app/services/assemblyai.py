from __future__ import annotations

import asyncio
import base64
import json
import logging
import time
import uuid
from collections.abc import Callable, Coroutine
from typing import Any
from urllib.parse import quote

import websockets

log = logging.getLogger(__name__)

STREAMING_URL = "wss://streaming.assemblyai.com/v3/ws"


class AssemblyAIRealtime:
    def __init__(
        self,
        api_key: str,
        on_partial: Callable[[str, str | None], Coroutine],
        on_final: Callable[[str, str, str, float], Coroutine],
        keyterms: list[str] | None = None,
    ):
        self._api_key = api_key
        self._on_partial = on_partial
        self._on_final = on_final
        self._keyterms = keyterms or []
        self._ws: Any = None
        self._receive_task: asyncio.Task | None = None

    async def connect(self):
        url = f"{STREAMING_URL}?sample_rate=16000&speech_model=u3-rt-pro&speaker_labels=true"
        if self._keyterms:
            url += f"&keyterms_prompt={quote(json.dumps(self._keyterms))}"
        self._ws = await websockets.connect(
            url,
            additional_headers={"Authorization": self._api_key},
        )
        self._receive_task = asyncio.create_task(self._receive_loop())

    async def send_audio(self, base64_audio: str):
        if self._ws:
            await self._ws.send(base64.b64decode(base64_audio))

    async def close(self):
        if self._ws:
            try:
                await self._ws.send(json.dumps({"type": "Terminate"}))
                if self._receive_task:
                    try:
                        await asyncio.wait_for(self._receive_task, timeout=10)
                    except (asyncio.TimeoutError, asyncio.CancelledError):
                        pass
                await self._ws.close()
            except Exception:
                pass
            self._ws = None
        elif self._receive_task:
            self._receive_task.cancel()

    async def _receive_loop(self):
        async for raw in self._ws:
            msg = json.loads(raw)
            msg_type = msg.get("type")

            if msg_type == "Error":
                log.error("AssemblyAI error: %s", msg)
                continue

            if msg_type == "Begin":
                log.info("AssemblyAI session started: %s", msg.get("id"))

            elif msg_type == "Turn":
                transcript = msg.get("transcript", "")
                if not transcript:
                    continue
                end_of_turn = msg.get("end_of_turn", False)
                speaker = self._extract_speaker(msg)

                if end_of_turn:
                    utterance_id = str(uuid.uuid4())[:8]
                    await self._on_final(utterance_id, transcript, speaker, time.time() * 1000)
                else:
                    await self._on_partial(transcript, speaker)

            elif msg_type == "Termination":
                log.info("AssemblyAI session terminated")
                break

    def _extract_speaker(self, msg: dict) -> str:
        words = msg.get("words", [])
        if words and "speaker" in words[0]:
            return words[0]["speaker"]
        return "A"
