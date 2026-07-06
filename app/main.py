from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi import Request
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


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data: https:; "
        "style-src 'self'; script-src 'self'; connect-src 'self'"
    )
    return response

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
        "b2_configured": CampaignEngine.b2_configured(),
    }


@app.get("/api/readiness")
def readiness() -> dict[str, str | bool | list[str]]:
    live = LiveCampaignEngine.configured()
    b2 = CampaignEngine.b2_configured()
    return {
        "status": "ready",
        "demo_pipeline": True,
        "live_pipeline": live,
        "b2_pipeline": b2,
        "storage": "b2" if b2 else "local-ephemeral",
        "missing_live_configuration": [
            name for name in LiveCampaignEngine.required_env if not os.getenv(name)
        ],
    }


@app.post("/api/campaigns", response_model=CampaignView)
def create_campaign(request: CampaignRequest) -> CampaignView:
    if os.getenv("PROOFFORGE_MODE") == "live":
        return live_engine.generate(request)
    return engine.generate(request)
