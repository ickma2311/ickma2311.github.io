#!/usr/bin/env python3
"""Generate low-text 1600x900 SVG/PNG figures for CMU ANLP Fall 2025 Lecture 12 (v1 r4)."""

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
    width: float = 3.2,
    dashed: bool = False,
) -> str:
    """Draw a straight line ending with an explicit <polygon> arrowhead at (x2, y2)."""
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy)
    ux, uy = dx / norm, dy / norm
    lx2, ly2 = x2 - 12.0 * ux, y2 - 12.0 * uy
    dash_attr = ' stroke-dasharray="9 7"' if dashed else ""
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
    title_size: int = 26,
    sub_size: int = 21,
    rx: int = 16,
    dashed: bool = False,
) -> str:
    """Render a centered rounded box with 1-line title and optional 1-line subtitle."""
    cx = x + w / 2.0
    dash_attr = ' stroke-dasharray="10 7"' if dashed else ""
    parts = [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2.4"{dash_attr} />'
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


def fig_token_compression() -> str:
    """Figure 1: Log-scale sequence length comparison across image representations."""
    items = [
        ("1024×1024 RGB subpixels", 3_145_728, "3,145,728 tokens", "#B5493A"),
        ("256×256 RGB subpixels", 196_608, "196,608 tokens", "#A87919"),
        ("256×256 spatial grid", 65_536, "65,536 spatial positions", "#356482"),
        ("32×32 VQ token grid", 1_024, "1,024 tokens", "#4B6B46"),
    ]
    x0 = 420.0
    max_w = 870.0
    min_log = math.log10(100.0)
    max_log = math.log10(3_145_728.0)

    def x_for(val: float) -> float:
        return x0 + ((math.log10(val) - min_log) / (max_log - min_log)) * max_w

    grid_ticks = [100, 1_000, 10_000, 100_000, 1_000_000]
    grid_labels = ["10²", "10³", "10⁴", "10⁵", "10⁶"]
    elems = []

    for tick, lbl in zip(grid_ticks, grid_labels):
        gx = x_for(tick)
        if tick > 100:
            elems.append(
                f'<line x1="{gx:.1f}" y1="195" x2="{gx:.1f}" y2="735" '
                f'stroke="#DDD6C7" stroke-width="2" stroke-dasharray="6 6" />'
            )
        elems.append(
            f'<text x="{gx:.1f}" y="776" text-anchor="middle" font-size="22" '
            f'font-weight="600" fill="#6B655B">{lbl}</text>'
        )

    elems.append(
        f'<line x1="{x0:.1f}" y1="195" x2="{x0:.1f}" y2="735" stroke="#8C8375" stroke-width="2.5" />'
    )

    y_start = 230.0
    row_step = 132.0
    bar_h = 66.0
    for idx, (label, val, val_txt, color) in enumerate(items):
        by = y_start + idx * row_step
        cy = by + bar_h * 0.62
        bw = x_for(val) - x0
        elems.append(
            f'<text x="{x0 - 24:.1f}" y="{cy:.1f}" text-anchor="end" font-size="25" '
            f'font-weight="700" fill="#1F2A2E">{label}</text>'
        )
        elems.append(
            f'<rect x="{x0:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bar_h:.1f}" '
            f'rx="10" fill="{color}" />'
        )
        elems.append(
            f'<text x="{x0 + bw + 18:.1f}" y="{cy:.1f}" text-anchor="start" font-size="23" '
            f'font-weight="700" fill="{color}">{val_txt}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="90" y="96" font-size="44" font-weight="700" fill="#1F2A2E">Visual Tokenization Compresses Sequence Length</text>
    <text x="90" y="144" font-size="24" fill="#6B655B">Discrete 32×32 VQ codes cut 256×256 steps by 64× (derived 192× vs RGB)</text>
    {"".join(elems)}
    <text x="855" y="838" text-anchor="middle" font-size="23" font-weight="600" fill="#4B5558">Sequence length (log₁₀ scale)</text>
  </g>
</svg>
"""


def fig_vqvae_ste() -> str:
    """Figure 2: VQ-VAE nearest-neighbor lookup and straight-through gradient bypass."""
    se = '<tspan baseline-shift="sub" font-size="18">e</tspan>'
    sq = '<tspan baseline-shift="sub" font-size="18">q</tspan>'
    sj = '<tspan baseline-shift="sub" font-size="18">j</tspan>'
    sk = '<tspan baseline-shift="sub" font-size="18">k*</tspan>'
    srec = '<tspan baseline-shift="sub" font-size="18">rec</tspan>'
    parts = [
        # Codebook box above Quantizer
        box(650, 175, 300, 125, "Codebook E", "K vectors in ℝᵈ", "#ECF2EB", "#4B6B46", "#2E472B", "#364635"),

        # Main forward pipeline
        box(75, 420, 210, 130, "Image x", "Input pixels", "#F3EEE3", "#7A7367", "#1F2A2E", "#5A554E"),
        draw_arrow(285, 485, 355, 485, "#356482", 3.4),
        box(360, 420, 230, 130, "Encoder", f"z{se}(x) ∈ ℝᵈ", "#EBF1F5", "#356482", "#23475E", "#33434A"),
        draw_arrow(590, 485, 665, 485, "#356482", 3.4),
        box(670, 420, 260, 130, "Quantizer", f"z{sq} = e{sk} (nearest e{sj})", "#F8EFE0", "#A87919", "#6F4E0C", "#5B4A23", dashed=True),
        draw_arrow(930, 485, 1005, 485, "#356482", 3.4),
        box(1010, 420, 230, 130, "Decoder", f"p(x | z{sq})", "#EBF1F5", "#356482", "#23475E", "#33434A"),
        draw_arrow(1240, 485, 1310, 485, "#356482", 3.4),
        box(1315, 420, 210, 130, "Output x̂", "Reconstruction", "#F3EEE3", "#7A7367", "#1F2A2E", "#5A554E"),

        # Lookup and codebook update arrows
        draw_arrow(760, 300, 760, 415, "#4B6B46", 3.2, dashed=True),
        draw_arrow(840, 415, 840, 305, "#4B6B46", 3.4),
        '<text x="862" y="366" font-size="22" font-weight="700" fill="#4B6B46">Codebook loss</text>',

        # Commitment loss arc from Quantizer to Encoder
        '<path d="M 700 420 C 665 340, 540 340, 510 410" fill="none" stroke="#4B6B46" stroke-width="3.2" />',
        f'<polygon points="{arrow_polygon(507, 419, -0.3, 1, 16, 7)}" fill="#4B6B46" />',
        '<text x="515" y="342" text-anchor="middle" font-size="22" font-weight="700" fill="#4B6B46">Commitment loss</text>',

        # Straight-through gradient bypass curve from Decoder input back to Encoder output
        '<path d="M 970 500 C 970 690, 625 690, 625 512" fill="none" stroke="#B5493A" stroke-width="4.2" />',
        f'<polygon points="{arrow_polygon(625, 502, 0, -1, 18, 8)}" fill="#B5493A" />',
        f'<text x="800" y="705" text-anchor="middle" font-size="25" font-weight="700" fill="#B5493A">Straight-through copy: ∂L{srec}/∂z{se} ← ∂L{srec}/∂z{sq}</text>',
        '<text x="800" y="746" text-anchor="middle" font-size="22" fill="#6B655B">Bypasses zero gradient of discrete argmin lookup</text>',
    ]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="80" y="96" font-size="44" font-weight="700" fill="#1F2A2E">Straight-Through Gradient Bypasses Discrete Lookup</text>
    {"".join(parts)}
  </g>
</svg>
"""


def fig_generation_paths() -> str:
    """Figure 3: Two bridges from text prompts to generated images."""
    sub_t = '<tspan baseline-shift="sub" font-size="18">T</tspan>'
    sub_i = '<tspan baseline-shift="sub" font-size="18">I</tspan>'
    parts = [
        # Row 1: Unified Discrete AR
        '<text x="90" y="215" font-size="27" font-weight="700" fill="#356482">1. Early Fusion (Chameleon / Liquid)</text>',
        box(90, 248, 275, 130, "Text + Image", "Mixed prompt", "#EBF1F5", "#356482", "#23475E", "#33434A"),
        draw_arrow(365, 313, 440, 313, "#356482", 3.4),
        box(445, 248, 310, 130, "BPE + VQ-GAN", "Token IDs", "#ECF2EB", "#4B6B46", "#2E472B", "#364635"),
        draw_arrow(755, 313, 830, 313, "#356482", 3.4),
        box(835, 248, 335, 130, "Single Transformer", "Next-token CE", "#EBF1F5", "#356482", "#23475E", "#33434A"),
        draw_arrow(1170, 313, 1245, 313, "#356482", 3.4),
        box(1250, 248, 260, 130, "Detokenizer", "Pixels x̂", "#ECF2EB", "#4B6B46", "#2E472B", "#364635"),

        # Divider
        '<line x1="90" y1="465" x2="1510" y2="465" stroke="#DDD6C7" stroke-width="2" stroke-dasharray="8 8" />',

        # Row 2: CLIP + Diffusion (DALL-E 2)
        '<text x="90" y="545" font-size="27" font-weight="700" fill="#B5493A">2. Continuous Latents + Diffusion (DALL-E 2)</text>',
        box(90, 578, 275, 130, "Text Prompt", f"x{sub_t}", "#F8EFE0", "#A87919", "#6F4E0C", "#5B4A23"),
        draw_arrow(365, 643, 440, 643, "#B5493A", 3.4),
        box(445, 578, 310, 130, "CLIP Text", f"Embedding z{sub_t}", "#F8EFE0", "#A87919", "#6F4E0C", "#5B4A23"),
        draw_arrow(755, 643, 830, 643, "#B5493A", 3.4),
        box(835, 578, 335, 130, "Diffusion Prior", f"p(z{sub_i} | z{sub_t})", "#F8EBE8", "#B5493A", "#7A2D22", "#5C352E"),
        draw_arrow(1170, 643, 1245, 643, "#B5493A", 3.4),
        box(1250, 578, 260, 130, "Diffusion Decoder", f"1024×1024 x{sub_i}", "#F8EBE8", "#B5493A", "#7A2D22", "#5C352E"),
    ]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <rect width="1600" height="900" fill="#FAF6EE" />
  <g font-family="{FONT}">
    <text x="90" y="102" font-size="44" font-weight="700" fill="#1F2A2E">Two Bridges from Text Prompts to Generated Pixels</text>
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


def verify_math() -> dict:
    """Numerically verify lecture counts and the constructed VQ-VAE worked example."""
    # Sequence lengths
    seq_1024_rgb = 1024 * 1024 * 3
    seq_256_rgb = 256 * 256 * 3
    seq_256_spatial = 256 * 256
    seq_vq_32 = 32 * 32

    # Constructed 2D VQ-VAE example
    z_e = (0.8, 0.3)
    codebook = [(0.0, 0.0), (1.0, 0.5), (-1.0, 1.0)]
    dists_sq = [round((z_e[0] - e[0]) ** 2 + (z_e[1] - e[1]) ** 2, 6) for e in codebook]
    k_star = dists_sq.index(min(dists_sq)) + 1  # 1-indexed
    e_star = codebook[k_star - 1]
    beta = 0.25
    g_rec = (0.4, -0.2)
    grad_commit_ze = (round(2 * beta * (z_e[0] - e_star[0]), 6), round(2 * beta * (z_e[1] - e_star[1]), 6))
    grad_ze_total = (round(g_rec[0] + grad_commit_ze[0], 6), round(g_rec[1] + grad_commit_ze[1], 6))
    grad_e_star = (round(2 * (e_star[0] - z_e[0]), 6), round(2 * (e_star[1] - z_e[1]), 6))

    return {
        "sequence_lengths": {
            "rgb_1024x1024": seq_1024_rgb,
            "rgb_256x256": seq_256_rgb,
            "spatial_256x256": seq_256_spatial,
            "vq_32x32": seq_vq_32,
            "ratio_spatial_256_to_vq": seq_256_spatial // seq_vq_32,
            "ratio_rgb_256_to_vq": seq_256_rgb // seq_vq_32,
        },
        "vqvae_constructed_2d": {
            "z_e": list(z_e),
            "codebook": [list(c) for c in codebook],
            "dists_sq": dists_sq,
            "k_star": k_star,
            "e_star": list(e_star),
            "beta": beta,
            "g_rec": list(g_rec),
            "grad_commit_ze": list(grad_commit_ze),
            "grad_ze_total": list(grad_ze_total),
            "grad_e_star": list(grad_e_star),
        },
    }


def main() -> None:
    specs = [
        ("token-compression-sequence", fig_token_compression()),
        ("vqvae-ste-gradient", fig_vqvae_ste()),
        ("multimodal-generation-paths", fig_generation_paths()),
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
        "lecture": "CMU 11-711 Advanced NLP (Fall 2025) — Lecture 12: Multimodal Modeling II",
        "version": "v1 r4",
        "figures": [f"{name}.png" for name, _ in specs],
        "svg_word_counts": word_counts,
        "verified_math": verify_math(),
        "palette": PALETTE,
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
