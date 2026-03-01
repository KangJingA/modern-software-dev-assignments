from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .db import init_db
from .routers import action_items, notes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up - initializing database")
    init_db()
    yield
    logger.info("Shutting down")


app = FastAPI(title="Action Item Extractor", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (config.FRONTEND_DIR / "index.html").read_text(encoding="utf-8")


app.include_router(notes.router)
app.include_router(action_items.router)
app.mount("/static", StaticFiles(directory=str(config.FRONTEND_DIR)), name="static")
