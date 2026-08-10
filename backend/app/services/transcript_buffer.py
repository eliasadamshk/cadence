from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass


@dataclass
class BufferedUtterance:
    speaker: str
    text: str
    timestamp: float


class TranscriptBuffer:
    def __init__(self, on_flush: Callable[[str, str], Coroutine], flush_interval: float = 5.0):
        self._on_flush = on_flush  # (new_segment, previous_context) -> None
        self._flush_interval = flush_interval
        self._buffer: list[BufferedUtterance] = []
        self._previous_contexts: list[str] = []
        self._flush_task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    def start(self):
        self._flush_task = asyncio.create_task(self._timer_loop())

    async def stop(self):
        self._stop_event.set()
        if self._flush_task:
            await self._flush_task
            self._flush_task = None
        await self._flush()

    async def add(self, speaker: str, text: str, timestamp: float):
        self._buffer.append(BufferedUtterance(speaker=speaker, text=text, timestamp=timestamp))

    async def _timer_loop(self):
        while True:
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self._flush_interval)
            except TimeoutError:
                if self._buffer:
                    await self._flush()
            else:
                return

    async def _flush(self):
        if not self._buffer:
            return

        self._buffer.sort(key=lambda u: u.timestamp)
        segment = "\n".join(f"[{u.speaker}]: {u.text}" for u in self._buffer)
        previous = "\n---\n".join(self._previous_contexts[-2:])

        self._previous_contexts.append(segment)
        if len(self._previous_contexts) > 3:
            self._previous_contexts.pop(0)

        self._buffer.clear()

        await self._on_flush(segment, previous)
