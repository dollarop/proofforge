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
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'self'" in response.headers["content-security-policy"]


def test_readiness_reports_demo_without_exposing_secrets(monkeypatch) -> None:
    for name in LiveCampaignEngine.required_env:
        monkeypatch.delenv(name, raising=False)
    payload = TestClient(app).get("/api/readiness").json()
    assert payload["demo_pipeline"] is True
    assert payload["live_pipeline"] is False
    assert payload["b2_pipeline"] is False
    assert payload["missing_live_configuration"] == list(LiveCampaignEngine.required_env)


def test_campaign_api_rejects_invalid_and_returns_verified_assets() -> None:
    client = TestClient(app)
    invalid = client.post("/api/campaigns", json={"product": "x"})
    assert invalid.status_code == 422

    response = client.post(
        "/api/campaigns",
        json={
            "product": "ProofForge",
            "audience": "creative teams",
            "promise": "Generate campaign media with verifiable provenance",
            "tone": "clear",
            "format": "square",
            "variants": 3,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["verified"] is True
    assert len(payload["assets"]) == 3
    assert all(len(asset["sha256"]) == 64 for asset in payload["assets"])


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


def test_b2_mode_requires_scoped_storage_credentials(monkeypatch) -> None:
    for name in ("B2_KEY_ID", "B2_APP_KEY", "B2_BUCKET"):
        monkeypatch.delenv(name, raising=False)
    assert CampaignEngine.b2_configured() is False
