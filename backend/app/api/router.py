from fastapi import APIRouter

from app.api.routes import board, health, meeting

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(board.router)
api_router.include_router(meeting.router)
