from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/board")


class MoveCardBody(BaseModel):
    to_status: str


@router.get("")
async def get_board(request: Request):
    board = await request.app.state.board.get_board()
    return board.model_dump()


@router.post("/seed")
async def seed_board(request: Request):
    from app.pm.seed import seed_board

    request.app.state.board = seed_board()
    board = await request.app.state.board.get_board()
    return board.model_dump()


@router.post("/cards/{card_id}/move")
async def move_card(card_id: str, body: MoveCardBody, request: Request):
    try:
        await request.app.state.board.move_card(card_id, body.to_status)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Card {card_id} not found")
    board = await request.app.state.board.get_board()
    return board.model_dump()
