#!/usr/bin/env python3
"""Generate low-text 1600x900 SVG/PNG figures for CMU DLSys Lecture 22."""

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


def arrow_polygon(tip_x: float, tip_y: float, dx: float, dy: float, length: float = 16.0, half_w: float = 7.0) -> str:
    """Return explicit <polygon> points for an arrowhead pointing along (dx, dy) ending at (tip_x, tip_y)."""
    norm = math.hypot(dx, dy)
    ux, uy = dx / norm, dy / norm
    px, py = -uy, ux
    bx, by = tip_x - length * ux, tip_y - length * uy
    p1 = (bx + half_w * px, by + half_w * py)
    p2 = (bx - half_w * px, by - half_w * py)
    return f"{tip_x:.1f},{tip_y:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"


def draw_arrow(x1: float, y1: float, x2: float, y2: float, color: str = "#4B5558", width: float = 3.0) -> str:
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


def box(x: float, y: float, w: float, h: float, title: str, subtitle: str = "", fill: str = "#F3EEE3",
        stroke: str = "#7A7367", title_color: str = "#1F2A2E", sub_color: str = "#4B5558",
        title_size: int = 26, sub_size: int = 20, rx: int = 14) -> str:
    """Render a centered rounded box with 1-line title and optional 1-line subtitle."""
    cx = x + w / 2.0
    parts = [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2.2" />'
    ]
    if subtitle:
        ty = y + h * 0.43
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


def fig_intervention_map() -> str:
    """Figure 1: Three attachment interfaces along one frozen forward pass."""
    backbone = "\n    ".join([
        box(90, 430, 195, 110, "Inputs", "", "#F3EEE3", "#8C857B", "#1F2A2E", title_size=26),
        box(345, 430, 240, 110, "Embeddings", "", "#EBF1F5", "#356482", "#23475E", title_size=26),
        box(645, 418, 320, 134, "Frozen Backbone", "Locked weights", "#F3EEE3", "#4B5558", "#1F2A2E", "#5A554E", title_size=26, sub_size=20),
        box(1025, 430, 220, 110, "Logits", "", "#FAECE9", "#B5493A", "#7A2D22", title_size=26),
        box(1305, 430, 205, 110, "Output", "", "#F3EEE3", "#8C857B", "#1F2A2E", title_size=26),
        draw_arrow(285, 485, 343, 485, "#4B5558"),
        draw_arrow(585, 485, 643, 485, "#4B5558"),
        draw_arrow(965, 485, 1023, 485, "#4B5558"),
        draw_arrow(1245, 485, 1303, 485, "#4B5558"),
    ])

    top_cards = "\n    ".join([
        box(270, 195, 390, 134, "CLIP / Visual Tokens", "Condition denoiser or LLM sequence", "#EBF1F5", "#356482", "#23475E", "#33434A", title_size=26, sub_size=20),
        draw_arrow(465, 329, 465, 426, "#356482", 3.2),
        box(940, 195, 390, 134, "XGrammar Mask", "Constrain output grammar", "#FAECE9", "#B5493A", "#7A2D22", "#52322D", title_size=26, sub_size=20),
        draw_arrow(1135, 329, 1135, 426, "#B5493A", 3.2),
    ])

    bottom_cards = "\n    ".join([
        box(410, 640, 360, 134, "ControlNet", "Trainable zero-conv branch", "#ECF2EB", "#4B6B46", "#344E30", "#364635", title_size=26, sub_size=20),
        draw_arrow(670, 640, 745, 556, "#4B6B46", 3.2),
        box(840, 640, 360, 134, "LoRA (W + BA)", "Low-rank adapter branch", "#F6F0E1", "#A87919", "#7A5710", "#473E2C", title_size=26, sub_size=20),
        draw_arrow(940, 640, 865, 556, "#A87919", 3.2),
    ])

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="90" y="92" font-size="44" font-weight="700" fill="#1F2A2E">Where to Customize a Frozen Pretrained Model</text>
    {backbone}
    {top_cards}
    {bottom_cards}
    <text x="90" y="854" font-size="18" fill="#6B655B">Three attachment interfaces along a frozen forward pass (pp. 6–21).</text>
  </g>
</svg>
"""


def fig_zero_init_branches() -> str:
    """Figure 2: Zero-initialized residual branches in ControlNet (p. 10) and LoRA (p. 16 + Hu et al.)."""
    # Left zone: ControlNet (x=90..750)
    left_parts = [
        '<text x="90" y="182" font-size="28" font-weight="700" fill="#1F2A2E">ControlNet (p. 10)</text>',
        box(120, 320, 90, 56, "x", "", "#F3EEE3", "#4B5558", title_size=24),
        draw_arrow(165, 376, 165, 456, "#4B5558"),
        box(75, 460, 180, 110, "Locked Block", "", "#EBF1F5", "#356482", "#23475E", title_size=24),
        draw_arrow(165, 570, 165, 672, "#4B5558"),

        # Control condition branch
        box(450, 210, 90, 50, "c", "", "#ECF2EB", "#4B6B46", "#344E30", title_size=24),
        draw_arrow(495, 260, 495, 296, "#4B6B46", 3.0),
        box(385, 300, 220, 58, "0-conv", "", "#ECF2EB", "#4B6B46", "#344E30", title_size=24),
        draw_arrow(495, 358, 495, 394, "#4B6B46", 3.0),
        '<circle cx="495" cy="416" r="18" fill="#FAF6EE" stroke="#4B6B46" stroke-width="2.5" />',
        '<text x="495" y="424" text-anchor="middle" font-size="24" font-weight="700" fill="#344E30">+</text>',
        '<polyline points="210,348 330,348 330,416 463,416" fill="none" stroke="#356482" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" />',
        f'<polygon points="{arrow_polygon(475, 416, 1.0, 0.0)}" fill="#356482" />',
        draw_arrow(495, 434, 495, 480, "#4B6B46", 3.0),
        box(365, 484, 260, 64, "Trainable Copy", "", "#EBF1F5", "#356482", "#23475E", title_size=22),
        draw_arrow(495, 548, 495, 594, "#4B6B46", 3.0),
        box(385, 598, 220, 58, "0-conv", "", "#ECF2EB", "#4B6B46", "#344E30", title_size=24),

        # Merge at bottom + node
        '<circle cx="165" cy="696" r="20" fill="#FAF6EE" stroke="#4B5558" stroke-width="2.5" />',
        '<text x="165" y="704" text-anchor="middle" font-size="26" font-weight="700" fill="#1F2A2E">+</text>',
        draw_arrow(385, 636, 187, 691, "#4B6B46", 3.0),
        draw_arrow(165, 716, 165, 772, "#4B5558", 3.0),
        '<text x="194" y="766" font-size="24" font-weight="700" fill="#1F2A2E">y_c = F(x)</text>',
    ]

    # Right zone: LoRA (x=865..1510)
    right_parts = [
        '<text x="865" y="182" font-size="28" font-weight="700" fill="#1F2A2E">LoRA (p. 16)</text>',
        box(1000, 320, 90, 56, "X", "", "#F3EEE3", "#4B5558", title_size=24),
        draw_arrow(1045, 376, 1045, 456, "#4B5558"),
        box(955, 460, 180, 110, "Frozen W", "", "#F3EEE3", "#4B5558", "#1F2A2E", title_size=24),
        draw_arrow(1045, 570, 1045, 672, "#4B5558"),

        # Parallel branch: A -> B (init B=0 per Hu et al.)
        draw_arrow(1090, 348, 1345, 402, "#A87919", 2.8),
        box(1235, 406, 265, 86, "A (r×d_in)", "", "#F6F0E1", "#A87919", "#7A5710", title_size=23),
        draw_arrow(1367.5, 492, 1367.5, 550, "#A87919", 3.0),
        box(1235, 554, 265, 92, "B (d_out×r, B=0)", "", "#F6F0E1", "#A87919", "#7A5710", title_size=23),

        # Merge + node
        '<circle cx="1045" cy="696" r="20" fill="#FAF6EE" stroke="#4B5558" stroke-width="2.5" />',
        '<text x="1045" y="704" text-anchor="middle" font-size="26" font-weight="700" fill="#1F2A2E">+</text>',
        draw_arrow(1235, 610, 1067, 691, "#A87919", 3.0),
        draw_arrow(1045, 716, 1045, 772, "#4B5558", 3.0),
        '<text x="1074" y="766" font-size="24" font-weight="700" fill="#1F2A2E">Y = WX</text>',
    ]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="90" y="92" font-size="44" font-weight="700" fill="#1F2A2E">Zero-Initialized Branches Preserve Step-0 Output</text>
    {"".join(left_parts)}
    <line x1="800" y1="165" x2="800" y2="775" stroke="#DDD5C7" stroke-width="1.5" />
    {"".join(right_parts)}
    <text x="90" y="854" font-size="18" fill="#6B655B">Step-0 output matches pretrained weights; outer 0-conv and LoRA B learn first (pp. 10, 16; Hu et al.).</text>
  </g>
</svg>
"""


def fig_xgrammar_split() -> str:
    """Figure 3: Two-branch XGrammar token masking flow without distorted bar widths."""
    nodes = "\n    ".join([
        box(580, 175, 440, 108, "PDA Stack Top State", "Current grammar node", "#F3EEE3", "#4B5558", "#1F2A2E", "#5A554E", title_size=26, sub_size=20),
        draw_arrow(700, 283, 470, 382, "#356482", 3.2),
        draw_arrow(900, 283, 1130, 382, "#B5493A", 3.2),
        box(140, 386, 620, 160, "&gt;99% Context-Independent", "Precomputed mask cache (accepted / rejected)", "#EBF1F5", "#356482", "#23475E", "#33434A", title_size=28, sub_size=20),
        box(840, 386, 620, 160, "&lt;1% Context-Dependent", "Runtime check against deeper stack", "#FAECE9", "#B5493A", "#7A2D22", "#52322D", title_size=28, sub_size=20),
        draw_arrow(450, 546, 690, 646, "#356482", 3.2),
        draw_arrow(1150, 546, 910, 646, "#B5493A", 3.2),
        box(460, 650, 680, 120, "Mask Applied to Logits", "Valid grammar tokens only", "#ECF2EB", "#4B6B46", "#344E30", "#364635", title_size=28, sub_size=20),
    ])

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="90" y="92" font-size="44" font-weight="700" fill="#1F2A2E">XGrammar Splits Token Masking into Two Paths</text>
    {nodes}
    <text x="90" y="854" font-size="18" fill="#6B655B">Slide-reported &gt;99% / &lt;1% token split (CMU DLSys Lecture 22, pp. 19–21).</text>
  </g>
</svg>
"""


def count_svg_words(svg_str: str) -> int:
    root = ET.fromstring(svg_str)
    texts = [" ".join("".join(el.itertext()).split()) for el in root.iter() if el.tag.endswith("}text") or el.tag == "text"]
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
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "fig.html"
        html_path.write_text(html, encoding="utf-8")
        subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
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
        ("intervention-map", fig_intervention_map()),
        ("zero-init-branches", fig_zero_init_branches()),
        ("xgrammar-split", fig_xgrammar_split()),
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
        "lecture": "CMU 10-414/714 Deep Learning Systems — Lecture 22: Customizing Pretrained Models",
        "version": "v1 r3",
        "figures": [f"{name}.png" for name, _ in specs],
        "svg_word_counts": word_counts,
        "verified_math": {
            "controlnet_scalar_check": {
                "f_u": "u + 1",
                "x": 2.0,
                "c": 5.0,
                "yc_step0": 3.0,
                "grad_wz2_step0": 3.0,
                "eta": 0.1,
                "wz2_step1": -0.3,
                "grad_wz1_step1": -1.5,
            },
            "lora_example_full_params": 4096 * 4096,
            "lora_example_rank": 16,
            "lora_example_adapter_params": 2 * 4096 * 16,
            "lora_example_ratio_pct": round((2 * 4096 * 16) / (4096 * 4096) * 100, 3),
            "xgrammar_example_vocab": 128000,
            "xgrammar_example_outlier_exclusive_bound": 1280,
            "xgrammar_example_outlier_max_inclusive": 1279,
            "xgrammar_example_bitmask_kib": round(128000 / 8 / 1024, 3),
        },
        "palette": PALETTE,
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
