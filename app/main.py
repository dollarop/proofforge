from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .engine import CampaignEngine
from .live_engine import LiveCampaignEngine
from .models import CampaignRequest, CampaignView


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / os.getenv("PROOFFORGE_DATA_DIR", "data")
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="ProofForge", version="0.1.0")
engine = CampaignEngine(DATA_DIR)
live_engine = LiveCampaignEngine()

app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")
app.mount("/media", StaticFiles(directory=DATA_DIR), name="media")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "mode": "live" if os.getenv("PROOFFORGE_MODE") == "live" else "demo",
        "b2_configured": all(
            os.getenv(name) for name in ("B2_KEY_ID", "B2_APP_KEY", "B2_BUCKET")
        ),
    }


@app.post("/api/campaigns", response_model=CampaignView)
def create_campaign(request: CampaignRequest) -> CampaignView:
    if os.getenv("PROOFFORGE_MODE") == "live":
        return live_engine.generate(request)
    return engine.generate(request)
