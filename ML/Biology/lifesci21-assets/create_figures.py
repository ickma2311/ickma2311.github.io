#!/usr/bin/env python3
"""Generate low-text 1600x900 SVG/PNG figures for MIT 6.874 Lecture 21 (v1 r6)."""

from pathlib import Path
import base64
import io
import json
import math
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image
from pypdf import PdfReader

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
    width: float = 3.2,
    dashed: bool = False,
) -> str:
    """Draw a straight line ending with an explicit <polygon> arrowhead at (x2, y2)."""
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy)
    ux, uy = dx / norm, dy / norm
    lx2, ly2 = x2 - 12.0 * ux, y2 - 12.0 * uy
    dash_attr = ' stroke-dasharray="9,7"' if dashed else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{lx2:.1f}" y2="{ly2:.1f}" '
        f'stroke="{color}" stroke-width="{width:.1f}" stroke-linecap="round"{dash_attr} />'
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
    rx: int = 16,
) -> str:
    """Render a centered rounded box with 1-line title and optional 1-line subtitle."""
    cx = x + w / 2.0
    parts = [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2.4" />'
    ]
    if subtitle:
        ty = y + h * 0.42
        sy = y + h * 0.72
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


def _load_lecture_image_b64(
    page_num: int,
    image_name: str,
    crop_box: tuple[int, int, int, int] | None = None,
) -> str:
    """Extract an embedded image from l21.pdf and encode as a base64 PNG URI."""
    pdf_path = OUT_DIR.parents[2] / "output" / "lifesci21" / "sources" / "l21.pdf"
    reader = PdfReader(str(pdf_path))
    page = reader.pages[page_num - 1]
    for img in page.images:
        if img.name == image_name:
            pil = Image.open(io.BytesIO(img.data)).convert("RGB")
            if crop_box is not None:
                pil = pil.crop(crop_box)
            buf = io.BytesIO()
            pil.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return f"data:image/png;base64,{b64}"
    raise FileNotFoundError(f"Image {image_name} not found on page {page_num} of {pdf_path}")


def fig_cell_profiling_pipeline() -> str:
    """Figure 1: Visually rich 4-stage conceptual synthesis with real DSB & lecture microscopy."""
    raw_uri = _load_lecture_image_b64(12, "Image48.jp2")
    mask_uri = _load_lecture_image_b64(12, "Image49.jp2")
    crop1_uri = _load_lecture_image_b64(25, "Image187.jpg", (16, 16, 82, 82))
    crop2_uri = _load_lecture_image_b64(25, "Image191.jpg", (16, 16, 82, 82))

    # Panel 1: Real DSB raw fluorescence nuclei (x=75, y=270, w=264, h=224)
    raw_elems = [
        '<defs>'
        '<clipPath id="clip-raw"><rect x="75" y="270" width="264" height="224" rx="12" /></clipPath>'
        '<clipPath id="clip-mask"><rect x="435" y="270" width="264" height="224" rx="12" /></clipPath>'
        '<clipPath id="clip-c1"><rect x="812" y="308" width="54" height="54" rx="6" /></clipPath>'
        '<clipPath id="clip-c2"><rect x="812" y="402" width="54" height="54" rx="6" /></clipPath>'
        '</defs>',
        f'<image href="{raw_uri}" x="75" y="270" width="264" height="224" preserveAspectRatio="xMidYMid slice" clip-path="url(#clip-raw)" />',
        '<rect x="75" y="270" width="264" height="224" rx="12" fill="none" stroke="#6B655B" stroke-width="2.4" />',
    ]

    # Panel 2: Real DSB color-coded manual reference masks (x=435, y=270, w=264, h=224)
    seg_elems = [
        f'<image href="{mask_uri}" x="435" y="270" width="264" height="224" preserveAspectRatio="xMidYMid slice" clip-path="url(#clip-mask)" />',
        '<rect x="435" y="270" width="264" height="224" rx="12" fill="none" stroke="#356482" stroke-width="2.6" />',
    ]

    # Panel 3: Two separate Slide 25 EGFR cell crops -> CNN encoder -> embedding h -> y and connected GRL -> d
    cnn_elems = [
        '<rect x="800" y="270" width="324" height="224" rx="14" fill="#F3EEE3" stroke="#4B6B46" stroke-width="2.4" />',
        f'<image href="{crop1_uri}" x="812" y="308" width="54" height="54" preserveAspectRatio="xMidYMid slice" clip-path="url(#clip-c1)" />',
        '<rect x="812" y="308" width="54" height="54" rx="6" fill="none" stroke="#356482" stroke-width="2.0" />',
        f'<image href="{crop2_uri}" x="812" y="402" width="54" height="54" preserveAspectRatio="xMidYMid slice" clip-path="url(#clip-c2)" />',
        '<rect x="812" y="402" width="54" height="54" rx="6" fill="none" stroke="#356482" stroke-width="2.0" />',
        draw_arrow(868, 335, 892, 368, "#356482", 2.4),
        draw_arrow(868, 429, 892, 398, "#356482", 2.4),
        '<rect x="894" y="324" width="14" height="116" rx="4" fill="#DCE7EE" stroke="#356482" stroke-width="2.0" />',
        '<rect x="916" y="338" width="14" height="88" rx="4" fill="#C4D8E4" stroke="#356482" stroke-width="2.0" />',
        '<rect x="938" y="352" width="14" height="60" rx="4" fill="#A9C6D8" stroke="#356482" stroke-width="2.0" />',
        '<rect x="962" y="358" width="14" height="48" rx="4" fill="#356482" />',
        '<text x="969" y="427" text-anchor="middle" font-size="18" font-weight="700" fill="#23475E">h</text>',
        # Upper forward path: h -> y
        draw_arrow(978, 372, 1054, 328, "#4B6B46", 2.6),
        '<rect x="1058" y="302" width="52" height="44" rx="8" fill="#ECF2EB" stroke="#4B6B46" stroke-width="2.2" />',
        '<text x="1084" y="331" text-anchor="middle" font-size="22" font-weight="700" fill="#344E30">y</text>',
        # Lower forward path: h -> GRL -> d, plus backward -lambda gradient arrow
        draw_arrow(978, 394, 1002, 434, "#A87919", 2.4),
        '<rect x="1002" y="434" width="46" height="32" rx="6" fill="#F6F0E1" stroke="#A87919" stroke-width="1.8" />',
        '<text x="1025" y="456" text-anchor="middle" font-size="18" font-weight="700" fill="#7A5710">GRL</text>',
        draw_arrow(1048, 450, 1068, 450, "#B5493A", 2.4),
        '<rect x="1070" y="428" width="40" height="44" rx="8" fill="#FAECE9" stroke="#B5493A" stroke-width="2.2" />',
        '<text x="1090" y="457" text-anchor="middle" font-size="22" font-weight="700" fill="#7A2D22">d</text>',
        draw_arrow(1000, 464, 962, 444, "#B5493A", 2.2, dashed=True),
        '<text x="976" y="480" text-anchor="middle" font-size="18" font-weight="700" fill="#7A2D22">−λ</text>',
    ]

    # Panel 4: Barcode Profiles + Exact 4-Leaf Dendrogram + 4x4 Similarity Matrix (x=1220, y=270, w=290, h=224)
    prof_elems = [
        '<rect x="1220" y="270" width="290" height="224" rx="14" fill="#F3EEE3" stroke="#A87919" stroke-width="2.4" />',
    ]
    stripe_pal = ["#356482", "#B5493A", "#A87919", "#4B6B46", "#D9D2C5"]
    patterns = [
        [0, 4, 1, 0, 2, 4, 0, 1, 3, 4, 0, 2, 1, 4, 0, 3],
        [3, 2, 4, 3, 0, 4, 3, 2, 4, 1, 3, 0, 4, 3, 2, 4],
        [1, 1, 4, 2, 1, 0, 4, 1, 2, 4, 1, 3, 1, 4, 2, 0],
    ]
    for r, pat in enumerate(patterns):
        sy = 286 + r * 22
        for c, pid in enumerate(pat):
            sx = 1246 + c * 15.0
            prof_elems.append(f'<rect x="{sx:.1f}" y="{sy}" width="13.0" height="15" rx="2" fill="{stripe_pal[pid]}" />')
    # 4-leaf dendrogram aligned exactly to column centers: 1315.5, 1347.5, 1379.5, 1411.5
    prof_elems.append(
        '<path d="M1315.5 378 V367 H1347.5 V378 '
        'M1379.5 378 V367 H1411.5 V378 '
        'M1331.5 367 V357 H1395.5 V367" '
        'fill="none" stroke="#6B655B" stroke-width="2.0" />'
    )
    sim = [
        ["#B5493A", "#D8897C", "#C5D5DF", "#82A3B8"],
        ["#D8897C", "#B5493A", "#9AB6C8", "#7498B0"],
        ["#C5D5DF", "#9AB6C8", "#B5493A", "#DC9B8F"],
        ["#82A3B8", "#7498B0", "#DC9B8F", "#B5493A"],
    ]
    for r in range(4):
        for c in range(4):
            mx = 1301 + c * 32
            my = 382 + r * 24
            prof_elems.append(f'<rect x="{mx}" y="{my}" width="29" height="21" rx="3" fill="{sim[r][c]}" />')

    parts = [
        '<text x="207" y="206" text-anchor="middle" font-size="26" font-weight="700" fill="#1F2A2E">1. Raw Images</text>',
        '<text x="207" y="242" text-anchor="middle" font-size="21" fill="#5A554E">DSB fluorescence</text>',

        '<text x="567" y="206" text-anchor="middle" font-size="26" font-weight="700" fill="#23475E">2. Cell Segmentation</text>',
        '<text x="567" y="242" text-anchor="middle" font-size="21" fill="#33434A">Reference masks</text>',

        '<text x="962" y="206" text-anchor="middle" font-size="26" font-weight="700" fill="#344E30">3. Single-Cell CNN</text>',
        '<text x="962" y="242" text-anchor="middle" font-size="21" fill="#364635">Treatment + opt. GRL</text>',

        '<text x="1365" y="206" text-anchor="middle" font-size="26" font-weight="700" fill="#7A5710">4. Profiles</text>',
        '<text x="1365" y="242" text-anchor="middle" font-size="21" fill="#473E2C">Mean &amp; similarity</text>',

        *raw_elems,
        draw_arrow(348, 382, 426, 382, "#356482", 3.4),
        *seg_elems,
        draw_arrow(708, 382, 792, 382, "#4B6B46", 3.4),
        *cnn_elems,
        draw_arrow(1132, 382, 1212, 382, "#A87919", 3.4),
        *prof_elems,

        '<line x1="435" y1="546" x2="699" y2="546" stroke="#356482" stroke-width="5" stroke-linecap="round" />',
        '<text x="567" y="594" text-anchor="middle" font-size="24" font-weight="700" fill="#23475E">Supervised</text>',
        '<text x="567" y="632" text-anchor="middle" font-size="21" fill="#4B5558">0.816 F1, 0 h</text>',

        '<line x1="800" y1="546" x2="1124" y2="546" stroke="#4B6B46" stroke-width="5" stroke-linecap="round" />',
        '<text x="962" y="594" text-anchor="middle" font-size="24" font-weight="700" fill="#344E30">Weakly Supervised</text>',
        '<text x="962" y="632" text-anchor="middle" font-size="21" fill="#4B5558">Penalize batch</text>',

        '<line x1="1220" y1="546" x2="1510" y2="546" stroke="#A87919" stroke-width="5" stroke-linecap="round" />',
        '<text x="1365" y="594" text-anchor="middle" font-size="24" font-weight="700" fill="#7A5710">Inference</text>',
        '<text x="1365" y="632" text-anchor="middle" font-size="21" fill="#4B5558">MOA &amp; variants</text>',

        '<text x="75" y="818" font-size="21" fill="#6B655B">DSB nuclei &amp; EGFR cell crops (Caicedo et al., 2017–2019)</text>',
    ]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="75" y="102" font-size="44" font-weight="700" fill="#1F2A2E">Two Deep-Learning Stages Turn Pixels Into Profiles</text>
    {"".join(parts)}
  </g>
</svg>
"""


def fig_dsb_modality_shift_accuracy() -> str:
    """Figure 2: Slide 15 Mean F1 @ 0.7 IoU vs configuration time across 4 workflows."""
    rows = [
        ("Top DSB model", 0.816, 0.0, "#356482"),
        ("CellProfiler Expert", 0.743, 3.0, "#A87919"),
        ("U-Net (Data scientist)", 0.620, 20.0, "#B5493A"),
        ("CellProfiler Novice", 0.616, 5.0, "#4B6B46"),
    ]
    top_y = 265.0
    row_step = 118.0
    bar_h = 48.0

    f1_x0 = 410.0
    f1_w = 480.0
    hr_x0 = 1020.0
    hr_w = 440.0
    hr_max = 22.0

    elems = [
        '<text x="650" y="218" text-anchor="middle" font-size="25" font-weight="700" fill="#1F2A2E">Mean Per-Image F1 @ 0.7 IoU</text>',
        '<text x="1240" y="218" text-anchor="middle" font-size="25" font-weight="700" fill="#1F2A2E">Configuration Time (hrs)</text>',
    ]

    for tick in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        tx = f1_x0 + tick * f1_w
        stroke = "#4B5558" if tick == 0.0 else "#DDD5C7"
        sw = "2.2" if tick == 0.0 else "1.4"
        elems.append(f'<line x1="{tx:.1f}" y1="242" x2="{tx:.1f}" y2="725" stroke="{stroke}" stroke-width="{sw}" />')
        elems.append(f'<text x="{tx:.1f}" y="762" text-anchor="middle" font-size="20" fill="#5A554E">{tick:.1f}</text>')

    for tick in (0, 5, 10, 15, 20):
        tx = hr_x0 + (tick / hr_max) * hr_w
        stroke = "#4B5558" if tick == 0 else "#DDD5C7"
        sw = "2.2" if tick == 0 else "1.4"
        elems.append(f'<line x1="{tx:.1f}" y1="242" x2="{tx:.1f}" y2="725" stroke="{stroke}" stroke-width="{sw}" />')
        elems.append(f'<text x="{tx:.1f}" y="762" text-anchor="middle" font-size="20" fill="#5A554E">{tick}</text>')

    for idx, (label, f1, hrs, color) in enumerate(rows):
        cy = top_y + idx * row_step
        by = cy
        elems.append(
            f'<text x="385" y="{cy + 32:.1f}" text-anchor="end" font-size="24" font-weight="700" fill="#1F2A2E">{label}</text>'
        )
        bw1 = f1 * f1_w
        elems.append(f'<rect x="{f1_x0:.1f}" y="{by:.1f}" width="{bw1:.1f}" height="{bar_h:.1f}" rx="7" fill="{color}" />')
        lbl1_x = f1_x0 + bw1 + 10.0
        elems.append(f'<rect x="{lbl1_x - 3:.1f}" y="{cy + 8:.1f}" width="66" height="32" rx="4" fill="#FAF6EE" />')
        elems.append(
            f'<text x="{lbl1_x + 2:.1f}" y="{cy + 32:.1f}" text-anchor="start" font-size="22" '
            f'font-weight="700" fill="{color}">{f1:.3f}</text>'
        )
        if hrs > 0:
            bw2 = (hrs / hr_max) * hr_w
            elems.append(f'<rect x="{hr_x0:.1f}" y="{by:.1f}" width="{bw2:.1f}" height="{bar_h:.1f}" rx="7" fill="{color}" opacity="0.88" />')
            lbl2_x = hr_x0 + bw2 + 10.0
            pill_w = 56 if hrs >= 10 else 44
            elems.append(f'<rect x="{lbl2_x - 3:.1f}" y="{cy + 8:.1f}" width="{pill_w}" height="32" rx="4" fill="#FAF6EE" />')
            elems.append(
                f'<text x="{lbl2_x + 2:.1f}" y="{cy + 32:.1f}" text-anchor="start" font-size="22" '
                f'font-weight="700" fill="{color}">{int(hrs)} h</text>'
            )
        else:
            lbl2_x = hr_x0 + 12.0
            elems.append(f'<rect x="{lbl2_x - 3:.1f}" y="{cy + 8:.1f}" width="44" height="32" rx="4" fill="#FAF6EE" />')
            elems.append(
                f'<text x="{lbl2_x + 2:.1f}" y="{cy + 32:.1f}" text-anchor="start" font-size="22" '
                f'font-weight="700" fill="{color}">0 h</text>'
            )

    elems.append(
        '<text x="75" y="838" font-size="21" fill="#6B655B">Stage 2 benchmark across 5 image groups (Caicedo et al., 2019)</text>'
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="75" y="102" font-size="44" font-weight="700" fill="#1F2A2E">The DSB Ensemble Outscored Group-Specific Workflows</text>
    {"".join(elems)}
  </g>
</svg>
"""


def fig_grl_batch_deconfounding() -> str:
    """Figure 3: Gradient Reversal Layer discouraging batch-predictive features."""
    parts = [
        box(75, 365, 225, 130, "Single-Cell Crop x", "Multi-channel patch", "#F3EEE3", "#6B655B", "#1F2A2E", "#5A554E", 23, 19),
        draw_arrow(300, 430, 385, 430, "#356482", 3.4),
        box(390, 365, 250, 130, "Encoder G_f", "Parameters θ_f", "#EBF1F5", "#356482", "#23475E", "#33434A", 25, 20),
        draw_arrow(640, 430, 725, 430, "#356482", 3.4),
        box(730, 365, 210, 130, "Embedding h", "Cell features", "#EBF1F5", "#356482", "#23475E", "#33434A", 25, 20),

        draw_arrow(940, 405, 1025, 265, "#4B6B46", 3.4),
        box(1030, 195, 240, 125, "Treatment Head", "G_y(h; θ_y)", "#ECF2EB", "#4B6B46", "#344E30", "#364635", 24, 20),
        draw_arrow(1270, 258, 1335, 258, "#4B6B46", 3.4),
        box(1340, 195, 190, 125, "Loss L_y", "Compound y", "#ECF2EB", "#4B6B46", "#344E30", "#364635", 24, 20),

        draw_arrow(940, 455, 1025, 595, "#A87919", 3.4),
        box(1030, 535, 165, 125, "GRL", "Backward × −λ", "#F6F0E1", "#A87919", "#7A5710", "#473E2C", 25, 19),
        draw_arrow(1195, 598, 1235, 598, "#B5493A", 3.4),
        box(1240, 535, 155, 125, "Batch Head", "G_d(h; θ_d)", "#FAECE9", "#B5493A", "#7A2D22", "#52322D", 23, 19),
        draw_arrow(1395, 598, 1435, 598, "#B5493A", 3.4),
        box(1440, 535, 110, 125, "Loss L_d", "Plate d", "#FAECE9", "#B5493A", "#7A2D22", "#52322D", 22, 19),

        draw_arrow(1030, 222, 645, 345, "#4B6B46", 3.2, dashed=True),
        '<text x="805" y="218" text-anchor="middle" font-size="22" font-weight="700" fill="#344E30">+∂L_y/∂θ_f (keep compound)</text>',

        draw_arrow(1030, 635, 645, 515, "#B5493A", 3.2, dashed=True),
        '<text x="805" y="670" text-anchor="middle" font-size="22" font-weight="700" fill="#7A2D22">−λ ∂L_d/∂θ_f (penalize batch)</text>',

        '<text x="75" y="835" font-size="21" fill="#6B655B">Adversarial domain adaptation during training</text>',
    ]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="75" y="102" font-size="42" font-weight="700" fill="#1F2A2E">Gradient Reversal Discourages Batch-Predictive Features</text>
    {"".join(parts)}
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


def compute_verified_math() -> dict:
    """Compute all reported sums and constructed worked checks directly from inputs."""
    train_shares = [80.6, 15.5, 0.6, 0.9, 2.4]
    test_shares = [67.9, 15.1, 4.7, 11.3, 0.9]

    iou_thresh = 0.7
    r_ratio = math.sqrt(iou_thresh)

    tp, fp, fn = 16, 3, 5
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * tp / (2 * tp + fp + fn)

    slide23_nodes = 13
    slide23_pairs = math.comb(slide23_nodes, 2)

    top_same, top_total = 6, 13
    rest_same, rest_total = 6, 65
    rate_ratio = (top_same / top_total) / (rest_same / rest_total)
    odds_ratio = (top_same / (top_total - top_same)) / (rest_same / (rest_total - rest_same))

    x, theta_f, w_y, w_d, y, d, lam = 2.0, 0.5, 1.0, 1.0, 2.0, 2.0, 0.5
    h = theta_f * x
    g_y_f = (w_y * h - y) * w_y * x
    g_d_f = (w_d * h - d) * w_d * x
    g_eff = g_y_f - lam * g_d_f

    return {
        "dsb_train_pct_sum": round(sum(train_shares), 1),
        "dsb_test_pct_sum": round(sum(test_shares), 1),
        "constructed_iou_0_7_concentric_radius_ratio": round(r_ratio, 4),
        "constructed_f1_check": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        },
        "slide23_reported_nodes_and_pairs": {
            "nodes": slide23_nodes,
            "pairwise_connections": slide23_pairs,
        },
        "constructed_enrichment_check": {
            "top_same": top_same,
            "top_total": top_total,
            "rest_same": rest_same,
            "rest_total": rest_total,
            "rate_ratio": round(rate_ratio, 4),
            "odds_ratio": round(odds_ratio, 4),
        },
        "constructed_grl_1d_check": {
            "x": x,
            "theta_f": theta_f,
            "w_y": w_y,
            "w_d": w_d,
            "y": y,
            "d": d,
            "lambda": lam,
            "g_y_f": round(g_y_f, 4),
            "g_d_f": round(g_d_f, 4),
            "g_eff": round(g_eff, 4),
        },
    }


def main() -> None:
    specs = [
        ("cell-profiling-pipeline", fig_cell_profiling_pipeline()),
        ("dsb-modality-shift-accuracy", fig_dsb_modality_shift_accuracy()),
        ("grl-batch-deconfounding", fig_grl_batch_deconfounding()),
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
        "lecture": "MIT 6.874 Deep Learning in the Life Sciences (Spring 2021) — Lecture 21: Image-Based Cell Phenotyping",
        "version": "v1 r6",
        "figures": [f"{name}.png" for name, _ in specs],
        "svg_word_counts": word_counts,
        "verified_math": compute_verified_math(),
        "palette": PALETTE,
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
