from __future__ import annotations

import asyncio
import base64
import json
import logging
import time
import uuid
from collections.abc import Callable, Coroutine
from contextlib import suppress
from typing import Any
from urllib.parse import urlencode

import websockets
from websockets.exceptions import ConnectionClosed

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
        params = {
            "sample_rate": 16000,
            "speech_model": "u3-rt-pro",
            "speaker_labels": "true",
            "max_speakers": 4,
            "min_turn_silence": 100,
            "max_turn_silence": 700,
        }
        if self._keyterms:
            params["keyterms_prompt"] = json.dumps([term[:50] for term in self._keyterms[:100]])
        url = f"{STREAMING_URL}?{urlencode(params)}"
        self._ws = await websockets.connect(
            url,
            additional_headers={"Authorization": self._api_key},
        )
        self._receive_task = asyncio.create_task(self._receive_loop(self._ws))

    async def send_audio(self, base64_audio: str):
        if self._ws:
            await self._ws.send(base64.b64decode(base64_audio))

    async def close(self):
        ws = self._ws
        receive_task = self._receive_task
        self._ws = None
        self._receive_task = None

        if not ws:
            if receive_task:
                receive_task.cancel()
            return

        with suppress(ConnectionClosed):
            await ws.send(json.dumps({"type": "Terminate"}))

        if receive_task:
            try:
                await asyncio.wait_for(receive_task, timeout=10)
            except TimeoutError:
                receive_task.cancel()
                with suppress(asyncio.CancelledError):
                    await receive_task

        with suppress(ConnectionClosed):
            await ws.close()

    async def _receive_loop(self, ws):
        async for raw in ws:
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
        if speaker := msg.get("speaker_label"):
            return speaker
        words = msg.get("words", [])
        if words and "speaker" in words[0]:
            return words[0]["speaker"]
        return "UNKNOWN"
