import pytest

from app.models.actions import ExtractedAction
from app.pm.seed import seed_board
from app.services.meeting_session import MeetingSession


class FakeWebSocket:
    def __init__(self):
        self.messages = []

    async def send_json(self, message):
        self.messages.append(message)


class FakeAssemblyAI:
    def __init__(self, events):
        self.events = events

    async def close(self):
        self.events.append("transcription_closed")


class FakeBuffer:
    def __init__(self, events):
        self.events = events

    async def stop(self):
        self.events.append("buffer_flushed")


@pytest.mark.asyncio
async def test_flag_blocker_action_updates_board():
    board = seed_board()
    session = MeetingSession(ws=FakeWebSocket(), board=board)
    action = ExtractedAction(
        kind="FLAG_BLOCKER",
        card_id="CAD-5",
        title=None,
        assignee=None,
        to_status=None,
        summary="Jordan is waiting for DBA approval",
        source_text="The migration is blocked waiting for the DBA.",
    )

    applied = await session._apply_action(action)

    card = next(card for card in (await board.get_board()).to_flat_cards() if card.id == "CAD-5")
    assert applied is True
    assert card.blocker == action.summary


@pytest.mark.asyncio
async def test_duplicate_move_action_is_not_sent_twice(monkeypatch):
    board = seed_board()
    websocket = FakeWebSocket()
    session = MeetingSession(ws=websocket, board=board)
    first = ExtractedAction(
        kind="MOVE_CARD",
        card_id="CAD-4",
        title=None,
        assignee=None,
        to_status="IN_REVIEW",
        summary="Move rate limiting middleware to review",
        source_text="I put the rate limiting ticket into review.",
    )
    duplicate = first.model_copy(update={"summary": "Rate limiting is now in review"})

    async def extract_actions(**kwargs):
        return [first, duplicate]

    monkeypatch.setattr("app.services.meeting_session.extract_actions", extract_actions)

    await session._on_flush("[A]: Rate limiting is in review.", "")

    action_messages = [
        message for message in websocket.messages if message["type"] == "action_extracted"
    ]
    assert len(action_messages) == 1
    card = next(card for card in (await board.get_board()).to_flat_cards() if card.id == "CAD-4")
    assert card.status == "IN_REVIEW"


@pytest.mark.asyncio
async def test_stop_closes_transcription_before_final_buffer_flush():
    events = []
    session = MeetingSession(ws=FakeWebSocket(), board=seed_board())
    session._aai = FakeAssemblyAI(events)
    session._buffer = FakeBuffer(events)

    await session.stop()

    assert events == ["transcription_closed", "buffer_flushed"]
