from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("DB_PATH", str(BASE_DIR / "data" / "app.db")))
FRONTEND_DIR = Path(os.getenv("FRONTEND_DIR", str(BASE_DIR / "frontend")))
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral-nemo:12b")
