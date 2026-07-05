from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "media"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#111820"
PAPER = "#F4F1EA"
WHITE = "#FCFBF8"
RED = "#F34C3C"
GREEN = "#14715F"
GOLD = "#E7B73D"
BLUE = "#455DA8"


def font(size: int, bold: bool = False):
    path = Path(f"C:/Windows/Fonts/{'arialbd' if bold else 'arial'}.ttf")
    return ImageFont.truetype(str(path), size)


def wrapped(draw, xy, text, width, fill, size, bold=False, spacing=10):
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font(size, bold)) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    draw.multiline_text(xy, "\n".join(lines), fill=fill, font=font(size, bold), spacing=spacing)


def cover():
    image = Image.new("RGB", (1500, 1000), INK)
    draw = ImageDraw.Draw(image)
    draw.rectangle((90, 85, 335, 103), fill=RED)
    draw.text((90, 142), "PROOFFORGE", fill=RED, font=font(30, True))
    wrapped(draw, (90, 285), "Generate media you can prove.", 980, WHITE, 92, True, 12)
    wrapped(
        draw,
        (94, 650),
        "Evaluated campaign variants. Canonical Genblaze manifests. Durable Backblaze B2 storage.",
        900,
        "#C8CDD1",
        32,
        False,
        8,
    )
    draw.rounded_rectangle((1130, 105, 1395, 900), radius=8, fill="#1C2730")
    for y, color, label in [(180, RED, "GENERATE"), (400, GOLD, "EVALUATE"), (620, GREEN, "VERIFY")]:
        draw.ellipse((1210, y, 1315, y + 105), fill=color)
        draw.text((1172, y + 130), label, fill=WHITE, font=font(22, True))
    image.save(OUT / "proofforge-cover-3x2.png", optimize=True)


def architecture():
    image = Image.new("RGB", (1500, 1000), PAPER)
    draw = ImageDraw.Draw(image)
    draw.text((80, 70), "A provenance-first media pipeline", fill=INK, font=font(54, True))
    draw.text((82, 140), "Every output remains connected to the work that produced it.", fill="#596069", font=font(26))
    boxes = [
        (80, 310, 340, 690, RED, "01", "BRIEF", "Product, audience, promise, tone, format"),
        (440, 310, 700, 690, BLUE, "02", "GENERATE", "Genblaze orchestrates provider and fallback model"),
        (800, 310, 1060, 690, GOLD, "03", "EVALUATE", "Quality score, verdict, alt text, retry policy"),
        (1160, 310, 1420, 690, GREEN, "04", "PERSIST", "Asset and canonical manifest stored on B2"),
    ]
    for x1, y1, x2, y2, color, number, title, body in boxes:
        draw.rounded_rectangle((x1, y1, x2, y2), radius=8, fill=WHITE, outline="#CBC8C0", width=2)
        draw.rectangle((x1, y1, x2, y1 + 12), fill=color)
        draw.text((x1 + 25, y1 + 45), number, fill=color, font=font(28, True))
        draw.text((x1 + 25, y1 + 112), title, fill=INK, font=font(27, True))
        wrapped(draw, (x1 + 25, y1 + 190), body, 205, "#596069", 22, False, 8)
    draw.text((80, 845), "GENBLAZE", fill=GREEN, font=font(25, True))
    draw.text((245, 845), "+", fill="#8B8F93", font=font(25, True))
    draw.text((285, 845), "BACKBLAZE B2", fill=RED, font=font(25, True))
    draw.text((535, 845), "= inspectable, durable, verifiable media", fill=INK, font=font(25))
    image.save(OUT / "proofforge-architecture-3x2.png", optimize=True)


def integrity():
    image = Image.new("RGB", (1500, 1000), WHITE)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 500, 1000), fill=GREEN)
    draw.text((65, 82), "VERIFIED", fill=WHITE, font=font(27, True))
    draw.text((65, 220), "SHA-256", fill=WHITE, font=font(70, True))
    wrapped(draw, (65, 340), "Integrity is visible, not implied.", 350, WHITE, 42, True, 10)
    draw.text((65, 790), "Canonical Genblaze manifest", fill="#CDE9E1", font=font(22))
    draw.text((65, 830), "Asset hashes + model lineage", fill="#CDE9E1", font=font(22))
    draw.text((590, 90), "What judges can inspect", fill=INK, font=font(50, True))
    rows = [
        ("Provider + model", "Which generator produced the asset"),
        ("Prompt + parameters", "The exact generation context"),
        ("Evaluation", "Score, verdict, and accessible alt text"),
        ("Asset digest", "A SHA-256 fingerprint for every output"),
        ("Durable URI", "The Backblaze B2 storage location"),
    ]
    for i, (title, body) in enumerate(rows):
        y = 220 + i * 135
        draw.ellipse((590, y, 628, y + 38), fill=RED if i < 2 else GREEN)
        draw.text((650, y - 5), title, fill=INK, font=font(27, True))
        draw.text((650, y + 39), body, fill="#656B70", font=font(22))
    image.save(OUT / "proofforge-integrity-3x2.png", optimize=True)


if __name__ == "__main__":
    cover()
    architecture()
    integrity()

