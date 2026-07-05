from pathlib import Path

from fastapi.testclient import TestClient

from app.engine import CampaignEngine
from app.live_engine import LiveCampaignEngine
from app.main import app
from app.models import CampaignRequest


def test_health() -> None:
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo_campaign_has_verified_manifest(tmp_path: Path) -> None:
    result = CampaignEngine(tmp_path).generate(
        CampaignRequest(
            product="ProofForge",
            audience="small creative teams",
            promise="Generate campaign media with traceable provenance",
            tone="clear",
            format="square",
            variants=3,
        )
    )

    assert result.verified is True
    assert len(result.assets) == 3
    assert all(len(asset.sha256) == 64 for asset in result.assets)
    assert (tmp_path / "runs" / result.run_id / "manifest.json").exists()


def test_live_engine_requires_all_credentials(monkeypatch) -> None:
    for name in LiveCampaignEngine.required_env:
        monkeypatch.delenv(name, raising=False)
    assert LiveCampaignEngine.configured() is False
