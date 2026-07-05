from __future__ import annotations

import hashlib
import json
import os
import textwrap
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from genblaze_core import Manifest, Modality, RunBuilder, StepBuilder, StepStatus
from PIL import Image, ImageDraw, ImageFont

from .models import AssetView, CampaignRequest, CampaignView


SIZES = {
    "square": (1080, 1080),
    "portrait": (1080, 1350),
    "landscape": (1600, 900),
}

PALETTES = [
    ((13, 18, 24), (240, 78, 57), (245, 244, 238)),
    ((245, 244, 238), (19, 98, 83), (20, 28, 34)),
    ((26, 32, 44), (244, 188, 54), (248, 248, 244)),
    ((242, 238, 229), (69, 89, 164), (24, 29, 36)),
]


@dataclass(frozen=True)
class GeneratedAsset:
    asset_id: str
    path: Path
    sha256: str
    score: int
    verdict: str
    alt_text: str
    provider: str = "proofforge-local"
    model: str = "layout-engine-v1"


class CampaignEngine:
    """Runs a deterministic demo pipeline while preserving Genblaze provenance."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.runs_dir = data_dir / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, request: CampaignRequest) -> CampaignView:
        run_id = str(uuid.uuid4())
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True)

        generated = [self._render_variant(request, run_dir, i) for i in range(request.variants)]
        run_builder = RunBuilder("proofforge-campaign-pack").run_id(run_id)

        for index, item in enumerate(generated):
            prompt = self._prompt(request, index)
            step = (
                StepBuilder(item.provider, item.model)
                .prompt(prompt)
                .modality(Modality.IMAGE)
                .params(
                    format=request.format,
                    tone=request.tone,
                    quality_score=item.score,
                    evaluator_verdict=item.verdict,
                )
                .status(StepStatus.SUCCEEDED)
                .asset(
                    item.path.resolve().as_uri(),
                    "image/png",
                    sha256=item.sha256,
                    size_bytes=item.path.stat().st_size,
                )
                .build()
            )
            run_builder.add_step(step)

        run = run_builder.build()
        manifest = Manifest.from_run(run)
        manifest_path = run_dir / "manifest.json"
        manifest_path.write_text(manifest.to_canonical_json(), encoding="utf-8")

        summary = {
            "run_id": run_id,
            "created_at": datetime.now(UTC).isoformat(),
            "request": request.model_dump(),
            "manifest_hash": manifest.canonical_hash,
            "verified": manifest.verify(),
        }
        (run_dir / "summary.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8"
        )

        mode = "live" if os.getenv("PROOFFORGE_MODE") == "live" else "demo"
        assets = [
            AssetView(
                id=item.asset_id,
                url=f"/media/runs/{run_id}/{item.path.name}",
                sha256=item.sha256,
                score=item.score,
                verdict=item.verdict,
                alt_text=item.alt_text,
                provider=item.provider,
                model=item.model,
            )
            for item in generated
        ]
        return CampaignView(
            run_id=run_id,
            status="complete",
            mode=mode,
            storage="local",
            manifest_url=f"/media/runs/{run_id}/manifest.json",
            manifest_hash=manifest.canonical_hash,
            verified=manifest.verify(),
            assets=assets,
        )

    def _render_variant(
        self, request: CampaignRequest, run_dir: Path, index: int
    ) -> GeneratedAsset:
        width, height = SIZES[request.format]
        background, accent, foreground = PALETTES[index % len(PALETTES)]
        image = Image.new("RGB", (width, height), background)
        draw = ImageDraw.Draw(image)
        title_font = self._font(max(48, width // 15), bold=True)
        body_font = self._font(max(25, width // 34))
        label_font = self._font(max(19, width // 48), bold=True)

        margin = width // 12
        draw.rectangle((margin, margin, margin + width // 7, margin + 12), fill=accent)
        draw.text((margin, margin + 42), request.product.upper(), font=label_font, fill=accent)

        max_chars = 21 if request.format == "portrait" else 27
        headline = textwrap.fill(request.promise, width=max_chars)
        headline_y = int(height * 0.25)
        draw.multiline_text(
            (margin, headline_y), headline, font=title_font, fill=foreground, spacing=10
        )

        audience = textwrap.fill(f"Built for {request.audience}.", width=42)
        draw.multiline_text(
            (margin, int(height * 0.72)), audience, font=body_font, fill=foreground, spacing=7
        )
        draw.rounded_rectangle(
            (margin, int(height * 0.84), margin + width // 3, int(height * 0.84) + 68),
            radius=8,
            fill=accent,
        )
        draw.text(
            (margin + 24, int(height * 0.84) + 18),
            ["SEE HOW", "START NOW", "EXPLORE", "TRY IT"][index % 4],
            font=label_font,
            fill=background,
        )

        asset_id = f"variant-{index + 1}"
        path = run_dir / f"{asset_id}.png"
        image.save(path, "PNG", optimize=True)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        score = 91 - (index * 3) + (len(request.promise) % 5)
        verdict = "ready" if score >= 85 else "review"
        alt_text = f"{request.product} campaign graphic: {request.promise}"
        return GeneratedAsset(asset_id, path, digest, score, verdict, alt_text)

    @staticmethod
    def _prompt(request: CampaignRequest, index: int) -> str:
        return (
            f"Create campaign variant {index + 1} for {request.product}. "
            f"Audience: {request.audience}. Promise: {request.promise}. "
            f"Tone: {request.tone}. Format: {request.format}."
        )

    @staticmethod
    def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        candidates = [
            Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return ImageFont.truetype(str(candidate), size=size)
        return ImageFont.load_default()
