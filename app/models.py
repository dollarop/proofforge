from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CampaignRequest(BaseModel):
    product: str = Field(min_length=2, max_length=80)
    audience: str = Field(min_length=2, max_length=160)
    promise: str = Field(min_length=4, max_length=240)
    tone: Literal["clear", "bold", "warm", "playful"] = "clear"
    format: Literal["square", "portrait", "landscape"] = "square"
    variants: int = Field(default=3, ge=2, le=4)

    @field_validator("product", "audience", "promise")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return " ".join(value.split())


class AssetView(BaseModel):
    id: str
    url: str
    sha256: str
    score: int
    verdict: str
    alt_text: str
    provider: str
    model: str


class CampaignView(BaseModel):
    run_id: str
    status: Literal["complete", "failed"]
    mode: Literal["demo", "live"]
    storage: Literal["local", "b2"]
    manifest_url: str
    manifest_hash: str
    verified: bool
    assets: list[AssetView]

