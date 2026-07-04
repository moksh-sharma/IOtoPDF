"""Shakkar Daddy - Resume.io to PDF web application."""

__author__ = "Shakkar Daddy"

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.api import router

app = FastAPI(title="Shakkar Daddy · Resume.io to PDF")
app.include_router(router)

static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
