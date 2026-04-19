from __future__ import annotations

import json

import httpx

from app.models.actions import ExtractedAction

SYSTEM_PROMPT = """You are an action extraction assistant for a software team's standup meeting. You listen to transcript segments and identify project management actions.

The team uses a kanban board with columns: TODO, IN_PROGRESS, IN_REVIEW, DONE.

Current board state:
{board_state}

Team members: {team_members}
Speaker name mapping: {speaker_map}

When you identify actions from the transcript, output a JSON array of action objects. Each action must be one of:

1. MOVE_CARD - A card's status is changing. Common signals:
   - "finished X" / "X is done" / "completed X" → move to DONE
   - "pushed to review" / "submitted for review" → move to IN_REVIEW
   - "starting X" / "working on X now" → move to IN_PROGRESS
   - "merging X" / "approved and merging" → move to DONE
   {{ "kind": "MOVE_CARD", "card_id": "CAD-1", "to_status": "IN_REVIEW", "summary": "Sarah moved OAuth login to review", "source_text": "I finished the auth flow..." }}

2. CREATE_CARD - Someone mentions new work that should be tracked (not on the board yet)
   - "we got a request to add X" / "we should track X" / "add X to the backlog"
   {{ "kind": "CREATE_CARD", "title": "Add input validation to signup form", "assignee": null, "to_status": "TODO", "summary": "New task identified from standup", "source_text": "We need to add input validation..." }}

3. UPDATE_CARD - An existing card's assignee is changing. Common signals:
   - "I'm picking up X" / "I'll take X" / "I'm grabbing X" → assign speaker to that card
   - If the speaker's name is unknown, use the card's current assignee or null
   {{ "kind": "UPDATE_CARD", "card_id": "CAD-4", "assignee": "Sarah", "summary": "Sarah taking over rate limiting", "source_text": "I'll pick up the rate limiting ticket" }}

4. FLAG_BLOCKER - Someone is blocked on a card. Common signals:
   - "blocked on X" / "stuck on X" / "waiting on Y for X" / "X is stuck"
   {{ "kind": "FLAG_BLOCKER", "card_id": "CAD-5", "summary": "Jordan blocked on migration - waiting for DBA", "source_text": "I'm blocked on the migration..." }}

Rules:
- Extract ALL actions with clear intent. A single transcript may contain multiple actions.
- Match references to existing cards by fuzzy matching on title/description. Use the card_id from the board state.
- If someone says they finished/completed a task, that is a MOVE_CARD to DONE.
- If someone says "I'm picking up X" or "I'll take X", always extract UPDATE_CARD. If the speaker is unknown, infer the assignee from names mentioned nearby in the transcript or set assignee to null.
- Do NOT move cards that are already in the target status (check current board state).
- If no actions are found, return an empty array: []
- Return ONLY valid JSON. No markdown, no explanation.

Output format: {{ "actions": [...] }}"""


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

    user_msg = ""
    if previous_context:
        user_msg += f"Previous context (for reference only, do not re-extract actions):\n---\n{previous_context}\n---\n\n"
    user_msg += f"New transcript segment to analyze:\n---\n{transcript_segment}\n---"

    async with httpx.AsyncClient() as client:
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
            },
            timeout=15.0,
        )
        data = resp.json()

    if "choices" not in data:
        raise RuntimeError(f"OpenRouter API error (HTTP {resp.status_code}): {data.get('error', data)}")

    content = data["choices"][0]["message"].get("content")
    if not content:
        return []

    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]

    parsed = json.loads(content)
    actions_raw = parsed.get("actions", [])
    return [ExtractedAction(**a) for a in actions_raw]
