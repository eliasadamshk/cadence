"""Full E2E eval: WAV audio -> WebSocket -> AssemblyAI -> LLM -> score board state.

Requires generated audio fixtures (run generate_audio.py first).
Sends PCM16 chunks over a real WebSocket to the running backend.
"""
from __future__ import annotations

import asyncio
import base64
import json
import struct
import wave
from pathlib import Path

import websockets

from app.models.actions import ExtractedAction
from evals.scenarios import Scenario
from evals.scoring import ScenarioScore, score_actions

FIXTURES_DIR = Path(__file__).parent / "fixtures"
# 16kHz, 100ms chunks = 1600 samples = 3200 bytes
CHUNK_SIZE = 3200
SEND_INTERVAL = 0.1


async def eval_scenario(
    scenario: Scenario,
    ws_url: str = "ws://localhost:8000",
) -> ScenarioScore:
    wav_path = FIXTURES_DIR / f"{scenario.name}.wav"
    if not wav_path.exists():
        raise FileNotFoundError(f"Audio fixture not found: {wav_path}. Run generate_audio.py first.")

    pcm_data = _read_wav_as_pcm16(wav_path, target_rate=16000)

    collected_actions: list[ExtractedAction] = []
    done = asyncio.Event()

    async with websockets.connect(f"{ws_url}/ws/meeting/eval-{scenario.name}") as ws:
        # Send speaker map
        speaker_map = {name: name for name in scenario.voice_map}
        await ws.send(json.dumps({"type": "speaker_map", "map": speaker_map}))
        await ws.send(json.dumps({"type": "start_recording"}))

        transcripts: list[str] = []

        async def receive():
            async for raw in ws:
                msg = json.loads(raw)
                if msg["type"] == "action_extracted":
                    collected_actions.append(ExtractedAction(**msg["action"]))
                elif msg["type"] == "transcript_final":
                    transcripts.append(f"[{msg.get('speaker', '?')}]: {msg.get('text', '')}")

        recv_task = asyncio.create_task(receive())

        # Stream audio at real-time pace
        for offset in range(0, len(pcm_data), CHUNK_SIZE):
            chunk = pcm_data[offset : offset + CHUNK_SIZE]
            b64 = base64.b64encode(chunk).decode()
            await ws.send(json.dumps({"type": "audio_data", "data": b64}))
            await asyncio.sleep(SEND_INTERVAL)

        await asyncio.sleep(8)

        await ws.send(json.dumps({"type": "stop_recording"}))

        await asyncio.sleep(40)
        recv_task.cancel()

    if transcripts:
        print(f"  [transcript] {len(transcripts)} utterances received:")
        for t in transcripts:
            print(f"    {t}")
    if not collected_actions:
        print(f"  [actions] None extracted")
    else:
        for a in collected_actions:
            print(f"  [action] {a.kind} {a.card_id or a.title or ''}")

    return score_actions(scenario.name, scenario.expected_actions, collected_actions)


def _read_wav_as_pcm16(path: Path, target_rate: int = 16000) -> bytes:
    """Read WAV and resample to target rate as raw PCM16 bytes."""
    with wave.open(str(path), "rb") as wf:
        src_rate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    # Parse as int16
    samples = struct.unpack(f"<{n_frames}h", raw)

    if src_rate == target_rate:
        return raw

    # Simple linear resample
    ratio = src_rate / target_rate
    resampled_len = int(n_frames / ratio)
    resampled = []
    for i in range(resampled_len):
        src_idx = min(int(i * ratio), n_frames - 1)
        resampled.append(samples[src_idx])

    return struct.pack(f"<{len(resampled)}h", *resampled)
