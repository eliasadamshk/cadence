import pytest

from app.pm.seed import seed_board


@pytest.mark.asyncio
async def test_board_moves_cards_and_persists_blockers():
    board = seed_board()

    moved = await board.move_card("CAD-1", "IN_REVIEW")
    blocked = await board.flag_blocker("CAD-5", "Waiting for DBA approval")
    state = await board.get_board()

    assert moved.status == "IN_REVIEW"
    assert blocked.blocker == "Waiting for DBA approval"
    assert next(card for card in state.to_flat_cards() if card.id == "CAD-5").blocker == (
        "Waiting for DBA approval"
    )
