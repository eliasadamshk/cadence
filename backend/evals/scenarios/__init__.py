from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Line:
    speaker: str
    text: str


@dataclass
class ExpectedAction:
    kind: str
    card_id: str | None = None
    title_contains: str | None = None  # fuzzy match for CREATE_CARD
    assignee: str | None = None
    to_status: str | None = None


@dataclass
class Scenario:
    name: str
    description: str
    lines: list[Line]
    expected_actions: list[ExpectedAction]
    # Voice assignments for TTS generation
    voice_map: dict[str, str] = field(default_factory=dict)

    def to_transcript(self, speaker_map: dict[str, str] | None = None) -> str:
        result = []
        for line in self.lines:
            label = speaker_map.get(line.speaker, line.speaker) if speaker_map else line.speaker
            result.append(f"[{label}]: {line.text}")
        return "\n".join(result)

    def to_tts_text(self) -> str:
        """Format for Gemini multi-speaker TTS input."""
        return "\n".join(f"{line.speaker}: {line.text}" for line in self.lines)
