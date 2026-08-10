from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.pm.seed import seed_board


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.board = seed_board()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Cadence", lifespan=lifespan)

    app.include_router(api_router)
    return app


app = create_app()
