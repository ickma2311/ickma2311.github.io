#!/usr/bin/env python3
"""Generate low-text 1600x900 SVG/PNG figures for CMU ANLP Fall 2025 Lecture 11 (v1 r2)."""

from pathlib import Path
import json
import math
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET

OUT_DIR = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"

PALETTE = {
    "background": "#FAF6EE",
    "ink": "#1F2A2E",
    "muted": "#6B655B",
    "blue": "#356482",
    "terracotta": "#B5493A",
    "sage": "#4B6B46",
    "ochre": "#A87919",
}


def arrow_polygon(
    tip_x: float,
    tip_y: float,
    dx: float,
    dy: float,
    length: float = 16.0,
    half_w: float = 7.0,
) -> str:
    """Return explicit <polygon> points for an arrowhead at (tip_x, tip_y)."""
    norm = math.hypot(dx, dy)
    ux, uy = dx / norm, dy / norm
    px, py = -uy, ux
    bx, by = tip_x - length * ux, tip_y - length * uy
    p1 = (bx + half_w * px, by + half_w * py)
    p2 = (bx - half_w * px, by - half_w * py)
    return f"{tip_x:.1f},{tip_y:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"


def draw_arrow(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str = "#4B5558",
    width: float = 3.0,
) -> str:
    """Draw a straight line ending with an explicit <polygon> arrowhead at (x2, y2)."""
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy)
    ux, uy = dx / norm, dy / norm
    lx2, ly2 = x2 - 12.0 * ux, y2 - 12.0 * uy
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{lx2:.1f}" y2="{ly2:.1f}" '
        f'stroke="{color}" stroke-width="{width:.1f}" stroke-linecap="round" />'
        f'<polygon points="{arrow_polygon(x2, y2, dx, dy)}" fill="{color}" />'
    )


def box(
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    subtitle: str = "",
    fill: str = "#F3EEE3",
    stroke: str = "#7A7367",
    title_color: str = "#1F2A2E",
    sub_color: str = "#4B5558",
    title_size: int = 25,
    sub_size: int = 20,
    rx: int = 14,
) -> str:
    """Render a centered rounded box with 1-line title and optional 1-line subtitle."""
    cx = x + w / 2.0
    parts = [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2.2" />'
    ]
    if subtitle:
        ty = y + h * 0.42
        sy = y + h * 0.74
        parts.append(
            f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="{title_size}" '
            f'font-weight="700" fill="{title_color}">{title}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{sy:.1f}" text-anchor="middle" font-size="{sub_size}" '
            f'fill="{sub_color}">{subtitle}</text>'
        )
    else:
        ty = y + h * 0.56
        parts.append(
            f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="{title_size}" '
            f'font-weight="700" fill="{title_color}">{title}</text>'
        )
    return "\n    ".join(parts)


def fig_multimodal_pipeline() -> str:
    """Figure 1: Three architectural bridges from pixels to language models."""
    parts = [
        # Shared pixel input + caption input on the left
        box(70, 315, 200, 140, "Image", "H×W×C", "#F3EEE3", "#4B5558", "#1F2A2E", "#5A554E", 26, 21),
        box(70, 495, 200, 100, "Caption y", "Text pairs", "#ECF2EB", "#4B6B46", "#344E30", "#364635", 24, 20),

        # Row 1: ViT (pp. 9-11)
        draw_arrow(270, 355, 365, 225, "#356482", 3.2),
        box(370, 165, 300, 120, "Patch + Project", "N×D embeddings", "#EBF1F5", "#356482", "#23475E", "#33434A"),
        draw_arrow(670, 225, 745, 225, "#356482", 3.2),
        box(750, 165, 290, 120, "ViT Encoder", "Transformer", "#EBF1F5", "#356482", "#23475E", "#33434A"),
        draw_arrow(1040, 225, 1115, 225, "#356482", 3.2),
        box(1120, 165, 405, 120, "Class Logits", "Supervised labels", "#EBF1F5", "#356482", "#23475E", "#33434A"),

        # Row 2: CLIP (pp. 20-24) — image -> Image Encoder, caption -> Text Encoder
        draw_arrow(270, 405, 365, 405, "#4B6B46", 3.2),
        draw_arrow(270, 545, 365, 520, "#4B6B46", 3.2),
        box(370, 360, 300, 88, "Image Encoder", "f_I(x)", "#ECF2EB", "#4B6B46", "#344E30", "#364635", 24, 20),
        box(370, 474, 300, 88, "Text Encoder", "f_T(y)", "#ECF2EB", "#4B6B46", "#344E30", "#364635", 24, 20),
        draw_arrow(670, 404, 745, 444, "#4B6B46", 3.0),
        draw_arrow(670, 518, 745, 478, "#4B6B46", 3.0),
        box(750, 400, 290, 122, "Cosine Matrix", "B×B batch scores", "#ECF2EB", "#4B6B46", "#344E30", "#364635"),
        draw_arrow(1040, 461, 1115, 461, "#4B6B46", 3.2),
        box(1120, 400, 405, 122, "Symmetric InfoNCE", "Mean row + col CE", "#ECF2EB", "#4B6B46", "#344E30", "#364635"),

        # Row 3: LLaVA / Molmo (pp. 30-35)
        draw_arrow(270, 435, 365, 695, "#A87919", 3.2),
        box(370, 635, 300, 120, "CLIP ViT", "Patch tokens", "#F6F0E1", "#A87919", "#7A5710", "#473E2C"),
        draw_arrow(670, 695, 745, 695, "#A87919", 3.2),
        box(750, 635, 290, 120, "Connector W", "LLM dimension", "#F6F0E1", "#A87919", "#7A5710", "#473E2C"),
        draw_arrow(1040, 695, 1115, 695, "#B5493A", 3.2),
        box(1120, 635, 405, 120, "Language Model", "Text loss only", "#FAECE9", "#B5493A", "#7A2D22", "#52322D"),
    ]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="70" y="96" font-size="44" font-weight="700" fill="#1F2A2E">Three Bridges From Pixels to Language Models</text>
    {"".join(parts)}
  </g>
</svg>
"""


def draw_grid(x0: float, y0: float, size: float, n: int, stroke: str, fill: str) -> str:
    """Draw an n x n patch grid."""
    cell = size / n
    elems = [f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{size:.1f}" height="{size:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="2.5" />']
    for i in range(1, n):
        xi = x0 + i * cell
        yi = y0 + i * cell
        elems.append(f'<line x1="{xi:.1f}" y1="{y0:.1f}" x2="{xi:.1f}" y2="{y0 + size:.1f}" stroke="{stroke}" stroke-width="1.3" opacity="0.7" />')
        elems.append(f'<line x1="{x0:.1f}" y1="{yi:.1f}" x2="{x0 + size:.1f}" y2="{yi:.1f}" stroke="{stroke}" stroke-width="1.3" opacity="0.7" />')
    return "\n    ".join(elems)


def fig_patch_token_budget() -> str:
    """Figure 2: How patch size, 2x2 pooling, and crops govern visual token count."""
    parts = [
        # Column 1: Slide p. 10 worked example (3x3 = 9)
        '<text x="235" y="195" text-anchor="middle" font-size="26" font-weight="700" fill="#23475E">Slide Example</text>',
        '<text x="235" y="232" text-anchor="middle" font-size="22" fill="#4B5558">120×120, P=40</text>',
        draw_grid(125, 265, 220, 3, "#356482", "#EBF1F5"),
        draw_arrow(235, 495, 235, 570, "#356482", 3.0),
        box(95, 575, 280, 126, "9 patch tokens", "9×1024", "#EBF1F5", "#356482", "#23475E", "#33434A"),

        # Column 2: ViT-B/16 code example p. 17 (14x14 = 196 + 1 CLS)
        '<text x="610" y="195" text-anchor="middle" font-size="26" font-weight="700" fill="#23475E">ViT-B/16 Code</text>',
        '<text x="610" y="232" text-anchor="middle" font-size="22" fill="#4B5558">224×224, P=16</text>',
        draw_grid(500, 265, 220, 14, "#356482", "#EBF1F5"),
        draw_arrow(610, 495, 610, 570, "#356482", 3.0),
        box(460, 575, 300, 126, "197 tokens", "196 patches + CLS", "#EBF1F5", "#356482", "#23475E", "#33434A"),

        # Divider
        '<line x1="815" y1="180" x2="815" y2="755" stroke="#DDD5C7" stroke-width="2" />',

        # Column 3: Molmo single view 24x24 -> 12x12 (p. 35)
        '<text x="1030" y="195" text-anchor="middle" font-size="26" font-weight="700" fill="#7A5710">Molmo View</text>',
        '<text x="1030" y="232" text-anchor="middle" font-size="22" fill="#4B5558">336×336, P=14</text>',
        draw_grid(920, 265, 220, 24, "#A87919", "#F6F0E1"),
        draw_arrow(1030, 495, 1030, 570, "#A87919", 3.0),
        box(880, 575, 300, 126, "144 per view", "576 → 2×2 pool", "#F6F0E1", "#A87919", "#7A5710", "#473E2C"),

        # Column 4: Molmo multi-crop total (1 + 12 crops)
        draw_arrow(1185, 638, 1245, 638, "#4B6B46", 3.2),
        '<text x="1390" y="195" text-anchor="middle" font-size="26" font-weight="700" fill="#344E30">Pooled Grid ×13</text>',
        '<text x="1390" y="232" text-anchor="middle" font-size="22" fill="#4B5558">1 full + 12 crops</text>',
        draw_grid(1280, 265, 220, 12, "#4B6B46", "#ECF2EB"),
        draw_arrow(1390, 495, 1390, 570, "#4B6B46", 3.0),
        box(1250, 575, 280, 126, "1,872 vectors", "Before markers", "#ECF2EB", "#4B6B46", "#344E30", "#364635"),
    ]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="85" y="96" font-size="44" font-weight="700" fill="#1F2A2E">Patch Size and Cropping Control Visual Tokens</text>
    {"".join(parts)}
  </g>
</svg>
"""


def fig_clip_zero_shot_spread() -> str:
    """Figure 3: Diverging bars from slide p. 26 (Zero-Shot CLIP vs ResNet-50 Linear Probe)."""
    rows = [
        ("StanfordCars", +28.9),
        ("Country211", +23.2),
        ("Food101", +22.5),
        ("SST2", +12.4),
        ("ImageNet", +1.9),
        ("MNIST", -10.0),
        ("CLEVRCounts", -18.2),
        ("PatchCamelyon", -19.5),
        ("KITTI Distance", -34.0),
        ("EuroSAT", -37.1),
    ]
    zero_x = 820.0
    scale = 12.0  # 40 -> 480px
    top_y = 175.0
    row_h = 56.0
    bar_h = 34.0

    elems = []
    for tick in (-40, -20, 0, 20, 40):
        tx = zero_x + tick * scale
        stroke = "#4B5558" if tick == 0 else "#DDD5C7"
        sw = "2.6" if tick == 0 else "1.4"
        elems.append(f'<line x1="{tx:.1f}" y1="160" x2="{tx:.1f}" y2="748" stroke="{stroke}" stroke-width="{sw}" />')
        label = f"+{tick}" if tick > 0 else f"{tick}"
        elems.append(f'<text x="{tx:.1f}" y="784" text-anchor="middle" font-size="22" fill="#5A554E">{label}</text>')

    for idx, (name, val) in enumerate(rows):
        cy = top_y + idx * row_h
        by = cy + (row_h - bar_h) / 2.0
        bw = abs(val) * scale
        if val >= 0:
            bx = zero_x
            fill = "#4B6B46"
            val_x = zero_x + bw + 14.0
            anchor = "start"
            txt = f"+{val:.1f}"
            name_x = zero_x - 18.0
            name_anchor = "end"
        else:
            bx = zero_x - bw
            fill = "#B5493A"
            val_x = bx - 14.0
            anchor = "end"
            txt = f"{val:.1f}"
            name_x = zero_x + 18.0
            name_anchor = "start"

        elems.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bar_h:.1f}" rx="5" fill="{fill}" />')
        elems.append(
            f'<text x="{name_x:.1f}" y="{cy + 36:.1f}" text-anchor="{name_anchor}" font-size="24" '
            f'font-weight="600" fill="#1F2A2E">{name}</text>'
        )
        elems.append(
            f'<text x="{val_x:.1f}" y="{cy + 36:.1f}" text-anchor="{anchor}" font-size="22" '
            f'font-weight="700" fill="{fill}">{txt}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="85" y="96" font-size="44" font-weight="700" fill="#1F2A2E">Zero-Shot CLIP vs. ResNet-50 Linear Probe</text>
    {"".join(elems)}
    <text x="820" y="846" text-anchor="middle" font-size="23" font-weight="600" fill="#4B5558">CLIP minus ResNet-50 linear probe (percentage points)</text>
  </g>
</svg>
"""


def count_svg_words(svg_str: str) -> int:
    root = ET.fromstring(svg_str)
    texts = [
        " ".join("".join(el.itertext()).split())
        for el in root.iter()
        if el.tag.endswith("}text") or el.tag == "text"
    ]
    return sum(len(t.split()) for t in texts)


def rasterize_svg(svg_str: str, png_path: Path) -> None:
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
* {{ margin: 0; padding: 0; border: 0; box-sizing: border-box; }}
html, body {{ width: 1600px; height: 900px; overflow: hidden; background: #FAF6EE; }}
svg {{ display: block; width: 1600px; height: 900px; }}
</style>
</head>
<body>{svg_str}</body>
</html>
"""
    with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
        html_path = Path(tmp) / "fig.html"
        prof_dir = Path(tmp) / "profile"
        prof_dir.mkdir()
        html_path.write_text(html, encoding="utf-8")
        subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                f"--user-data-dir={prof_dir}",
                "--force-device-scale-factor=1",
                "--window-size=1600,900",
                f"--screenshot={png_path}",
                f"file://{html_path}",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


def png_dimensions(png_path: Path) -> tuple[int, int]:
    data = png_path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"Not PNG: {png_path}"
    return struct.unpack(">II", data[16:24])


def main() -> None:
    specs = [
        ("multimodal-pipeline", fig_multimodal_pipeline()),
        ("vit-patch-tokens", fig_patch_token_budget()),
        ("clip-zero-shot-spread", fig_clip_zero_shot_spread()),
    ]
    word_counts = {}
    for name, svg_str in specs:
        words = count_svg_words(svg_str)
        assert words <= 60, f"{name} exceeds 60 words: {words}"
        svg_path = OUT_DIR / f"{name}.svg"
        png_path = OUT_DIR / f"{name}.png"
        svg_path.write_text(svg_str, encoding="utf-8")
        rasterize_svg(svg_str, png_path)
        w, h = png_dimensions(png_path)
        assert (w, h) == (1600, 900), f"{name} unexpected PNG size {w}x{h}"
        word_counts[name] = words
        print(f"{name}: words={words} size={w}x{h}")

    manifest = {
        "lecture": "CMU 11-711 Advanced NLP (Fall 2025) — Lecture 11: Multimodal Modeling I",
        "version": "v1 r2",
        "figures": [f"{name}.png" for name, _ in specs],
        "svg_word_counts": word_counts,
        "verified_math": {
            "vit_slide_p10": {"H": 120, "W": 120, "C": 3, "P": 40, "N": 9, "patch_dim": 4800, "D": 1024},
            "vit_code_p17": {"H": 224, "W": 224, "C": 3, "P": 16, "N": 196, "tokens_with_cls": 197, "D": 768, "heads": 12, "head_dim": 64},
            "clip_code_p28": {"cat_logit": 18.904, "dog_logit": 11.716, "p_cat_pct": 99.9245, "p_dog_pct": 0.0755},
            "clip_constructed_2x2": {
                "batch_size": 2,
                "diag_cos": 0.8,
                "off_cos": 0.2,
                "scale": 2.0,
                "p_pos": 0.768525,
                "batch_mean_symmetric_ce_loss": 0.263282,
                "grad_pos": -0.115738,
                "grad_neg": 0.115738,
            },
            "molmo_p35": {
                "grid": 24,
                "raw_patches": 576,
                "pooled_grid": 12,
                "tokens_per_view": 144,
                "views": 13,
                "tokens_before_markers": 1872,
            },
        },
        "palette": PALETTE,
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
