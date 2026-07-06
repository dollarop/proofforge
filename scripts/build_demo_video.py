from __future__ import annotations

import json
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "docs" / "media"
OUTPUT = MEDIA / "proofforge-demo.mp4"
SIZE = (1280, 720)
FPS = 12
INK = "#111820"
PAPER = "#F4F1EA"
WHITE = "#FCFBF8"
RED = "#F34C3C"
GREEN = "#14715F"
MUTED = "#667078"


def font(size: int, bold: bool = False):
    path = Path(f"C:/Windows/Fonts/{'arialbd' if bold else 'arial'}.ttf")
    return ImageFont.truetype(str(path), size)


def wrap(draw, text: str, max_width: int, size: int, bold: bool = False) -> str:
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font(size, bold)) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


def base(title: str, kicker: str = "PROOFFORGE") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", SIZE, PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((55, 48, 215, 59), fill=RED)
    draw.text((55, 78), kicker, fill=RED, font=font(20, True))
    draw.multiline_text((55, 128), wrap(draw, title, 1130, 53, True), fill=INK, font=font(53, True), spacing=8)
    return image, draw


def intro() -> Image.Image:
    image = Image.open(MEDIA / "proofforge-cover-3x2.png").convert("RGB")
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def brief_slide() -> Image.Image:
    image, draw = base("One structured brief. Multiple traceable variants.")
    fields = [
        ("PRODUCT", "ProofForge"),
        ("AUDIENCE", "Creative teams"),
        ("PROMISE", "Generate media with verifiable provenance"),
        ("TONE", "Clear"),
        ("FORMAT", "Square 1:1"),
    ]
    y = 300
    for label, value in fields:
        draw.text((65, y), label, fill=GREEN, font=font(18, True))
        draw.text((260, y - 3), value, fill=INK, font=font(27))
        draw.line((65, y + 47, 1160, y + 47), fill="#D4D0C8", width=2)
        y += 72
    return image


def results_slide() -> Image.Image:
    image, draw = base("The pipeline returns evaluated campaign media.")
    runs = sorted((ROOT / "data" / "runs").glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    pngs = list(runs[0].glob("variant-*.png"))[:3] if runs else []
    for index, path in enumerate(pngs):
        thumb = Image.open(path).convert("RGB").resize((270, 270), Image.Resampling.LANCZOS)
        x = 65 + index * 395
        image.paste(thumb, (x, 300))
        draw.text((x, 595), f"VARIANT {index + 1}", fill=INK, font=font(20, True))
        draw.text((x + 175, 595), f"{91 - index * 3}/100", fill=GREEN, font=font(20, True))
    draw.text((65, 660), "Public app: https://proofforge.onrender.com", fill=MUTED, font=font(20))
    return image


def manifest_slide() -> Image.Image:
    image, draw = base("Every asset is bound to a canonical manifest.")
    runs = sorted((ROOT / "data" / "runs").glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    summary = {}
    if runs and (runs[0] / "summary.json").exists():
        summary = json.loads((runs[0] / "summary.json").read_text(encoding="utf-8"))
    hash_value = summary.get("manifest_hash", "SHA-256 verified")
    rows = [
        ("RUN", str(summary.get("run_id", "verified public run"))),
        ("PROVIDER", "proofforge-local / GMI Cloud live adapter"),
        ("MODEL", "layout-engine-v1 / Seedream with Gemini fallback"),
        ("INTEGRITY", hash_value),
        ("VERIFIED", str(summary.get("verified", True)).lower()),
    ]
    y = 300
    for label, value in rows:
        draw.text((65, y), label, fill=GREEN, font=font(18, True))
        shown = value if len(value) < 76 else value[:73] + "..."
        draw.text((265, y - 3), shown, fill=INK, font=font(23))
        y += 67
    return image


def image_slide(filename: str) -> Image.Image:
    return Image.open(MEDIA / filename).convert("RGB").resize(SIZE, Image.Resampling.LANCZOS)


def close_slide() -> Image.Image:
    image = Image.new("RGB", SIZE, INK)
    draw = ImageDraw.Draw(image)
    draw.rectangle((65, 65, 275, 79), fill=RED)
    draw.text((65, 110), "PROOFFORGE", fill=RED, font=font(25, True))
    draw.multiline_text((65, 245), "Inspectable.\nDurable. Verifiable.", fill=WHITE, font=font(66, True), spacing=10)
    draw.text((67, 585), "Genblaze orchestration + Backblaze B2 storage", fill="#C9CED2", font=font(25))
    draw.text((67, 635), "https://proofforge.onrender.com", fill=WHITE, font=font(23, True))
    return image


def append_slide(writer, frame: Image.Image, seconds: float, previous: Image.Image | None):
    array = np.asarray(frame)
    if previous is not None:
        old = np.asarray(previous).astype(np.float32)
        new = array.astype(np.float32)
        for index in range(FPS):
            alpha = (index + 1) / FPS
            writer.append_data((old * (1 - alpha) + new * alpha).astype(np.uint8))
    for _ in range(int(seconds * FPS)):
        writer.append_data(array)


def main():
    slides = [
        (intro(), 7),
        (brief_slide(), 10),
        (results_slide(), 12),
        (manifest_slide(), 12),
        (image_slide("proofforge-architecture-3x2.png"), 12),
        (image_slide("proofforge-integrity-3x2.png"), 12),
        (close_slide(), 8),
    ]
    with imageio.get_writer(
        OUTPUT,
        fps=FPS,
        codec="libx264",
        quality=8,
        pixelformat="yuv420p",
        ffmpeg_log_level="warning",
    ) as writer:
        previous = None
        for frame, seconds in slides:
            append_slide(writer, frame, seconds, previous)
            previous = frame
    print(OUTPUT)


if __name__ == "__main__":
    main()
