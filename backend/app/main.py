from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.pm.seed import seed_board


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.board = seed_board()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Cadence", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app


app = create_app()
