"""Fast eval: transcript text -> LLM -> score actions.

No audio, no AssemblyAI. Tests action extraction quality only.
Runs in seconds, minimal API cost.
"""
from __future__ import annotations

import json
import traceback

from app.core.config import settings
from app.models.board import Board
from app.pm.seed import seed_board
from app.services.llm import extract_actions
from evals.scenarios import Scenario
from evals.scoring import ScenarioScore, score_actions


async def eval_scenario(
    scenario: Scenario,
    model_override: str | None = None,
) -> ScenarioScore:
    board = seed_board()
    board_state = await board.get_board()
    board_json = json.dumps(board_state.model_dump(), indent=2)

    speaker_map = {name: name for name in scenario.voice_map}
    transcript = scenario.to_transcript(speaker_map)

    actual = await extract_actions(
        transcript_segment=transcript,
        previous_context="",
        board_state_json=board_json,
        speaker_map=speaker_map,
        api_key=settings.openrouter_api_key,
        model=model_override or settings.openrouter_model,
    )

    return score_actions(scenario.name, scenario.expected_actions, actual)
