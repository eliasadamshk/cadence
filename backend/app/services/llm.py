from __future__ import annotations

import json

import httpx2

from app.models.actions import ExtractedAction, ExtractedActions

SYSTEM_PROMPT = """You extract project-management actions from a software standup.

The team uses a kanban board with columns: TODO, IN_PROGRESS, IN_REVIEW, DONE.

Current board state:
{board_state}

Team members: {team_members}
Speaker name mapping: {speaker_map}

Return every clear action. Each action must be one of:

1. MOVE_CARD - A card's status is changing. Common signals:
   - "finished X" / "X is done" / "completed X" → move to DONE
   - "pushed to review" / "submitted for review" → move to IN_REVIEW
   - "starting X" / "working on X now" → move to IN_PROGRESS
   - "merging X" / "approved and merging" → move to DONE
   MOVE_CARD requires card_id and to_status.

2. CREATE_CARD - Someone mentions new work that is not already on the board.
   - "we got a request to add X" / "we should track X" / "add X to the backlog"
   CREATE_CARD requires title and normally uses TODO.

3. UPDATE_CARD - An existing card's assignee is changing. Common signals:
   - "I'm picking up X" / "I'll take X" / "I'm grabbing X" → assign speaker to that card
   - If the speaker's name is unknown, use the card's current assignee or null
   UPDATE_CARD requires card_id and the changed assignee or status.

4. FLAG_BLOCKER - Someone is blocked on a card. Common signals:
   - "blocked on X" / "stuck on X" / "waiting on Y for X" / "X is stuck"
   FLAG_BLOCKER requires card_id and a summary that describes the blocker.

Rules:
- Extract ALL actions with clear intent. A single transcript may contain multiple actions.
- Match references to existing cards by fuzzy title matching. Use the board's card_id.
- If someone says they finished/completed a task, that is a MOVE_CARD to DONE.
- For "I'm picking up X" or "I'll take X", extract UPDATE_CARD.
- Infer the assignee from the speaker map or nearby names; otherwise use null.
- Do NOT move cards that are already in the target status (check current board state).
- Return at most one action per card. Combine repeated or paraphrased mentions and use
  the final intended state.
- If no actions are found, return an empty array: []
- Set fields that do not apply to null.
- Follow the supplied JSON schema exactly."""


async def extract_actions(
    transcript_segment: str,
    previous_context: str,
    board_state_json: str,
    speaker_map: dict[str, str],
    api_key: str,
    model: str,
) -> list[ExtractedAction]:
    board_data = json.loads(board_state_json)
    members = set()
    for col in board_data.get("columns", []):
        for card in col.get("cards", []):
            if card.get("assignee"):
                members.add(card["assignee"])

    system = SYSTEM_PROMPT.format(
        board_state=board_state_json,
        team_members=", ".join(sorted(members)) if members else "unknown",
        speaker_map=json.dumps(speaker_map),
    )

    user_parts = []
    if previous_context:
        user_parts.append(
            f"Previous context (reference only; do not re-extract):\n---\n{previous_context}\n---"
        )
    user_parts.append(f"New transcript segment:\n---\n{transcript_segment}\n---")
    user_msg = "\n\n".join(user_parts)

    async with httpx2.AsyncClient() as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_msg},
                ],
                "temperature": 0.0,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "standup_actions",
                        "strict": True,
                        "schema": ExtractedActions.model_json_schema(),
                    },
                },
                "provider": {
                    "require_parameters": True,
                    "sort": "latency",
                },
            },
            timeout=15.0,
        )
        data = resp.json()

    if "choices" not in data:
        detail = data.get("error", data)
        raise RuntimeError(f"OpenRouter API error (HTTP {resp.status_code}): {detail}")

    content = data["choices"][0]["message"].get("content")
    if not content:
        return []

    return ExtractedActions.model_validate_json(content).actions
