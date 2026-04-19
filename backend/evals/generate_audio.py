"""Generate multi-voice audio fixtures from eval scenarios using Gemini TTS.

Usage:
    python -m evals.generate_audio                    # all scenarios
    python -m evals.generate_audio simple_updates     # specific scenario

Requires: GCP_PROJECT and GCP_LOCATION env vars (Vertex AI)
"""
from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from google import genai
from google.genai import types

from evals.scenarios import Scenario

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TTS_MODEL = "gemini-2.5-flash-preview-tts"


def _split_lines_by_speaker_pairs(lines: list, voice_map: dict[str, str]):
    """Split lines into chunks where each chunk has at most 2 distinct speakers."""
    chunks: list[list] = []
    current_chunk: list = []
    current_speakers: set[str] = set()

    for line in lines:
        if line.speaker not in current_speakers and len(current_speakers) >= 2:
            chunks.append((current_chunk, {s: voice_map[s] for s in current_speakers}))
            current_chunk = []
            current_speakers = set()
        current_chunk.append(line)
        current_speakers.add(line.speaker)

    if current_chunk:
        chunks.append((current_chunk, {s: voice_map[s] for s in current_speakers}))

    return chunks


FILLER_VOICES = ["Kore", "Charon", "Puck", "Aoede", "Fenrir", "Leda"]


def _generate_chunk(client, lines: list, voice_map: dict[str, str]) -> bytes:
    """Generate audio for a chunk of lines with at most 2 speakers."""
    # API requires exactly 2 speaker configs; pad with a dummy if needed
    padded_map = dict(voice_map)
    if len(padded_map) == 1:
        used_voices = set(padded_map.values())
        filler_voice = next(v for v in FILLER_VOICES if v not in used_voices)
        padded_map["_unused"] = filler_voice

    speaker_configs = [
        types.SpeakerVoiceConfig(
            speaker=speaker,
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
            ),
        )
        for speaker, voice in padded_map.items()
    ]

    text = "\n".join(f"{line.speaker}: {line.text}" for line in lines)

    response = client.models.generate_content(
        model=TTS_MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=speaker_configs,
                )
            ),
        ),
    )
    return response.candidates[0].content.parts[0].inline_data.data


def generate_audio(scenario: Scenario) -> Path:
    client = genai.Client(
        vertexai=True,
        project=os.environ["GCP_PROJECT"],
        location=os.environ.get("GCP_LOCATION", "us-central1"),
    )
    sample_rate = 24000

    if len(scenario.voice_map) <= 2:
        audio_data = _generate_chunk(client, scenario.lines, scenario.voice_map)
    else:
        chunks = _split_lines_by_speaker_pairs(scenario.lines, scenario.voice_map)
        audio_data = b"".join(_generate_chunk(client, lines, vm) for lines, vm in chunks)

    out_path = FIXTURES_DIR / f"{scenario.name}.wav"
    _write_wav(out_path, audio_data, sample_rate)
    print(f"Generated {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")
    return out_path


def _write_wav(path: Path, pcm_data: bytes, sample_rate: int):
    """Write raw PCM16 mono data as a WAV file."""
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = len(pcm_data)

    with open(path, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        # fmt chunk
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, num_channels, sample_rate, byte_rate, block_align, bits_per_sample))
        # data chunk
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(pcm_data)


def _load_all_scenarios() -> list[Scenario]:
    from evals.scenarios import blockers, mixed, new_tickets, no_actions, reassignment, simple_updates
    return [
        simple_updates.scenario,
        blockers.scenario,
        new_tickets.scenario,
        reassignment.scenario,
        no_actions.scenario,
        mixed.scenario,
    ]


if __name__ == "__main__":
    FIXTURES_DIR.mkdir(exist_ok=True)

    if len(sys.argv) > 1:
        import importlib
        mod = importlib.import_module(f"evals.scenarios.{sys.argv[1]}")
        scenarios = [mod.scenario]
    else:
        scenarios = _load_all_scenarios()

    for s in scenarios:
        generate_audio(s)

    print(f"\nDone. {len(scenarios)} audio fixture(s) generated in {FIXTURES_DIR}/")
