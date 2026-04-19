from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


@dataclass(frozen=True)
class Settings:
    assemblyai_api_key: str = os.getenv("ASSEMBLYAI_API_KEY", "")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "google/gemini-3.1-flash-lite-preview")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


settings = Settings()
