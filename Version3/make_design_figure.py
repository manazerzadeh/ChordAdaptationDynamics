"""Experiment-design figure for Version 3 (index/ring chord adaptation).

Panel a: the trial screen, with the cursor perturbation that is the manipulation.
Panel b: the eight chord conditions.
Panel c: the perturbation schedule (i.i.d. zero-mean noise per finger, per trial).
Panel d: block timeline of the four sessions (16 blocks, 1120 trials).

Outputs Figs/fig_design_v3.{pdf,png}.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import to_rgb
from matplotlib.patches import FancyArrowPatch, Rectangle

# utils.py imports pingouin/statsmodels, which this figure does not need; fall back
# to the same literals if those packages are missing.
try:
    import utils
    N_BASE = utils.num_trials_baseline            # 20
    N_PERT = utils.num_trials_per_block           # 120
    N_SESSIONS = utils.num_sessions               # 4
    BLOCKS_PER_SESSION = utils.num_blocks_first_session   # 4 -> 2 chords per session
    set_figure_style = utils.set_figure_style
except ImportError:
    N_BASE, N_PERT, N_SESSIONS, BLOCKS_PER_SESSION = 20, 120, 4, 4

    def set_figure_style(scale="2col"):
        width_in = {"1col": 7.62, "1.5col": 11.6, "2col": 16.5}[scale] * 0.393701
        plt.rcParams.update({
            "figure.figsize": (width_in, width_in * (5 ** 0.5 - 1) / 2),
            "font.size": 10, "axes.titlesize": 12, "axes.labelsize": 9,
            "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 8,
            "figure.titleweight": "bold", "axes.linewidth": 0.75,
            "xtick.major.width": 0.75, "ytick.major.width": 0.75,
            "text.usetex": False, "axes.formatter.use_mathtext": True,
        })

OUT = Path("./Figs")
OUT.mkdir(parents=True, exist_ok=True)

# --- design constants (utils.py / TargetFileMaker.ipynb) ------------------
INDEX, RING = 2, 4                       # 1-based finger ids
AMP = 2.0                                # +-2 N targets
PERT_SD = 0.5                            # purturbation_std, N

# the eight conditions, as (index target, ring target); None = finger at rest
CONDITIONS = [(+AMP, None), (-AMP, None), (None, +AMP), (None, -AMP),
              (+AMP, +AMP), (+AMP, -AMP), (-AMP, +AMP), (-AMP, -AMP)]

# example participant's chord order; shuffled per participant
CHORD_ORDER = [5, 0, 7, 2, 4, 1, 6, 3]


def chord_string(idx, ring):
    """Repo notation: five characters, ^ extend / v flex / - rest."""
    sym = {None: "-", +AMP: "^", -AMP: "v"}
    return f"-{sym[idx]}-{sym[ring]}-"


# --- palette --------------------------------------------------------------
cb = sns.color_palette("colorblind")


def blend(color, alpha, bg=(1, 1, 1)):
    c = np.asarray(to_rgb(color))
    return tuple(alpha * c + (1 - alpha) * np.asarray(bg))


INDEX_COL, RING_COL = cb[0], cb[1]
BASE_COL, BASE_EDGE = "#d9d9d9", "#6e6e6e"
PERT_COL, PERT_EDGE = blend(cb[2], 0.85), "#04624c"

SCREEN_BG = "black"
ZERO_BAR = "#cdcdcd"
BOX_DIM_FACE, BOX_DIM_EDGE = "#232323", "#3a3a3a"
BOX_ON_FACE, BOX_ON_EDGE = "#6f6f6f", "#ffffff"
CURSOR = "#d92b2b"
NOTE = "#5a5a5a"
IN_SCREEN = "#9a9a9a"

SCREEN_YLIM = (-3.5, 3.5)
COL_X = {INDEX: 0.30, RING: 0.70}
BOX_W = 0.30


# --- panel a: the trial screen -------------------------------------------
def draw_screen(ax, idx_target, ring_target, idx_pert, ring_pert):
    ax.set_facecolor(SCREEN_BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(*SCREEN_YLIM)
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)

    ax.add_patch(Rectangle((0.03, -0.55), 0.94, 1.10, facecolor=ZERO_BAR,
                           edgecolor="none", zorder=1))

    for finger, target, pert in ((INDEX, idx_target, idx_pert),
                                 (RING, ring_target, ring_pert)):
        if target is None:                            # finger rests, nothing drawn
            continue
        cx = COL_X[finger]
        ax.add_patch(Rectangle((cx - BOX_W / 2, target - 0.26), BOX_W, 0.52,
                               facecolor=BOX_ON_FACE, edgecolor=BOX_ON_EDGE,
                               lw=1.1, zorder=2))
        # the cursor is drawn at the produced force plus the perturbation
        cursor = target + pert
        ax.plot([cx - BOX_W / 2 - 0.02, cx + BOX_W / 2 + 0.02], [cursor, cursor],
                color=CURSOR, lw=2.0, zorder=4, solid_capstyle="butt")

        # perturbation arrow, drawn in the gap between the columns
        side = 1 if finger == INDEX else -1
        ax_x = cx + side * (BOX_W / 2 + 0.02)
        ax.add_patch(FancyArrowPatch((ax_x, target), (ax_x, cursor), mutation_scale=6,
                                     arrowstyle="-|>", lw=1.1, color="#e8a0a0", zorder=5))
        lab = "$p_{index}$" if finger == INDEX else "$p_{ring}$"
        ax.text(ax_x + side * 0.04, target + pert / 2, lab, color="#e8a0a0", fontsize=6.3,
                ha="left" if side > 0 else "right", va="center", zorder=5)

    ax.set_yticks([-AMP, 0, AMP])
    ax.set_yticklabels(["−2", "0", "+2"], fontsize=7)
    ax.set_ylabel("Force (N)", fontsize=8, labelpad=3)
    ax.tick_params(axis="y", length=2.5, width=0.7, pad=2)

    for finger, col, name in ((INDEX, INDEX_COL, "index"), (RING, RING_COL, "ring")):
        ax.text(COL_X[finger], -3.15, name, color=col, fontsize=7, fontweight="bold",
                ha="center", va="center", zorder=5)


# --- panel b: the eight chord conditions ---------------------------------
def draw_conditions(ax):
    ax.set_xlim(0, 4)
    ax.set_ylim(-1.0, 10.2)
    ax.axis("off")

    row_cy = (7.4, 1.9)          # rest line of each row
    off = 1.15                   # target boxes sit this far above / below it

    for k, (idx_t, ring_t) in enumerate(CONDITIONS):
        col, row = k % 4, k // 4
        cx, cy = 0.5 + col, row_cy[row]

        ax.plot([cx - 0.38, cx + 0.38], [cy, cy], color="#c8c8c8", lw=0.8, zorder=1)
        for dx, target, fcol in ((-0.16, idx_t, INDEX_COL), (0.16, ring_t, RING_COL)):
            if target is None:
                ax.plot([cx + dx], [cy], marker="o", ms=2.4, color="#c8c8c8", zorder=2)
                continue
            y = cy + off * np.sign(target)
            ax.add_patch(Rectangle((cx + dx - 0.115, y - 0.35), 0.23, 0.70,
                                   facecolor=fcol, edgecolor="none", zorder=3))
        ax.text(cx, cy - 2.15, chord_string(idx_t, ring_t), fontsize=6.6,
                family="monospace", ha="center", va="center")

    ax.text(0.02, 10.1, "one finger  (4)", fontsize=7, color=NOTE, ha="left", va="top")
    ax.text(0.02, 4.35, "two fingers  (4)", fontsize=7, color=NOTE, ha="left", va="top")


# --- panel c: the perturbation schedule ----------------------------------
def draw_perturbation(ax):
    rng = np.random.default_rng(7)
    trials = np.arange(1, N_PERT + 1)
    p_idx = rng.normal(0, PERT_SD, N_PERT)
    p_ring = rng.normal(0, PERT_SD, N_PERT)

    ax.set_xlim(0, 152)
    ax.set_ylim(-2.3, 2.3)
    ax.axhspan(-PERT_SD, PERT_SD, color="#ededed", zorder=0)
    ax.axhline(0, color="#b0b0b0", lw=0.7, zorder=1)
    ax.plot(trials, p_idx, color=INDEX_COL, lw=0.7, zorder=3)
    ax.plot(trials, p_ring, color=RING_COL, lw=0.7, zorder=3)

    # marginal density, drawn sideways at the right edge
    y = np.linspace(-2.1, 2.1, 200)
    pdf = np.exp(-0.5 * (y / PERT_SD) ** 2)
    ax.fill_betweenx(y, 124, 124 + 24 * pdf, facecolor="#e6e6e6", edgecolor="none",
                     zorder=2)
    ax.plot(124 + 24 * pdf, y, color="#9a9a9a", lw=0.7, zorder=3)
    ax.text(150, 1.05, f"σ = {PERT_SD} N", fontsize=6.3, color=NOTE, ha="right",
            va="bottom")

    ax.text(2, 1.95, "added to each finger's cursor,\nindependently, on every trial",
            fontsize=6.3, color=NOTE, ha="left", va="top", linespacing=1.35)

    ax.set_xticks([1, 60, 120])
    ax.set_xticklabels(["1", "60", "120"], fontsize=7)
    ax.set_yticks([-1, 0, 1])
    ax.set_yticklabels(["−1", "0", "+1"], fontsize=7)
    ax.set_xlabel("Trial in perturbed block", fontsize=8, labelpad=2)
    ax.set_ylabel("Cursor perturbation (N)", fontsize=8, labelpad=2)
    ax.tick_params(length=2.5, width=0.7, pad=2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_position(("outward", 3))
    ax.spines["bottom"].set_position(("outward", 3))


def main():
    set_figure_style("2col")
    plt.rcParams["font.size"] = 8

    fig = plt.figure(figsize=(6.93, 5.85))
    gs_top = fig.add_gridspec(1, 3, width_ratios=[0.90, 1.55, 1.45],
                              left=0.075, right=0.985, top=0.920, bottom=0.605,
                              wspace=0.42)
    gs_bot = fig.add_gridspec(2, 1, height_ratios=[0.45, 1.55], left=0.075,
                              right=0.985, top=0.385, bottom=0.055, hspace=0.10)

    # ---------------- panels a-c ----------------
    ax_s = fig.add_subplot(gs_top[0, 0])
    draw_screen(ax_s, idx_target=+AMP, ring_target=-AMP, idx_pert=+0.55, ring_pert=+0.45)
    ax_s.text(0.5, 1.045, "Trial screen", transform=ax_s.transAxes, fontsize=9.5,
              fontweight="bold", ha="center", va="bottom")
    ax_s.text(0.5, -0.035, "one chord per block\ncursor = force + perturbation",
              transform=ax_s.transAxes, fontsize=6.8, color=NOTE, ha="center", va="top",
              linespacing=1.45)

    ax_c = fig.add_subplot(gs_top[0, 1])
    draw_conditions(ax_c)
    ax_c.text(0.5, 1.045, "Eight chord conditions", transform=ax_c.transAxes,
              fontsize=9.5, fontweight="bold", ha="center", va="bottom")
    ax_c.text(0.5, -0.035, "index and ring, ±2 N\n^ extend · v flex · − rest",
              transform=ax_c.transAxes, fontsize=6.8, color=NOTE, ha="center", va="top",
              linespacing=1.45)

    ax_p = fig.add_subplot(gs_top[0, 2])
    draw_perturbation(ax_p)
    ax_p.text(0.5, 1.045, "Perturbation", transform=ax_p.transAxes, fontsize=9.5,
              fontweight="bold", ha="center", va="bottom")

    # ---------------- panel d: blocks ----------------
    blocks = []          # (start, n_trials, kind, chord index, session)
    x = 0
    for k, cond in enumerate(CHORD_ORDER):
        session = k // 2
        for kind, n in (("baseline", N_BASE), ("perturbed", N_PERT)):
            blocks.append((x, n, kind, cond, session))
            x += n
    total = x

    # perturbation-size trace, the analogue of the gain trace in the V2 figure
    ax_g = fig.add_subplot(gs_bot[0])
    xs, ys = [], []
    for start, n, kind, _, _ in blocks:
        s = PERT_SD if kind == "perturbed" else 0.0
        xs += [start, start + n]
        ys += [s, s]
    ax_g.step(xs, ys, where="post", color="#333333", lw=1.1)
    ax_g.fill_between(xs, 0, ys, step="post", color=blend(cb[2], 0.25), lw=0)
    ax_g.set_xlim(-10, total + 10)
    ax_g.set_ylim(-0.08, 0.72)
    ax_g.set_yticks([0, PERT_SD])
    ax_g.set_yticklabels(["0", "0.5"], fontsize=7)
    ax_g.set_ylabel("Pert.\nσ (N)", fontsize=7.5, labelpad=3, linespacing=1.25)
    ax_g.set_xticks([])
    ax_g.tick_params(axis="y", length=2.5, width=0.7, pad=2)
    for sp in ("top", "right", "bottom"):
        ax_g.spines[sp].set_visible(False)

    ax_t = fig.add_subplot(gs_bot[1])
    ax_t.set_xlim(-10, total + 10)
    ax_t.set_ylim(-1.05, 1.25)
    ax_t.axis("off")

    top, h = 0.42, 0.50
    for i, (start, n, kind, cond, _) in enumerate(blocks):
        ax_t.add_patch(Rectangle((start, top), n, h,
                                 facecolor=BASE_COL if kind == "baseline" else PERT_COL,
                                 edgecolor=BASE_EDGE if kind == "baseline" else PERT_EDGE,
                                 lw=0.7, zorder=2))
        if i < 2:
            ax_t.text(start + n / 2, top + h + 0.05, f"{n}", fontsize=6.5, color=NOTE,
                      ha="center", va="bottom")
    ax_t.text(blocks[1][0] + N_PERT + 24, top + h + 0.05, "trials", fontsize=6.5,
              color=NOTE, ha="left", va="bottom", style="italic")

    # chord run under each baseline+perturbed pair
    for k, cond in enumerate(CHORD_ORDER):
        x0 = k * (N_BASE + N_PERT)
        mid = x0 + (N_BASE + N_PERT) / 2
        idx_t, ring_t = CONDITIONS[cond]
        ax_t.text(mid, 0.30, chord_string(idx_t, ring_t), fontsize=6.6,
                  family="monospace", ha="center", va="top")

    # session brackets, two chords each
    per_session = 2 * (N_BASE + N_PERT)
    for s in range(N_SESSIONS):
        x0, x1 = s * per_session + 4, (s + 1) * per_session - 4
        mid = (x0 + x1) / 2
        ax_t.plot([x0, x1], [0.06, 0.06], color="#8c8c8c", lw=0.8, solid_capstyle="butt")
        for xe in (x0, x1):
            ax_t.plot([xe, xe], [0.06, 0.14], color="#8c8c8c", lw=0.8)
        ax_t.text(mid, -0.07, f"Session {s + 1}", fontsize=7.5, ha="center", va="top")

    ax_t.annotate("", xy=(total, -0.55), xytext=(0, -0.55),
                  arrowprops=dict(arrowstyle="-|>", lw=0.9, color="#4d4d4d"))
    ax_t.text(0, -0.67, "trial", fontsize=7, color=NOTE, ha="left", va="top")
    ax_t.text(total, -0.67,
              f"{N_SESSIONS} sessions · {N_SESSIONS * BLOCKS_PER_SESSION} blocks "
              f"· {total} trials",
              fontsize=7, color=NOTE, ha="right", va="top")
    ax_t.text(total, -0.88, "chord order randomised across participants",
              fontsize=6.5, color=NOTE, ha="right", va="top", style="italic")

    handles = [Rectangle((0, 0), 1, 1, facecolor=BASE_COL, edgecolor=BASE_EDGE, lw=0.8),
               Rectangle((0, 0), 1, 1, facecolor=PERT_COL, edgecolor=PERT_EDGE, lw=0.8)]
    labels = [f"Baseline  (no perturbation, {N_BASE} trials)",
              f"Perturbed  (σ = {PERT_SD} N, {N_PERT} trials)"]
    ax_g.legend(handles, labels, loc="lower left", bbox_to_anchor=(0.0, 1.45),
                ncol=2, frameon=False, fontsize=7.2, handlelength=1.6,
                handleheight=0.95, columnspacing=1.8, borderpad=0.0)

    fig.canvas.draw()
    for ax, letter, dx in ((ax_s, "a", 0.068), (ax_c, "b", 0.052), (ax_p, "c", 0.062)):
        fig.text(ax.get_position().x0 - dx, ax.get_position().y1 + 0.075, letter,
                 fontsize=13, fontweight="bold", va="top")
    fig.text(0.007, ax_g.get_position().y1 + 0.085, "d", fontsize=13,
             fontweight="bold", va="top")

    for ext in (".pdf", ".png"):
        fig.savefig(OUT / f"fig_design_v3{ext}", dpi=300, facecolor="white",
                    bbox_inches="tight")
    print("wrote", OUT / "fig_design_v3.pdf", "and .png")


if __name__ == "__main__":
    main()
