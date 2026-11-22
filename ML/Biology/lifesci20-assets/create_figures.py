"""Programmatic scientific figures for MIT 6.874 Lecture 20 (v1 r3).
Pure Python standard-library SVG generator + macOS rasterization helper.
All numerical examples, Bezier midpoints, fiber bin counts, and 2D TVN
whitening transforms are verified via assertions and recorded in manifest.json.
"""
import json
import math
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path("/Users/chaoma/projects/ickma2311.github.io/ML/Biology/lifesci20-assets")
OUT.mkdir(parents=True, exist_ok=True)

# Warm scientific textbook palette
BG = "#FAF6EE"
CARD = "#FFFDF9"
PANEL_ALT = "#F3ECE0"
BORDER = "#D6CEC0"
INK = "#262420"
MUTED = "#5C5852"
BLUE = "#356482"
BLUE_LIGHT = "#E6EFF5"
RED = "#B5493A"
RED_LIGHT = "#F8E8E5"
GREEN = "#4B6B46"
GREEN_LIGHT = "#E8F0E6"
GOLD = "#A87919"
GOLD_LIGHT = "#F7EFE0"

W, H = 1600, 900

# ---------------------------------------------------------------------------
# 1. Exact mathematical assertions (saved to manifest.json)
# ---------------------------------------------------------------------------
# Collagen axial orientation entropy (theta in [0, 180), K = 4 equal 45-deg bins)
p_aligned = [1.0, 0.0, 0.0, 0.0]
H_aligned = -sum(p * math.log2(p) for p in p_aligned if p > 0)
assert abs(H_aligned - 0.0) < 1e-12

# Actual angles drawn in Figure 1B disordered fiber panel (must bin 5, 5, 5, 5)
DISORDERED_ANGLES_DEG = [
    15, 72, 130, 168, 45,
    110, 5, 88, 152, 33,
    125, 60, 175, 22, 95,
    142, 158, 80, 118, 10,
]
bin_counts = [sum(45 * k <= (ang % 180) < 45 * (k + 1) for ang in DISORDERED_ANGLES_DEG) for k in range(4)]
assert bin_counts == [5, 5, 5, 5], f"Expected [5, 5, 5, 5], got {bin_counts}"
p_disordered = [c / len(DISORDERED_ANGLES_DEG) for c in bin_counts]
H_disordered = -sum(p * math.log2(p) for p in p_disordered if p > 0)
assert abs(H_disordered - 2.0) < 1e-12

# Combinatorial explosion in TB drug regimens
n_20_choose_3 = math.comb(20, 3)
assert n_20_choose_3 == 1140
n_10_single = math.comb(10, 1)
n_10_pair = math.comb(10, 2)
n_10_triple = math.comb(10, 3)
n_10_multidrug = n_10_pair + n_10_triple
n_10_total = n_10_single + n_10_multidrug
assert (n_10_single, n_10_pair, n_10_triple, n_10_multidrug, n_10_total) == (10, 45, 120, 165, 175)

# DiaMOND FIC worked example in IC90-normalized coordinates (IC90_X = 1.0, IC90_Y = 1.0)
r_exp = math.hypot(0.5, 0.5)
r_obs_syn = math.hypot(0.25, 0.25)
r_obs_ant = math.hypot(0.75, 0.75)
fic_syn = r_obs_syn / r_exp
fic_add = r_exp / r_exp
fic_ant = r_obs_ant / r_exp
assert abs(fic_syn - 0.50) < 1e-12
assert abs(fic_add - 1.00) < 1e-12
assert abs(fic_ant - 1.50) < 1e-12

# Verify quadratic Bezier midpoints pass exactly through (0.25, 0.25) and (0.75, 0.75)
def qbezier(p0, pc, p1, t=0.5):
    return (
        (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * pc[0] + t ** 2 * p1[0],
        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * pc[1] + t ** 2 * p1[1],
    )

syn_mid = qbezier((0.0, 1.0), (0.0, 0.0), (1.0, 0.0), 0.5)
ant_mid = qbezier((0.0, 1.0), (1.0, 1.0), (1.0, 0.0), 0.5)
assert abs(syn_mid[0] - 0.25) < 1e-12 and abs(syn_mid[1] - 0.25) < 1e-12
assert abs(ant_mid[0] - 0.75) < 1e-12 and abs(ant_mid[1] - 0.75) < 1e-12


def arrow_head(x1, y1, x2, y2, color, size=10.0, half_w=4.5):
    """Explicit SVG <polygon> arrowhead pointing toward (x2, y2) along (x1,y1)->(x2,y2)."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-9:
        return ""
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    bx, by = x2 - size * ux, y2 - size * uy
    p1 = (x2, y2)
    p2 = (bx + half_w * px, by + half_w * py)
    p3 = (bx - half_w * px, by - half_w * py)
    return (
        f'<polygon points="{p1[0]:.1f},{p1[1]:.1f} '
        f'{p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}" fill="{color}"/>'
    )


def arrow_line(x1, y1, x2, y2, color=INK, width=2.0, size=10.0, half_w=4.5):
    """Line ending cleanly at the base of an explicit <polygon> arrowhead."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    lx2, ly2 = x2 - (size * 0.75) * ux, y2 - (size * 0.75) * uy
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{lx2:.1f}" y2="{ly2:.1f}" '
        f'stroke="{color}" stroke-width="{width}"/>'
        + arrow_head(x1, y1, x2, y2, color, size=size, half_w=half_w)
    )


def svg_wrap(title, subtitle, body, footer):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <style>
      .title {{ font-family: Georgia, "Times New Roman", serif; font-size: 30px; font-weight: 700; fill: {INK}; }}
      .subtitle {{ font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; font-size: 16.5px; fill: {MUTED}; }}
      .panel-title {{ font-family: Georgia, "Times New Roman", serif; font-size: 22px; font-weight: 700; fill: {INK}; }}
      .label {{ font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; font-size: 16px; font-weight: 600; fill: {INK}; }}
      .body {{ font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; font-size: 14.8px; fill: {INK}; }}
      .small {{ font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; font-size: 13.5px; fill: {MUTED}; }}
      .math {{ font-family: Georgia, "Times New Roman", serif; font-style: italic; font-size: 17px; fill: {INK}; }}
      .num {{ font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; font-size: 18px; font-weight: 700; }}
      .footer {{ font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; font-size: 13px; fill: {MUTED}; }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <text x="56" y="56" class="title">{title}</text>
  <text x="56" y="86" class="subtitle">{subtitle}</text>
  <line x1="56" y1="104" x2="{W - 56}" y2="104" stroke="{BORDER}" stroke-width="1.5"/>
  {body}
  <line x1="56" y1="846" x2="{W - 56}" y2="846" stroke="{BORDER}" stroke-width="1"/>
  <text x="56" y="872" class="footer">{footer}</text>
</svg>
'''


# ---------------------------------------------------------------------------
# FIGURE 1: End-to-End CNN Fragility vs. Hybrid Pathology Pipeline
# ---------------------------------------------------------------------------
def build_fig1():
    def auc_y(val):
        return 510 - (val - 0.50) * 500

    bars = [
        ("Pathologists\n(Cohort 1, n = 105)", 0.74, MUTED, 210),
        ("End-to-End CNN\n(Cohort 1, n = 105)", 0.97, BLUE, 395),
        ("Same CNN\n(Cohort 2)", 0.75, RED, 580),
    ]
    bar_svg = []
    for tick in [0.50, 0.60, 0.70, 0.80, 0.90, 1.00]:
        yy = auc_y(tick)
        bar_svg.append(f'<line x1="126" y1="{yy:.1f}" x2="690" y2="{yy:.1f}" stroke="{BORDER}" stroke-dasharray="4,4" stroke-width="1"/>')
        bar_svg.append(f'<text x="116" y="{yy + 5:.1f}" text-anchor="end" class="small">{tick:.2f}</text>')
    bar_svg.append(f'<line x1="126" y1="250" x2="126" y2="510" stroke="{INK}" stroke-width="1.5"/>')
    bar_svg.append(f'<line x1="126" y1="510" x2="690" y2="510" stroke="{INK}" stroke-width="1.5"/>')
    bar_svg.append('<text x="74" y="385" transform="rotate(-90 74 385)" text-anchor="middle" class="small">Reported AUC (Penn Heart Failure Biopsies)</text>')

    for lbl, val, col, cx in bars:
        top = auc_y(val)
        bh = 510 - top
        bar_svg.append(f'<rect x="{cx - 46}" y="{top:.1f}" width="92" height="{bh:.1f}" rx="4" fill="{col}" fill-opacity="0.88"/>')
        bar_svg.append(f'<text x="{cx}" y="{top - 10:.1f}" text-anchor="middle" class="num" fill="{col}">{val:.2f}</text>')
        for idx, l in enumerate(lbl.split("\n")):
            bar_svg.append(f'<text x="{cx}" y="{534 + idx * 18}" text-anchor="middle" class="small" fill="{INK}">{l}</text>')

    # Clean curved red drop arrow BELOW callout pill (zero overlap)
    bar_svg.append(f'<rect x="494" y="246" width="184" height="46" rx="6" fill="{RED_LIGHT}" stroke="{RED}" stroke-width="1.1"/>')
    bar_svg.append(f'<text x="586" y="266" text-anchor="middle" class="small" fill="{RED}" font-weight="700">−0.22 CNN drop</text>')
    bar_svg.append(f'<text x="586" y="283" text-anchor="middle" class="small" fill="{RED}">same site &amp; scanner</text>')
    # Curve from (447, 294) sweeping cleanly under pill to (535, 376) with explicit polygon arrowhead
    bar_svg.append(f'<path d="M 447 294 C 482 308, 510 342, 531 372" fill="none" stroke="{RED}" stroke-width="2.4"/>')
    bar_svg.append(arrow_head(518, 353, 536, 379, RED, size=11.0, half_w=5.0))

    # Right panel: Aligned vs Disordered axial fiber drawings
    aligned_lines = []
    for row in range(4):
        for col_i in range(5):
            x0 = 875 + col_i * 52
            y0 = 542 + row * 24
            aligned_lines.append(f'<line x1="{x0}" y1="{y0}" x2="{x0 + 34}" y2="{y0 - 4}" stroke="{RED}" stroke-width="2.6" stroke-linecap="round"/>')

    disordered_lines = []
    idx = 0
    for row in range(4):
        for col_i in range(5):
            cx = 1228 + col_i * 52
            cy = 540 + row * 24
            ang = math.radians(DISORDERED_ANGLES_DEG[idx])
            idx += 1
            dx, dy = 16 * math.cos(ang), 16 * math.sin(ang)
            disordered_lines.append(f'<line x1="{cx - dx:.1f}" y1="{cy - dy:.1f}" x2="{cx + dx:.1f}" y2="{cy + dy:.1f}" stroke="{GREEN}" stroke-width="2.6" stroke-linecap="round"/>')

    body = f'''
    <!-- Left Panel -->
    <rect x="56" y="124" width="690" height="700" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>
    <text x="84" y="164" class="panel-title">A. End-to-End CNN Vulnerability to Acquisition Shift</text>
    <text x="84" y="190" class="small">Reported Penn endomyocardial biopsy AUCs: pixel convolutions absorb scanner traits</text>
    {"".join(bar_svg)}
    <rect x="88" y="588" width="626" height="212" rx="8" fill="{PANEL_ALT}" stroke="{BORDER}" stroke-width="1"/>
    <text x="110" y="616" class="label">Why end-to-end pathology classifiers fail silently</text>
    <text x="110" y="644" class="body">• Cohort 1 (104 train, 105 test): CNN AUC 0.97 ± 0.01 vs. pathologists 0.74 (0.75, 0.73).</text>
    <text x="110" y="672" class="body">• Cohort 2: CNN AUC fell by 0.22 (0.97 → 0.75) on biopsies from the same site and</text>
    <text x="124" y="694" class="body">scanner; the lecturer attributed the drop to a remote scanner software upgrade.</text>
    <text x="110" y="722" class="body">• No Cohort 2 pathologist AUC or paired hybrid Penn AUC is shown in this figure</text>
    <text x="124" y="744" class="body">(Part A recording, 21:09–26:52; Nirschl et al., PLOS ONE 2018).</text>
    <text x="110" y="778" class="body" fill="{BLUE}" font-weight="600">Takeaway: strong single-cohort AUC does not guarantee scanner invariance.</text>

    <!-- Right Panel -->
    <rect x="774" y="124" width="770" height="700" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>
    <text x="802" y="164" class="panel-title">B. Hybrid Pipeline: Segment Primitives, Engineer Features</text>
    <text x="802" y="190" class="small">Deep learning locates biological objects; explicit geometry drives risk scoring</text>

    <!-- 3-step pipeline boxes with explicit polygon arrowheads -->
    <rect x="802" y="218" width="210" height="106" rx="8" fill="{BLUE_LIGHT}" stroke="{BLUE}" stroke-width="1.5"/>
    <text x="907" y="248" text-anchor="middle" class="label" fill="{BLUE}">1. Deep Segmentation</text>
    <text x="907" y="274" text-anchor="middle" class="small" fill="{INK}">Detect nuclei, TILs,</text>
    <text x="907" y="294" text-anchor="middle" class="small" fill="{INK}">glands &amp; collagen fibers</text>
    <text x="907" y="314" text-anchor="middle" class="small">(+ Quick Annotator)</text>

    {arrow_line(1012, 271, 1054, 271, INK, width=2.0, size=10.0, half_w=5.0)}

    <rect x="1056" y="218" width="222" height="106" rx="8" fill="{GOLD_LIGHT}" stroke="{GOLD}" stroke-width="1.5"/>
    <text x="1167" y="248" text-anchor="middle" class="label" fill="{GOLD}">2. Explicit Features</text>
    <text x="1167" y="274" text-anchor="middle" class="small" fill="{INK}">Voronoi / Delaunay graphs,</text>
    <text x="1167" y="294" text-anchor="middle" class="small" fill="{INK}">gland lumen geometry,</text>
    <text x="1167" y="314" text-anchor="middle" class="small" fill="{INK}">orientation entropy H(p)</text>

    {arrow_line(1278, 271, 1320, 271, INK, width=2.0, size=10.0, half_w=5.0)}

    <rect x="1322" y="218" width="194" height="106" rx="8" fill="{GREEN_LIGHT}" stroke="{GREEN}" stroke-width="1.5"/>
    <text x="1419" y="248" text-anchor="middle" class="label" fill="{GREEN}">3. Clinical Risk Score</text>
    <text x="1419" y="274" text-anchor="middle" class="small" fill="{INK}">Prognostic &amp; predictive</text>
    <text x="1419" y="294" text-anchor="middle" class="small" fill="{INK}">risk models (IbRiS)</text>
    <text x="1419" y="314" text-anchor="middle" class="small">non-destructive H&amp;E</text>

    <!-- Worked Example Box: Collagen Fiber Orientation Disorder -->
    <rect x="802" y="352" width="714" height="448" rx="8" fill="{PANEL_ALT}" stroke="{BORDER}" stroke-width="1"/>
    <text x="826" y="384" class="label">Constructed Check: Local-Window Entropy (CFOD-TS Schematic)</text>
    <text x="826" y="410" class="small">Undirected axial angle θ ∈ [0°, 180°) in K = 4 bins: H(p) = −Σ p<tspan baseline-shift="sub" font-size="10.5">k</tspan> log<tspan baseline-shift="sub" font-size="10.5">2</tspan>(p<tspan baseline-shift="sub" font-size="10.5">k</tspan>) (bits)</text>

    <!-- Left mini-card: Aligned -->
    <rect x="826" y="432" width="320" height="250" rx="8" fill="{CARD}" stroke="{RED}" stroke-width="1.3"/>
    <text x="986" y="460" text-anchor="middle" class="label" fill="{RED}">Aligned Fibers (Low Disorder)</text>
    <text x="986" y="482" text-anchor="middle" class="small">p = (1, 0, 0, 0)  →  H = 0.00 bits</text>
    <rect x="846" y="498" width="280" height="148" rx="6" fill="{RED_LIGHT}" fill-opacity="0.45"/>
    {"".join(aligned_lines)}
    <text x="986" y="668" text-anchor="middle" class="small" fill="{MUTED}" font-weight="600">Toy check: 20/20 fibers in one 45° bin</text>

    <!-- Right mini-card: Disordered -->
    <rect x="1174" y="432" width="320" height="250" rx="8" fill="{CARD}" stroke="{GREEN}" stroke-width="1.3"/>
    <text x="1334" y="460" text-anchor="middle" class="label" fill="{GREEN}">Disordered Fibers (High Disorder)</text>
    <text x="1334" y="482" text-anchor="middle" class="small">p = (0.25, 0.25, 0.25, 0.25)  →  H = 2.00 bits</text>
    <rect x="1194" y="498" width="280" height="148" rx="6" fill="{GREEN_LIGHT}" fill-opacity="0.45"/>
    {"".join(disordered_lines)}
    <text x="1334" y="668" text-anchor="middle" class="small" fill="{MUTED}" font-weight="600">Toy check: 5 fibers per 45° bin [5,5,5,5]</text>

    <text x="826" y="716" class="body">Reported ER+ cohorts (E2197, n = 234, p = 0.0057; TCGA, n = 171, p = 0.0090; Part A pp. 19–20):</text>
    <text x="826" y="742" class="body">higher CFOD-TS was independently linked to longer disease-free survival (aligned fibers may act</text>
    <text x="826" y="768" class="body">as tumor-cell migration tracks, whereas disordered stromal collagen impedes invasion).</text>
    '''
    svg = svg_wrap(
        "End-to-End Fragility vs. Hybrid Pathology Features",
        "MIT 6.874 Lecture 20 (Part A · Anant Madabhushi): separating object segmentation from explicit geometric risk modeling",
        body,
        "Panel A: reported Penn endomyocardial biopsy AUCs (21:09–26:52; Nirschl et al., 2018). Panel B: hybrid pipeline, constructed 4-bin axial schematic, and reported ER+ DFS."
    )
    ET.fromstring(svg)
    (OUT / "hybrid-pathology-pipeline.svg").write_text(svg)


# ---------------------------------------------------------------------------
# FIGURE 2: MorphEUS — Batch Normalization (TVN) & Consensus k-NN
# ---------------------------------------------------------------------------
def build_fig2():
    # Synthetic 2-batch data where BOTH Drug A and Drug B appear in BOTH batches
    # Batch 1 control cluster centered near (-0.95, -0.60); Batch 2 near (+0.95, +0.60)
    # Distinct shapes around each batch mean so Batch 1 & Batch 2 controls visibly intermix after TVN
    b1_ctrl = [(-1.48, -0.92), (-1.18, -0.18), (-0.72, -1.02), (-0.42, -0.28), (-1.28, -0.52), (-0.62, -0.68)]
    b2_ctrl = [(0.52, 0.38), (0.82, 0.98), (1.28, 0.22), (1.38, 0.88), (0.68, 0.78), (1.02, 0.36)]
    b1_drugA = [(-1.60, 0.06), (-1.42, 0.30), (-1.26, 0.14)]
    b2_drugA = [(0.26, 1.18), (0.44, 1.48), (0.64, 1.28)]
    b1_drugB = [(-0.26, -1.24), (-0.10, -1.08), (-0.46, -1.38)]
    b2_drugB = [(1.52, -0.12), (1.76, 0.10), (1.38, -0.22)]

    def mean2(pts):
        return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

    m1, m2 = mean2(b1_ctrl), mean2(b2_ctrl)
    pooled_ctrl = [(x - m1[0], y - m1[1]) for x, y in b1_ctrl] + [(x - m2[0], y - m2[1]) for x, y in b2_ctrl]
    n_c = len(pooled_ctrl)
    cxx = sum(x * x for x, _ in pooled_ctrl) / (n_c - 1)
    cyy = sum(y * y for _, y in pooled_ctrl) / (n_c - 1)
    cxy = sum(x * y for x, y in pooled_ctrl) / (n_c - 1)
    tr, diff = cxx + cyy, cxx - cyy
    disc = math.hypot(diff, 2 * cxy)
    l1, l2 = 0.5 * (tr + disc), 0.5 * (tr - disc)
    v1 = (l1 - cyy, cxy) if abs(cxy) > 1e-12 else ((1.0, 0.0) if cxx >= cyy else (0.0, 1.0))
    norm1 = math.hypot(*v1)
    u1 = (v1[0] / norm1, v1[1] / norm1)
    u2 = (-u1[1], u1[0])
    inv_s1, inv_s2 = 1.0 / math.sqrt(l1), 1.0 / math.sqrt(l2)

    def zca_whiten(pts, batch_mean):
        out = []
        for x, y in pts:
            dx, dy = x - batch_mean[0], y - batch_mean[1]
            z1 = (dx * u1[0] + dy * u1[1]) * inv_s1
            z2 = (dx * u2[0] + dy * u2[1]) * inv_s2
            out.append((z1 * u1[0] + z2 * u2[0], z1 * u1[1] + z2 * u2[1]))
        return out

    w_ctrl1 = zca_whiten(b1_ctrl, m1)
    w_ctrl2 = zca_whiten(b2_ctrl, m2)
    w_ctrl = w_ctrl1 + w_ctrl2
    w_drugA = zca_whiten(b1_drugA, m1) + zca_whiten(b2_drugA, m2)
    w_drugB = zca_whiten(b1_drugB, m1) + zca_whiten(b2_drugB, m2)

    # Assert exact sample mean = 0 and sample covariance = I for pooled whitened controls
    wm = mean2(w_ctrl)
    wcxx = sum((x - wm[0]) ** 2 for x, _ in w_ctrl) / (len(w_ctrl) - 1)
    wcyy = sum((y - wm[1]) ** 2 for _, y in w_ctrl) / (len(w_ctrl) - 1)
    wcxy = sum((x - wm[0]) * (y - wm[1]) for x, y in w_ctrl) / (len(w_ctrl) - 1)
    cov_err = max(abs(wm[0]), abs(wm[1]), abs(wcxx - 1.0), abs(wcyy - 1.0), abs(wcxy))
    assert cov_err < 1e-12, f"Whitened control covariance mismatch: {cov_err}"

    def map_pt(x, y, ox, oy, sx, sy):
        return ox + x * sx, oy - y * sy

    # Before plot box: x in [100..354], y in [264..476], origin (227, 370)
    before_pts = []
    for x, y in b1_ctrl:
        px, py = map_pt(x, y, 227, 370, 62, 58)
        assert 96 <= px <= 358 and 260 <= py <= 480
        before_pts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.2" fill="{BLUE}" fill-opacity="0.78"/>')
    for x, y in b2_ctrl:
        px, py = map_pt(x, y, 227, 370, 62, 58)
        assert 96 <= px <= 358 and 260 <= py <= 480
        before_pts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.2" fill="{GOLD}" fill-opacity="0.82"/>')
    for x, y in b1_drugA + b2_drugA:
        px, py = map_pt(x, y, 227, 370, 62, 58)
        assert 96 <= px <= 358 and 260 <= py <= 480
        before_pts.append(f'<rect x="{px - 4.8:.1f}" y="{py - 4.8:.1f}" width="9.6" height="9.6" fill="{RED}" fill-opacity="0.88"/>')
    for x, y in b1_drugB + b2_drugB:
        px, py = map_pt(x, y, 227, 370, 62, 58)
        assert 96 <= px <= 358 and 260 <= py <= 480
        before_pts.append(f'<polygon points="{px:.1f},{py - 5.8:.1f} {px - 5.5:.1f},{py + 4.8:.1f} {px + 5.5:.1f},{py + 4.8:.1f}" fill="{GREEN}" fill-opacity="0.88"/>')

    # After plot box: x in [442..702], y in [264..476], origin (572, 370), isotropic scale 34 px/unit
    after_pts = []
    for x, y in w_ctrl1:
        px, py = map_pt(x, y, 572, 370, 34, 34)
        assert 438 <= px <= 706 and 260 <= py <= 480, f"Out of bounds: {(px, py)}"
        after_pts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.2" fill="{BLUE}" fill-opacity="0.78"/>')
    for x, y in w_ctrl2:
        px, py = map_pt(x, y, 572, 370, 34, 34)
        assert 438 <= px <= 706 and 260 <= py <= 480
        after_pts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.2" fill="{GOLD}" fill-opacity="0.82"/>')
    for x, y in w_drugA:
        px, py = map_pt(x, y, 572, 370, 34, 34)
        assert 438 <= px <= 706 and 260 <= py <= 480
        after_pts.append(f'<rect x="{px - 4.8:.1f}" y="{py - 4.8:.1f}" width="9.6" height="9.6" fill="{RED}" fill-opacity="0.88"/>')
    for x, y in w_drugB:
        px, py = map_pt(x, y, 572, 370, 34, 34)
        assert 438 <= px <= 706 and 260 <= py <= 480
        after_pts.append(f'<polygon points="{px:.1f},{py - 5.8:.1f} {px - 5.5:.1f},{py + 4.8:.1f} {px + 5.5:.1f},{py + 4.8:.1f}" fill="{GREEN}" fill-opacity="0.88"/>')

    # Unit-std contour circle (1.5 sigma at scale 34 -> r = 51 px) centered at (572, 370)
    b1_mx, b1_my = map_pt(m1[0], m1[1], 227, 370, 62, 58)
    b2_mx, b2_my = map_pt(m2[0], m2[1], 227, 370, 62, 58)

    body = f'''
    <!-- Left Panel: TVN -->
    <rect x="56" y="124" width="692" height="700" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>
    <text x="84" y="164" class="panel-title">A. Typical Variation Normalization (TVN)</text>
    <text x="84" y="190" class="small">Constructed 2D check: per-batch control centering + pooled unregularized ZCA whitening</text>

    <!-- Before box -->
    <rect x="84" y="218" width="286" height="290" rx="8" fill="{PANEL_ALT}" stroke="{BORDER}" stroke-width="1"/>
    <text x="227" y="246" text-anchor="middle" class="label">Before TVN (Raw Space)</text>
    <line x1="100" y1="370" x2="354" y2="370" stroke="{BORDER}" stroke-width="1"/>
    <line x1="227" y1="264" x2="227" y2="478" stroke="{BORDER}" stroke-width="1"/>
    <ellipse cx="{b1_mx:.1f}" cy="{b1_my:.1f}" rx="42" ry="30" fill="{BLUE}" fill-opacity="0.10" stroke="{BLUE}" stroke-dasharray="4,3"/>
    <ellipse cx="{b2_mx:.1f}" cy="{b2_my:.1f}" rx="42" ry="30" fill="{GOLD}" fill-opacity="0.12" stroke="{GOLD}" stroke-dasharray="4,3"/>
    {"".join(before_pts)}
    <text x="227" y="498" text-anchor="middle" class="small">Batch shift separates same-drug replicates</text>

    <!-- Explicit polygon arrow -->
    {arrow_line(376, 365, 418, 365, BLUE, width=2.5, size=10.0, half_w=5.0)}
    <text x="397" y="346" text-anchor="middle" class="small" fill="{BLUE}" font-weight="700">TVN</text>

    <!-- After box -->
    <rect x="424" y="218" width="296" height="290" rx="8" fill="{PANEL_ALT}" stroke="{BORDER}" stroke-width="1"/>
    <text x="572" y="246" text-anchor="middle" class="label">After TVN (Ideal: μ = 0, Σ = I)</text>
    <line x1="442" y1="370" x2="702" y2="370" stroke="{BORDER}" stroke-width="1"/>
    <line x1="572" y1="264" x2="572" y2="478" stroke="{BORDER}" stroke-width="1"/>
    <circle cx="572" cy="370" r="51" fill="{BLUE}" fill-opacity="0.07" stroke="{MUTED}" stroke-dasharray="4,3"/>
    {"".join(after_pts)}
    <text x="572" y="498" text-anchor="middle" class="small">Controls align; drugs cluster across batches</text>

    <!-- Legend -->
    <circle cx="94" cy="540" r="5.2" fill="{BLUE}"/>
    <text x="106" y="545" class="small">Batch 1 untreated</text>
    <circle cx="244" cy="540" r="5.2" fill="{GOLD}"/>
    <text x="256" y="545" class="small">Batch 2 untreated</text>
    <rect x="394" y="535" width="9.6" height="9.6" fill="{RED}"/>
    <text x="410" y="545" class="small">Drug A (both batches)</text>
    <polygon points="572,534 566,545 578,545" fill="{GREEN}"/>
    <text x="584" y="545" class="small">Drug B (both batches)</text>

    <!-- Experimental context callout -->
    <rect x="84" y="572" width="636" height="228" rx="8" fill="{BLUE_LIGHT}" stroke="{BLUE}" stroke-width="1.2"/>
    <text x="108" y="604" class="label" fill="{BLUE}">Why standard E. coli profiling and CNNs failed on M. tuberculosis</text>
    <text x="108" y="634" class="body">• Mtb has a thick, waxy cell envelope (speaker: ~30× thicker than E. coli); imaging</text>
    <text x="122" y="656" class="body">showed uneven dye uptake, dark unstained cells, batch drift, and subtle shifts.</text>
    <text x="108" y="686" class="body">• The lab reported dedicating 25% of its imaging time to untreated controls across</text>
    <text x="122" y="708" class="body">biological and technical replicates (recording, 1:01:38).</text>
    <text x="108" y="738" class="body">• ~25 base metrics expand via median, Q1, Q3, IQR (~100/dose; ~200 paired low+high)</text>
    <text x="122" y="760" class="body">to represent single-cell heterogeneity explicitly before feature pruning.</text>

    <!-- Right Panel: MorphEUS 70-trial c-kNN -->
    <rect x="774" y="124" width="770" height="700" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>
    <text x="802" y="164" class="panel-title">B. MorphEUS: 70-Trial Stochastic Consensus (c-kNN)</text>
    <text x="802" y="190" class="small">Workflow from Part B p. 16 (Smith et al., PNAS 2020): resample controls to stabilize TVN</text>

    <!-- Flow Step 1 -->
    <rect x="820" y="216" width="676" height="74" rx="8" fill="{PANEL_ALT}" stroke="{BORDER}" stroke-width="1.2"/>
    <text x="844" y="246" class="label">1. Feature Quantification (~10,000 cells / treatment, low + high dose)</text>
    <text x="844" y="272" class="small">Segment single cells → filter out-of-focus cells → compute ~100 quartile features/dose</text>

    {arrow_line(1158, 290, 1158, 326, INK, width=2.0, size=10.0, half_w=5.0)}

    <!-- 70-trial dashed container matching l20b p. 16 order -->
    <rect x="820" y="328" width="676" height="206" rx="10" fill="{GOLD_LIGHT}" fill-opacity="0.55" stroke="{GOLD}" stroke-width="1.6" stroke-dasharray="6,4"/>
    <text x="844" y="358" class="label" fill="{GOLD}">2. Repeat 70 Stochastic Classification Trials (Part B p. 16)</text>

    <rect x="844" y="378" width="186" height="128" rx="7" fill="{CARD}" stroke="{GOLD}" stroke-width="1.2"/>
    <text x="937" y="408" text-anchor="middle" class="label">Resample Controls</text>
    <text x="937" y="434" text-anchor="middle" class="small">Draw untreated subset</text>
    <text x="937" y="454" text-anchor="middle" class="small">from control pool</text>
    <text x="937" y="476" text-anchor="middle" class="small">for this trial</text>

    {arrow_line(1030, 442, 1062, 442, INK, width=1.8, size=9.0, half_w=4.5)}

    <rect x="1064" y="378" width="194" height="128" rx="7" fill="{CARD}" stroke="{GOLD}" stroke-width="1.2"/>
    <text x="1161" y="408" text-anchor="middle" class="label">mRMR + TVN</text>
    <text x="1161" y="434" text-anchor="middle" class="small">Rank features (mRMR)</text>
    <text x="1161" y="454" text-anchor="middle" class="small">and apply TVN inside</text>
    <text x="1161" y="476" text-anchor="middle" class="small">selection loop</text>

    {arrow_line(1258, 442, 1290, 442, INK, width=1.8, size=9.0, half_w=4.5)}

    <rect x="1292" y="378" width="184" height="128" rx="7" fill="{CARD}" stroke="{GOLD}" stroke-width="1.2"/>
    <text x="1384" y="408" text-anchor="middle" class="label">k-NN + Prune</text>
    <text x="1384" y="434" text-anchor="middle" class="small">k-NN in PCA space;</text>
    <text x="1384" y="454" text-anchor="middle" class="small">backward selection</text>
    <text x="1384" y="476" text-anchor="middle" class="small">(~35–40 features kept)</text>

    {arrow_line(1158, 534, 1158, 568, INK, width=2.0, size=10.0, half_w=5.0)}

    <rect x="820" y="570" width="676" height="82" rx="8" fill="{GREEN_LIGHT}" stroke="{GREEN}" stroke-width="1.5"/>
    <text x="844" y="600" class="label" fill="{GREEN}">3. Consensus Classification (c-kNN: 34 TB drugs, 5 MoA classes)</text>
    <text x="844" y="628" class="body">Tabulate 70 trials → 94% reference accuracy, 76% cross-validation accuracy (Part B p. 18).</text>

    <!-- Bedaquiline Discovery Box -->
    <rect x="820" y="676" width="676" height="124" rx="8" fill="{RED_LIGHT}" stroke="{RED}" stroke-width="1.2"/>
    <text x="844" y="706" class="label" fill="{RED}">Investigator Interpretation: The Bedaquiline Paradox (Part B pp. 20–22)</text>
    <text x="844" y="734" class="body">• Bedaquiline (ATP synthase inhibitor) clustered with cell-wall drugs in rich sugar media.</text>
    <text x="844" y="758" class="body">• On fatty acids, that resemblance vanished: investigators attributed the sugar</text>
    <text x="858" y="780" class="body">phenotype to ATP depletion causing secondary cell-wall failure (proximal damage).</text>
    '''
    svg = svg_wrap(
        "Handling Batch and Cell Heterogeneity in M. tuberculosis (MorphEUS)",
        "MIT 6.874 Lecture 20 (Part B · Bree Aldridge): why TVN, quartile features, and 70-trial consensus k-NN beat black-box CNNs",
        body,
        "Panel A: constructed 2D unregularized TVN illustration (after Ando et al., bioRxiv 2017). Panel B: reported MorphEUS workflow and metrics (Part B pp. 14–22; Smith et al., PNAS 2020)."
    )
    ET.fromstring(svg)
    (OUT / "morpheus-tvn-pipeline.svg").write_text(svg)
    return cov_err


# ---------------------------------------------------------------------------
# FIGURE 3: DiaMOND Geometric Optimization & Combinatorial Scaling
# ---------------------------------------------------------------------------
def build_fig3():
    # Left panel: 2D IC90-normalized Dose Space (scale = 320 px per unit)
    ox, oy = 140, 660
    scale = 320

    def pt(x, y):
        return ox + x * scale, oy - y * scale

    x0, y0 = pt(0, 0)
    x1, y1 = pt(1.0, 0)
    x2, y2 = pt(0, 1.0)
    xe, ye = pt(0.5, 0.5)
    xs, ys = pt(0.25, 0.25)
    xa, ya = pt(0.75, 0.75)
    xd, yd = pt(1.12, 1.12)

    grid = []
    for t in [0.25, 0.50, 0.75, 1.00]:
        gx, gy = pt(t, t)
        grid.append(f'<line x1="{gx:.1f}" y1="{oy}" x2="{gx:.1f}" y2="{oy - 372}" stroke="{BORDER}" stroke-dasharray="3,4" stroke-width="1"/>')
        grid.append(f'<line x1="{ox}" y1="{gy:.1f}" x2="{ox + 372}" y2="{gy:.1f}" stroke="{BORDER}" stroke-dasharray="3,4" stroke-width="1"/>')
        grid.append(f'<text x="{gx:.1f}" y="{oy + 22}" text-anchor="middle" class="small">{t:.2f}</text>')
        grid.append(f'<text x="{ox - 12}" y="{gy + 5:.1f}" text-anchor="end" class="small">{t:.2f}</text>')

    # Exact Bezier control points: (0,0) for synergy -> B(0.5)=(0.25, 0.25); (1,1) for antagonism -> B(0.5)=(0.75, 0.75)
    c_syn = pt(0.0, 0.0)
    c_ant = pt(1.0, 1.0)
    syn_path = f"M {x2:.1f} {y2:.1f} Q {c_syn[0]:.1f} {c_syn[1]:.1f} {x1:.1f} {y1:.1f}"
    ant_path = f"M {x2:.1f} {y2:.1f} Q {c_ant[0]:.1f} {c_ant[1]:.1f} {x1:.1f} {y1:.1f}"

    # Verify clearance of right-side legend cards at x=486..704, y in [380, 466, 552]
    ts = [i / 400.0 for i in range(401)]
    curve_samples = (
        [pt(*qbezier((0.0, 1.0), (0.0, 0.0), (1.0, 0.0), t)) for t in ts]
        + [pt(*qbezier((0.0, 1.0), (1.0, 1.0), (1.0, 0.0), t)) for t in ts]
        + [pt(t, 1.0 - t) for t in ts]
        + [pt(1.12 * t, 1.12 * t) for t in ts]
    )
    for card_y in [380, 462, 544]:
        for sx, sy in curve_samples:
            cx = max(486.0, min(sx, 704.0))
            cy = max(float(card_y), min(sy, float(card_y + 58)))
            assert math.hypot(sx - cx, sy - cy) >= 18.0, f"Card at y={card_y} too close to curve ({sx:.1f},{sy:.1f})"

    # Right panel: Strictly proportional checkerboard bar chart (2-way: 1, 3-way: 3, 4-way: 25)
    plate_bars = [
        ("2-way\n(1 plate)", 1, BLUE, 882),
        ("3-way\n(3 plates)", 3, GOLD, 1034),
        ("4-way\n(25 plates)", 25, RED, 1186),
    ]
    base_y = 480
    px_per_plate = 9.0  # 25 * 9.0 = 225 px
    p_svg = []
    p_svg.append(f'<line x1="820" y1="{base_y}" x2="1280" y2="{base_y}" stroke="{INK}" stroke-width="1.5"/>')
    p_svg.append(f'<line x1="820" y1="235" x2="820" y2="{base_y}" stroke="{INK}" stroke-width="1.5"/>')
    for tick in [0, 5, 10, 15, 20, 25]:
        ty = base_y - tick * px_per_plate
        p_svg.append(f'<line x1="820" y1="{ty:.1f}" x2="1280" y2="{ty:.1f}" stroke="{BORDER}" stroke-dasharray="3,4" stroke-width="1"/>')
        p_svg.append(f'<text x="810" y="{ty + 5:.1f}" text-anchor="end" class="small">{tick}</text>')
    p_svg.append('<text x="782" y="362" transform="rotate(-90 782 362)" text-anchor="middle" class="small">384-well plates / replicate</text>')

    for lbl, cnt, col, cx in plate_bars:
        bh = cnt * px_per_plate
        top = base_y - bh
        p_svg.append(f'<rect x="{cx - 40}" y="{top:.1f}" width="80" height="{bh:.1f}" rx="3" fill="{col}" fill-opacity="0.88"/>')
        p_svg.append(f'<text x="{cx}" y="{top - 9:.1f}" text-anchor="middle" class="num" fill="{col}">{cnt}</text>')
        for i, l in enumerate(lbl.split("\n")):
            p_svg.append(f'<text x="{cx}" y="{base_y + 22 + i * 18}" text-anchor="middle" class="small" fill="{INK}">{l}</text>')

    # Separate DiaMOND callout badge off the numeric y-axis (fixes Codex M7)
    p_svg.append(f'<rect x="1302" y="256" width="214" height="224" rx="8" fill="{GREEN_LIGHT}" stroke="{GREEN}" stroke-width="1.5"/>')
    p_svg.append(f'<text x="1409" y="292" text-anchor="middle" class="label" fill="{GREEN}">DiaMOND Design</text>')
    p_svg.append(f'<text x="1409" y="320" text-anchor="middle" class="small" fill="{INK}">Instead of full N-D grids,</text>')
    p_svg.append(f'<text x="1409" y="340" text-anchor="middle" class="small" fill="{INK}">measure only:</text>')
    p_svg.append(f'<text x="1409" y="370" text-anchor="middle" class="small" fill="{GREEN}" font-weight="700">• N single-drug axes</text>')
    p_svg.append(f'<text x="1409" y="392" text-anchor="middle" class="small" fill="{GREEN}" font-weight="700">• 1 equal-fraction ray</text>')
    p_svg.append(f'<text x="1409" y="426" text-anchor="middle" class="small" fill="{MUTED}">Preserves dose-response</text>')
    p_svg.append(f'<text x="1409" y="446" text-anchor="middle" class="small" fill="{MUTED}">curves for both potency</text>')
    p_svg.append(f'<text x="1409" y="466" text-anchor="middle" class="small" fill="{MUTED}">&amp; FIC scoring</text>')

    body = f'''
    <!-- Left Panel: 2D DiaMOND Geometry -->
    <rect x="56" y="124" width="670" height="700" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>
    <text x="84" y="164" class="panel-title">A. DiaMOND Equipotent Geometry (Constructed Check)</text>
    <text x="84" y="190" class="small">Normalized IC<tspan baseline-shift="sub" font-size="10">90</tspan> space: FIC = r<tspan baseline-shift="sub" font-size="10">obs</tspan> / r<tspan baseline-shift="sub" font-size="10">exp</tspan> along 1:1 mixture ray (r<tspan baseline-shift="sub" font-size="10">exp</tspan> = 1/√2 ≈ 0.707)</text>

    {"".join(grid)}
    <!-- Axes with explicit polygon arrowheads -->
    {arrow_line(ox, oy, ox + 392, oy, INK, width=2.0, size=10.0, half_w=5.0)}
    {arrow_line(ox, oy, ox, oy - 392, INK, width=2.0, size=10.0, half_w=5.0)}
    <text x="{ox + 185}" y="{oy + 52}" text-anchor="middle" class="label">Drug X Dose (normalized to IC<tspan baseline-shift="sub" font-size="11">90,X</tspan> = 1.0)</text>
    <text x="84" y="{oy - 185}" transform="rotate(-90 84 {oy - 185})" text-anchor="middle" class="label">Drug Y Dose (normalized to IC<tspan baseline-shift="sub" font-size="11">90,Y</tspan> = 1.0)</text>

    <!-- Diagonal ray -->
    <line x1="{x0}" y1="{y0}" x2="{xd:.1f}" y2="{yd:.1f}" stroke="{BLUE}" stroke-width="2.2" stroke-dasharray="7,4"/>
    <text x="{xd - 6:.1f}" y="{yd - 12:.1f}" text-anchor="end" class="small" fill="{BLUE}" font-weight="700">1:1 mixture ray</text>

    <!-- Additivity line -->
    <line x1="{x2:.1f}" y1="{y2:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{INK}" stroke-width="2.2"/>
    <!-- Synergy & Antagonism contours passing EXACTLY through (0.25,0.25) and (0.75,0.75) -->
    <path d="{syn_path}" fill="none" stroke="{GREEN}" stroke-width="2.6"/>
    <path d="{ant_path}" fill="none" stroke="{RED}" stroke-width="2.6"/>

    <!-- Single-drug IC90 intercepts -->
    <circle cx="{x1:.1f}" cy="{y1:.1f}" r="6.2" fill="{CARD}" stroke="{INK}" stroke-width="2.2"/>
    <circle cx="{x2:.1f}" cy="{y2:.1f}" r="6.2" fill="{CARD}" stroke="{INK}" stroke-width="2.2"/>

    <!-- Diagonal intersection points -->
    <circle cx="{xs:.1f}" cy="{ys:.1f}" r="6.8" fill="{GREEN}"/>
    <circle cx="{xe:.1f}" cy="{ye:.1f}" r="6.8" fill="{INK}"/>
    <circle cx="{xa:.1f}" cy="{ya:.1f}" r="6.8" fill="{RED}"/>

    <!-- Non-overlapping right-column worked-example cards with matching marker dots -->
    <rect x="486" y="380" width="218" height="58" rx="7" fill="{RED_LIGHT}" stroke="{RED}" stroke-width="1.2"/>
    <circle cx="503" cy="400" r="5.5" fill="{RED}"/>
    <text x="516" y="405" class="small" fill="{RED}" font-weight="700">Antagonism: (0.75, 0.75)</text>
    <text x="503" y="426" class="small" fill="{RED}">FIC = 1.50 &gt; 1 (above line)</text>

    <rect x="486" y="462" width="218" height="58" rx="7" fill="{PANEL_ALT}" stroke="{INK}" stroke-width="1.2"/>
    <circle cx="503" cy="482" r="5.5" fill="{INK}"/>
    <text x="516" y="487" class="small" fill="{INK}" font-weight="700">Additive: (0.50, 0.50)</text>
    <text x="503" y="508" class="small" fill="{INK}">FIC = 1.00 (on additivity line)</text>

    <rect x="486" y="544" width="218" height="58" rx="7" fill="{GREEN_LIGHT}" stroke="{GREEN}" stroke-width="1.2"/>
    <circle cx="503" cy="564" r="5.5" fill="{GREEN}"/>
    <text x="516" y="569" class="small" fill="{GREEN}" font-weight="700">Synergy: (0.25, 0.25)</text>
    <text x="503" y="590" class="small" fill="{GREEN}">FIC = 0.50 &lt; 1 (below line)</text>

    <text x="84" y="756" class="small">Note: one equipotent ray tests FIC at equal normalized fractions; off-ray asymmetric</text>
    <text x="84" y="776" class="small">ratios require extra rays. In N dimensions, the additivity line becomes a hyperplane.</text>

    <!-- Right Panel: Scaling & In-Vivo Finding -->
    <rect x="752" y="124" width="792" height="700" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>
    <text x="780" y="164" class="panel-title">B. Checkerboard Scaling &amp; BALB/c Mouse Findings</text>
    <text x="780" y="190" class="small">Lecture checkerboard example (384-well plates / replicate) vs. DiaMOND 175-regimen TB screen</text>

    {"".join(p_svg)}

    <!-- Findings Box -->
    <rect x="780" y="556" width="736" height="244" rx="8" fill="{PANEL_ALT}" stroke="{BORDER}" stroke-width="1.2"/>
    <text x="804" y="586" class="label">Reported Empirical Findings (Part B pp. 28–36; Larkins-Ford et al., 2021)</text>
    <text x="804" y="616" class="body">• Combinatorial space: 20 TB drugs yield C(20, 3) = 1,140 three-drug regimens.</text>
    <text x="804" y="644" class="body">• DiaMOND tested 10 drugs: 175 regimens (10 single + 165 multidrug: 45 pairs, 120 triples)</text>
    <text x="818" y="666" class="body">across 8 growth environments (&gt;50,000 dynamic dose-response curves).</text>
    <text x="804" y="696" class="body" fill="{RED}" font-weight="600">• No single combination was synergistic across all 8 growth environments.</text>
    <text x="804" y="726" class="body" fill="{GREEN}" font-weight="600">• On 27 train / 19 test regimens in BALB/c mice (C1 better than SOC vs. C0 SOC or worse),</text>
    <text x="818" y="748" class="body" fill="{GREEN}" font-weight="600">potency (E<tspan baseline-shift="sub" font-size="10.5">inf</tspan>, GR<tspan baseline-shift="sub" font-size="10.5">inf</tspan>, AUC<tspan baseline-shift="sub" font-size="10.5">25</tspan>) in lipid-rich &amp; acidic media drove PCA + RF separation.</text>
    <text x="804" y="778" class="small">Top small-condition Random Forest models reached test AUC 0.75–0.94 (Part B p. 36).</text>
    '''
    svg = svg_wrap(
        "DiaMOND: Measuring High-Order Drug Combinations Without Full Checkerboards",
        "MIT 6.874 Lecture 20 (Part B · Bree Aldridge): geometric reduction of N-way dose space and in vitro potency predictors",
        body,
        "Panel A: constructed IC<tspan baseline-shift=\"sub\" font-size=\"9.5\">90</tspan>-normalized worked check (r<tspan baseline-shift=\"sub\" font-size=\"9.5\">exp</tspan> = 0.707; r<tspan baseline-shift=\"sub\" font-size=\"9.5\">obs</tspan> = 0.354, 1.061). Panel B: reported plate example &amp; BALB/c results (Part B pp. 25–36; Cokol et al. 2017; Larkins-Ford et al. 2021)."
    )
    ET.fromstring(svg)
    (OUT / "diamond-geometry.svg").write_text(svg)


def rasterize_all():
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    for stem in ["hybrid-pathology-pipeline", "morpheus-tvn-pipeline", "diamond-geometry"]:
        svg_path = OUT / f"{stem}.svg"
        png_path = OUT / f"{stem}.png"
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--force-device-scale-factor=1",
                "--hide-scrollbars",
                f"--window-size={W},{H}",
                f"--screenshot={png_path}",
                svg_path.as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        res = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(png_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        assert f"pixelWidth: {W}" in res.stdout and f"pixelHeight: {H}" in res.stdout, res.stdout
        print(f"Rendered {png_path.name}: {res.stdout.strip().replace(chr(10), ' | ')}")


if __name__ == "__main__":
    build_fig1()
    tvn_cov_err = build_fig2()
    build_fig3()
    rasterize_all()
    manifest = {
        "lecture": "MIT 6.874 Spring 2021 — Lecture 20: Imaging applications in healthcare",
        "version": "v1 r3",
        "figures": [
            "hybrid-pathology-pipeline.png",
            "morpheus-tvn-pipeline.png",
            "diamond-geometry.png",
        ],
        "verified_math": {
            "collagen_entropy_aligned_bits": round(H_aligned, 6) + 0.0,
            "collagen_entropy_disordered_4bin_bits": round(H_disordered, 6),
            "collagen_disordered_svg_bin_counts": bin_counts,
            "tvn_schematic_whitened_ctrl_cov_max_err": tvn_cov_err,
            "tb_20_choose_3": n_20_choose_3,
            "diamond_10_drugs_single": n_10_single,
            "diamond_10_drugs_pairwise": n_10_pair,
            "diamond_10_drugs_three_way": n_10_triple,
            "diamond_10_drugs_multidrug_combos": n_10_multidrug,
            "diamond_10_drugs_total_regimens": n_10_total,
            "diamond_worked_fic": {
                "r_exp": round(r_exp, 6),
                "r_obs_synergy": round(r_obs_syn, 6),
                "r_obs_antagonism": round(r_obs_ant, 6),
                "synergy": round(fic_syn, 6),
                "additive": round(fic_add, 6),
                "antagonism": round(fic_ant, 6),
            },
            "diamond_bezier_midpoints_verified": True,
        },
        "palette": {
            "background": BG,
            "ink": INK,
            "blue": BLUE,
            "terracotta": RED,
            "sage": GREEN,
            "ochre": GOLD,
        },
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("ALL FIGURES AND MANIFEST GENERATED SUCCESSFULLY.")
