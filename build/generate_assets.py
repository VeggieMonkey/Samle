"""Generate all graphical assets for Samle.

Produces:
  assets/icon.ico         – app icon (16/32/48/64/128/256 px)
  assets/installer_side.bmp   – Inno Setup wizard side image (164x314)
  assets/installer_header.bmp – Inno Setup header banner (497x55)
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

# Version is injected by build.py via the SAMLE_VERSION env var.
# When running generate_assets.py directly, falls back to pyproject.toml.
def _get_version() -> str:
    v = os.environ.get("SAMLE_VERSION", "")
    if v:
        return v
    try:
        import tomllib
        with open(ROOT / "pyproject.toml", "rb") as f:
            return tomllib.load(f)["project"]["version"]
    except Exception:
        return "0.0.0"


def _load_fonts(big_size: int, small_size: int):
    """Load fonts cross-platform; falls back to PIL default."""
    candidates_bold = [
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    candidates_reg = [
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    try:
        font_big = next(
            ImageFont.truetype(p, big_size) for p in candidates_bold if Path(p).exists()
        )
        font_small = next(
            ImageFont.truetype(p, small_size) for p in candidates_reg if Path(p).exists()
        )
        return font_big, font_small
    except StopIteration:
        default = ImageFont.load_default()
        return default, default


# ── Colour palette (Norwegian blue + modern accent) ────────────────────────
BLUE_DARK   = (30,  80, 162)   # #1E50A2
BLUE_MID    = (45, 110, 220)   # #2D6EDC
BLUE_LIGHT  = (90, 155, 255)   # #5A9BFF
WHITE       = (255, 255, 255)
OFF_WHITE   = (245, 247, 252)
GRAY_LIGHT  = (220, 228, 240)
GRAY_TEXT   = (100, 110, 130)


def _round_rect(draw: ImageDraw.ImageDraw, xy, radius: int, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.ellipse([x0, y0, x0 + radius * 2, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y0, x1, y0 + radius * 2], fill=fill)
    draw.ellipse([x0, y1 - radius * 2, x0 + radius * 2, y1], fill=fill)
    draw.ellipse([x1 - radius * 2, y1 - radius * 2, x1, y1], fill=fill)


def _draw_pdf_page(draw: ImageDraw.ImageDraw, x, y, w, h, color, fold=True):
    """Draw a simplified PDF page shape with a folded corner."""
    fold_size = w // 4
    if fold:
        # Main body (without top-right triangle)
        draw.polygon([
            (x, y),
            (x + w - fold_size, y),
            (x + w, y + fold_size),
            (x + w, y + h),
            (x, y + h),
        ], fill=color)
        # Fold triangle
        darker = tuple(max(0, c - 40) for c in color)
        draw.polygon([
            (x + w - fold_size, y),
            (x + w, y + fold_size),
            (x + w - fold_size, y + fold_size),
        ], fill=darker)
    else:
        draw.rectangle([x, y, x + w, y + h], fill=color)


def _draw_lines(draw: ImageDraw.ImageDraw, x, y, w, line_color, count=3, gap=None):
    """Draw small horizontal lines to suggest text content."""
    gap = gap or w // 5
    lh = max(1, w // 10)
    for i in range(count):
        lw = w - (i % 2) * (w // 4)
        draw.rectangle([x, y + i * gap, x + lw, y + i * gap + lh], fill=line_color)


def make_icon_image(size: int) -> Image.Image:
    """Render the icon at *size*x*size* with RGBA."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = max(1, size // 16)
    r = max(2, size // 8)   # corner radius for background pill

    # Background rounded square
    _round_rect(draw, [pad, pad, size - pad, size - pad], r, BLUE_MID)

    # Two PDF pages that merge into one
    # Page dimensions scaled to icon size
    pw = int(size * 0.30)
    ph = int(size * 0.38)
    fold = int(pw * 0.25)

    # Left page (slightly rotated feel — offset up-left)
    lx = int(size * 0.08)
    ly = int(size * 0.18)
    _draw_pdf_page(draw, lx, ly, pw, ph, WHITE)
    _draw_lines(draw, lx + max(1, pw // 8), ly + int(ph * 0.45),
                int(pw * 0.65), GRAY_LIGHT, count=3, gap=max(2, size // 14))

    # Right page (offset down-right)
    rx = int(size * 0.32)
    ry = int(size * 0.28)
    _draw_pdf_page(draw, rx, ry, pw, ph, (200, 220, 255, 230))
    _draw_lines(draw, rx + max(1, pw // 8), ry + int(ph * 0.45),
                int(pw * 0.65), (160, 185, 230), count=3, gap=max(2, size // 14))

    # Arrow pointing right -> merging
    ax = int(size * 0.62)
    ay = int(size * 0.42)
    aw = int(size * 0.10)
    ah = int(size * 0.16)
    arrow_color = (255, 255, 255, 200)
    # Shaft
    shaft_h = max(1, ah // 3)
    draw.rectangle([ax, ay + ah // 2 - shaft_h // 2,
                    ax + aw, ay + ah // 2 + shaft_h // 2], fill=arrow_color)
    # Head
    draw.polygon([
        (ax + aw, ay),
        (ax + aw + ah // 2, ay + ah // 2),
        (ax + aw, ay + ah),
    ], fill=arrow_color)

    # Output page (larger, centred-right)
    ox = int(size * 0.55)
    oy = int(size * 0.22)
    opw = int(size * 0.34)
    oph = int(size * 0.52)
    _draw_pdf_page(draw, ox, oy, opw, oph, (240, 245, 255))
    _draw_lines(draw, ox + max(1, opw // 8), oy + int(oph * 0.35),
                int(opw * 0.70), GRAY_LIGHT, count=4, gap=max(2, size // 12))

    return img


def build_icon():
    sizes = [16, 24, 32, 48, 64, 128, 256]
    logo = ASSETS / "logo.png"
    out = ASSETS / "icon.ico"

    if logo.exists():
        src = Image.open(logo).convert("RGBA")
        frames = [src.resize((s, s), Image.LANCZOS) for s in sizes]
        print(f"ok icon.ico  (from logo.png -> {', '.join(str(s) for s in sizes)} px)")
    else:
        frames = [make_icon_image(s) for s in sizes]
        print(f"ok icon.ico  (generated -> {', '.join(str(s) for s in sizes)} px)")

    frames[0].save(
        out,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=frames[1:],
    )


# ── Installer side image (164 x 314, 24-bit BMP) ──────────────────────────

def build_installer_side():
    W, H = 164, 314
    img = Image.new("RGB", (W, H), BLUE_DARK)
    draw = ImageDraw.Draw(img)

    # Gradient-like vertical bands
    for x in range(W):
        t = x / W
        r = int(BLUE_DARK[0] + (BLUE_MID[0] - BLUE_DARK[0]) * t)
        g = int(BLUE_DARK[1] + (BLUE_MID[1] - BLUE_DARK[1]) * t)
        b = int(BLUE_DARK[2] + (BLUE_MID[2] - BLUE_DARK[2]) * t)
        draw.line([(x, 0), (x, H)], fill=(r, g, b))

    # Decorative circle (semi-transparent overlay)
    for radius, alpha in [(120, 18), (80, 25), (45, 35)]:
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        cx, cy = W // 2, H // 3
        od.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                   fill=(255, 255, 255, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Draw a mini icon in the centre of the circle
    logo = ASSETS / "logo.png"
    if logo.exists():
        icon = Image.open(logo).convert("RGBA").resize((72, 72), Image.LANCZOS)
    else:
        icon = make_icon_image(72).convert("RGBA")
    ix = (W - 72) // 2
    iy = H // 3 - 36
    img.paste(icon, (ix, iy), icon)

    # App name text
    draw = ImageDraw.Draw(img)
    font_big, font_small = _load_fonts(14, 10)

    name = "Samle"
    bb = draw.textbbox((0, 0), name, font=font_big)
    tw = bb[2] - bb[0]
    draw.text(((W - tw) // 2, H // 3 + 46), name, fill=WHITE, font=font_big)

    tagline = "Merge PDFs with one click"
    bb2 = draw.textbbox((0, 0), tagline, font=font_small)
    tw2 = bb2[2] - bb2[0]
    draw.text(((W - tw2) // 2, H // 3 + 64), tagline, fill=GRAY_LIGHT, font=font_small)

    # Bottom version
    ver = f"v{_get_version()}"
    bb3 = draw.textbbox((0, 0), ver, font=font_small)
    tw3 = bb3[2] - bb3[0]
    draw.text(((W - tw3) // 2, H - 20), ver, fill=GRAY_LIGHT, font=font_small)

    out = ASSETS / "installer_side.bmp"
    img.save(out, format="BMP")
    print(f"ok installer_side.bmp  ({W}x{H})")


# ── Installer small image / header icon (55 x 55, 24-bit BMP) ─────────────
#
# Inno Setup displays WizardSmallImageFile in the upper-right corner of
# inner wizard pages — a fixed ~55 px slot.  Only an icon fits here;
# any text drawn on a wider image would be cropped and unreadable.

def build_installer_header():
    W, H = 55, 55
    img = Image.new("RGB", (W, H), WHITE)

    # Blue gradient background
    draw = ImageDraw.Draw(img)
    for x in range(W):
        t = x / W
        r = int(BLUE_DARK[0] + (BLUE_MID[0] - BLUE_DARK[0]) * t)
        g = int(BLUE_DARK[1] + (BLUE_MID[1] - BLUE_DARK[1]) * t)
        b = int(BLUE_DARK[2] + (BLUE_MID[2] - BLUE_DARK[2]) * t)
        draw.line([(x, 0), (x, H)], fill=(r, g, b))

    # Centred app icon
    logo = ASSETS / "logo.png"
    if logo.exists():
        icon = Image.open(logo).convert("RGBA").resize((40, 40), Image.LANCZOS)
    else:
        icon = make_icon_image(40).convert("RGBA")
    ix = (W - 40) // 2
    iy = (H - 40) // 2
    img.paste(icon, (ix, iy), icon)

    out = ASSETS / "installer_header.bmp"
    img.save(out, format="BMP")
    print(f"ok installer_header.bmp  ({W}x{H})")


if __name__ == "__main__":
    build_icon()
    build_installer_side()
    build_installer_header()
    print("\nAll assets generated in:", ASSETS)
