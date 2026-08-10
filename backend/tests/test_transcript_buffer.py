import asyncio

import pytest

from app.services.transcript_buffer import TranscriptBuffer


@pytest.mark.asyncio
async def test_flushes_within_configured_latency():
    flushed = asyncio.Event()

    async def on_flush(segment: str, previous: str):
        flushed.set()

    buffer = TranscriptBuffer(on_flush=on_flush, flush_interval=0.01)
    buffer.start()
    await buffer.add("Sarah", "Dashboard is done.", 1)

    await asyncio.wait_for(flushed.wait(), timeout=0.2)
    await buffer.stop()


@pytest.mark.asyncio
async def test_stop_waits_for_final_flush():
    callback_started = asyncio.Event()
    release_callback = asyncio.Event()
    flushed = []

    async def on_flush(segment: str, previous: str):
        callback_started.set()
        await release_callback.wait()
        flushed.append((segment, previous))

    buffer = TranscriptBuffer(on_flush=on_flush, flush_interval=60)
    buffer.start()
    await buffer.add("Sarah", "OAuth is ready for review.", 1)

    stop_task = asyncio.create_task(buffer.stop())
    await callback_started.wait()
    assert not stop_task.done()

    release_callback.set()
    await stop_task

    assert flushed == [("[Sarah]: OAuth is ready for review.", "")]


@pytest.mark.asyncio
async def test_previous_context_is_carried_between_flushes():
    flushed = []

    async def on_flush(segment: str, previous: str):
        flushed.append((segment, previous))

    buffer = TranscriptBuffer(on_flush=on_flush, flush_interval=60)
    buffer.start()
    await buffer.add("A", "First update", 1)
    await buffer._flush()
    await buffer.add("B", "Second update", 2)
    await buffer.stop()

    assert flushed == [
        ("[A]: First update", ""),
        ("[B]: Second update", "[A]: First update"),
    ]
