#!/usr/bin/env python3
"""Generate low-text 1600x900 SVG/PNG figures for CMU DLSys Lecture 23."""

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


def fig_deployment_compilation_stack() -> str:
    """Figure 1: Library-driven inference engines vs ML compilation."""
    top_lane = "\n    ".join([
        '<text x="90" y="210" font-size="24" font-weight="700" fill="#B5493A">Library-Driven Inference</text>',
        box(90, 238, 280, 128, "Trained Model", "Graph + weights", "#F3EEE3", "#8C857B", "#1F2A2E", "#5A554E", title_size=25, sub_size=20),
        draw_arrow(370, 302, 434, 302, "#B5493A", 3.2),
        box(438, 238, 300, 128, "Export Format", "ONNX, CoreML, TFLite", "#FAECE9", "#B5493A", "#7A2D22", "#52322D", title_size=25, sub_size=20),
        draw_arrow(738, 302, 802, 302, "#B5493A", 3.2),
        box(806, 238, 320, 128, "Backend Libraries", "TensorRT, ARMComputeLib", "#FAECE9", "#B5493A", "#7A2D22", "#52322D", title_size=25, sub_size=20),
        draw_arrow(1126, 302, 1190, 302, "#B5493A", 3.2),
        box(1194, 238, 316, 128, "Target Hardware", "CPU, GPU, Mobile", "#F3EEE3", "#8C857B", "#1F2A2E", "#5A554E", title_size=25, sub_size=20),
    ])

    bottom_lane = "\n    ".join([
        '<text x="90" y="510" font-size="24" font-weight="700" fill="#356482">ML Compilation</text>',
        box(90, 538, 280, 128, "Trained Model", "IRModule", "#F3EEE3", "#8C857B", "#1F2A2E", "#5A554E", title_size=25, sub_size=20),
        draw_arrow(370, 602, 434, 602, "#356482", 3.2),
        box(438, 538, 300, 128, "High-Level IR", "Graph fusion", "#EBF1F5", "#356482", "#23475E", "#33434A", title_size=25, sub_size=20),
        draw_arrow(738, 602, 802, 602, "#356482", 3.2),
        box(806, 538, 320, 128, "Loop IR Tuning", "Tiling, binding", "#ECF2EB", "#4B6B46", "#344E30", "#364635", title_size=25, sub_size=20),
        draw_arrow(1126, 602, 1190, 602, "#4B6B46", 3.2),
        box(1194, 538, 316, 128, "Direct Codegen", "CPU, GPU, Mobile", "#F6F0E1", "#A87919", "#7A5710", "#473E2C", title_size=25, sub_size=20),
    ])

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="90" y="96" font-size="44" font-weight="700" fill="#1F2A2E">Compilation Replaces Per-Backend Kernel Libraries</text>
    {top_lane}
    <line x1="90" y1="436" x2="1510" y2="436" stroke="#DDD5C7" stroke-width="1.6" />
    {bottom_lane}
    <text x="90" y="848" font-size="18" fill="#6B655B">Interpreters call libraries; compilers lower IR (pp. 7-11).</text>
  </g>
</svg>
"""


def fig_ir_lowering_fusion() -> str:
    """Figure 2: Lowering and fusing @dot-add removes intermediate buffer Z."""
    stages = "\n    ".join([
        box(90, 220, 410, 148, "High-Level IR", "dot(x,w) + b", "#EBF1F5", "#356482", "#23475E", "#33434A", title_size=28, sub_size=22),
        draw_arrow(500, 294, 588, 294, "#4B5558", 3.2),
        box(594, 220, 410, 148, "Unfused Loop IR", "3 nests; Y, Z", "#FAECE9", "#B5493A", "#7A2D22", "#52322D", title_size=28, sub_size=22),
        draw_arrow(1004, 294, 1092, 294, "#4B6B46", 3.2),
        box(1098, 220, 412, 148, "Fused Loop IR", "1 nest; Y only", "#ECF2EB", "#4B6B46", "#344E30", "#364635", title_size=28, sub_size=22),
    ])

    bars = "\n    ".join([
        '<text x="90" y="458" font-size="25" font-weight="700" fill="#1F2A2E">16x16 Buffers (float32)</text>',
        '<text x="90" y="532" font-size="22" font-weight="700" fill="#7A2D22">Unfused</text>',
        '<rect x="270" y="494" width="440" height="58" rx="10" fill="#FAECE9" stroke="#B5493A" stroke-width="2.2" />',
        '<text x="490" y="531" text-anchor="middle" font-size="21" font-weight="700" fill="#7A2D22">Y: 1,024 B</text>',
        '<rect x="722" y="494" width="440" height="58" rx="10" fill="#F6F0E1" stroke="#A87919" stroke-width="2.2" />',
        '<text x="942" y="531" text-anchor="middle" font-size="21" font-weight="700" fill="#7A5710">Z: 1,024 B</text>',
        '<text x="1192" y="531" font-size="21" font-weight="700" fill="#4B5558">2,048 B (3 passes)</text>',

        '<text x="90" y="646" font-size="22" font-weight="700" fill="#344E30">Fused</text>',
        '<rect x="270" y="608" width="440" height="58" rx="10" fill="#ECF2EB" stroke="#4B6B46" stroke-width="2.2" />',
        '<text x="490" y="645" text-anchor="middle" font-size="21" font-weight="700" fill="#344E30">Y: 1,024 B</text>',
        '<text x="742" y="645" font-size="21" font-weight="700" fill="#344E30">1,024 B (1 pass, -50%)</text>',
    ])

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="90" y="96" font-size="44" font-weight="700" fill="#1F2A2E">Loop Fusion Eliminates an Intermediate Buffer</text>
    {stages}
    <line x1="90" y1="414" x2="1510" y2="414" stroke="#DDD5C7" stroke-width="1.6" />
    {bars}
    <text x="90" y="848" font-size="18" fill="#6B655B">Fusing bias init removes Z (pp. 14-15).</text>
  </g>
</svg>
"""


def fig_autotuning_feedback_loop() -> str:
    """Figure 3: Learned cost model inside the ML compiler search loop."""
    nodes = "\n    ".join([
        box(90, 235, 270, 128, "Search Space", "Split, reorder, bind", "#EBF1F5", "#356482", "#23475E", "#33434A", title_size=26, sub_size=20),
        draw_arrow(360, 299, 434, 299, "#4B5558", 3.2),
        box(438, 235, 290, 128, "Search Planner", "Picks schedule c", "#F3EEE3", "#4B5558", "#1F2A2E", "#5A554E", title_size=26, sub_size=20),
        draw_arrow(728, 299, 824, 299, "#4B6B46", 3.2),
        '<text x="776" y="282" text-anchor="middle" font-size="24" font-weight="700" fill="#344E30">c</text>',
        box(828, 235, 290, 128, "Code Generator", "Emits binary x", "#ECF2EB", "#4B6B46", "#344E30", "#364635", title_size=26, sub_size=20),
        draw_arrow(1118, 299, 1214, 299, "#A87919", 3.2),
        '<text x="1166" y="282" text-anchor="middle" font-size="24" font-weight="700" fill="#7A5710">x</text>',
        box(1218, 235, 292, 128, "Target Hardware", "Edge or GPU", "#F6F0E1", "#A87919", "#7A5710", "#473E2C", title_size=26, sub_size=20),

        box(930, 560, 320, 128, "Measured Data D", "Records latency f(x)", "#F3EEE3", "#7A7367", "#1F2A2E", "#4B5558", title_size=26, sub_size=20),
        box(438, 560, 320, 128, "ML Cost Model", "Predicts f_hat(e,c)", "#FAECE9", "#B5493A", "#7A2D22", "#52322D", title_size=26, sub_size=20),

        draw_arrow(1364, 363, 1210, 556, "#A87919", 3.2),
        '<text x="1332" y="472" font-size="24" font-weight="700" fill="#7A5710">f(x)</text>',

        draw_arrow(930, 624, 762, 624, "#B5493A", 3.2),
        '<text x="846" y="604" text-anchor="middle" font-size="21" font-weight="700" fill="#7A2D22">train</text>',

        draw_arrow(530, 363, 530, 556, "#4B5558", 3.2),
        '<text x="502" y="468" text-anchor="end" font-size="24" font-weight="700" fill="#1F2A2E">c</text>',
        draw_arrow(642, 560, 642, 367, "#B5493A", 3.2),
        '<text x="668" y="468" font-size="24" font-weight="700" fill="#7A2D22">f_hat(e,c)</text>',
    ])

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="90" y="96" font-size="44" font-weight="700" fill="#1F2A2E">Learned Cost Models Steer Hardware Schedule Search</text>
    {nodes}
    <text x="90" y="848" font-size="18" fill="#6B655B">Measured latencies train f_hat(e,c) to rank schedules (p. 23).</text>
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
    with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
        html_path = Path(tmp) / "fig.html"
        prof_dir = Path(tmp) / "chrome-prof"
        html_path.write_text(html, encoding="utf-8")
        subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                f"--user-data-dir={prof_dir}",
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
        ("deployment-compilation-stack", fig_deployment_compilation_stack()),
        ("ir-lowering-fusion", fig_ir_lowering_fusion()),
        ("autotuning-feedback-loop", fig_autotuning_feedback_loop()),
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
        "lecture": "CMU 10-414/714 Deep Learning Systems — Lecture 23: Model Deployment",
        "version": "v1 r2",
        "figures": [f"{name}.png" for name, _ in specs],
        "svg_word_counts": word_counts,
        "verified_math": {
            "dot_add_grid": [16, 16, 16],
            "dot_add_elements": 16 * 16,
            "dot_add_macs": 16 * 16 * 16,
            "dot_add_unfused_buffers_bytes_fp32": 2 * 16 * 16 * 4,
            "dot_add_fused_buffers_bytes_fp32": 1 * 16 * 16 * 4,
            "tvm_matmul_m_n_k": 1024,
            "tvm_matmul_total_macs": 1024 ** 3,
            "tvm_matmul_tile": [8, 8, 8],
            "tvm_matmul_outer_tiles": 128,
            "tvm_matmul_tile_macs": 8 ** 3,
            "tvm_matmul_tile_operand_elems": 2 * 8 * 8,
            "tvm_matmul_macs_per_tile_elem": (8 ** 3) / (2 * 8 * 8),
            "split_128_factor_4_outer": 128 // 4,
        },
        "palette": PALETTE,
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
