from __future__ import annotations

import asyncio
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field


@dataclass
class BufferedUtterance:
    speaker: str
    text: str
    timestamp: float


class TranscriptBuffer:
    def __init__(self, on_flush: Callable[[str, str], Coroutine], flush_interval: float = 30.0):
        self._on_flush = on_flush  # (new_segment, previous_context) -> None
        self._flush_interval = flush_interval
        self._buffer: list[BufferedUtterance] = []
        self._previous_contexts: list[str] = []
        self._last_flush_time = time.time()
        self._flush_task: asyncio.Task | None = None

    def start(self):
        self._flush_task = asyncio.create_task(self._timer_loop())

    def stop(self):
        if self._flush_task:
            self._flush_task.cancel()
        if self._buffer:
            asyncio.create_task(self._flush())

    async def add(self, speaker: str, text: str, timestamp: float):
        self._buffer.append(BufferedUtterance(speaker=speaker, text=text, timestamp=timestamp))

    async def _timer_loop(self):
        while True:
            await asyncio.sleep(self._flush_interval)
            if self._buffer:
                await self._flush()

    async def _flush(self):
        if not self._buffer:
            return

        self._buffer.sort(key=lambda u: u.timestamp)
        segment = "\n".join(
            f"[{u.speaker}]: {u.text}" for u in self._buffer
        )
        previous = "\n---\n".join(self._previous_contexts[-2:])

        self._previous_contexts.append(segment)
        if len(self._previous_contexts) > 3:
            self._previous_contexts.pop(0)

        self._buffer.clear()
        self._last_flush_time = time.time()

        await self._on_flush(segment, previous)
