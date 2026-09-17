"""Experiment-design figure for Single-Finger Gain Generalization V2.

Panel a: what the participant sees in each epoch (washout / training / test).
Panel b: the force -> cursor mapping that the visual gain manipulates.
Panel c: block timeline of the single session (4 cycles x 3 blocks, 560 trials).

The screen is calibrated in cm of cursor extent; the hand produces force in N.
The visual gain is the N -> cm conversion: extent = gain x force.

Outputs Figs/fig_design_v2.{pdf,png}.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import to_rgb
from matplotlib.patches import FancyArrowPatch, Rectangle

import utils

OUT = Path("./Figs")
OUT.mkdir(parents=True, exist_ok=True)

# --- design constants (single source of truth: utils.py) ------------------
CONDITIONS = utils.conditions                       # [-4, -2, 2, 4] cm of extent
N_WASHOUT = utils.num_trials_washout_per_condition * utils.num_conditions   # 40
N_TRAIN = utils.num_trials_adaptation                                       # 40
N_TEST = utils.num_trials_test_per_condition * utils.num_conditions         # 60
N_CYCLES = utils.num_conditions                                             # 4
GAIN_TRAIN = utils.adaptation_gain                                          # 2.0
GAIN_BASE = utils.baseline_gain                                             # 1.0

CUED = 2            # extent cued in the washout / training mock-ups (cm)
CUED_TEST = 4       # extent cued in the test mock-up (cm)

# Example participant's order of trained extents; randomised per subject.
TRAINED_ORDER = [2, -4, 4, -2]


def signed(x):
    return f"{x:+g}".replace("-", "−")


# --- palette --------------------------------------------------------------
cb = sns.color_palette("colorblind")


def blend(color, alpha, bg=(1, 1, 1)):
    c = np.asarray(to_rgb(color))
    return tuple(alpha * c + (1 - alpha) * np.asarray(bg))


# extents: flexion (negative) blue, extension (positive) vermillion; |x| -> opacity
EXTENT_COLOR = {-4: blend(cb[0], 1.0), -2: blend(cb[0], 0.45),
                2: blend(cb[3], 0.45), 4: blend(cb[3], 1.0)}

GAIN1_COL = "#6e6e6e"
GAIN2_COL = blend(cb[2], 0.95)

EPOCH_COLOR = {"washout": "#d9d9d9", "training": blend(cb[2], 0.85), "test": "#ffffff"}
EPOCH_EDGE = {"washout": "#6e6e6e", "training": "#04624c", "test": "#3d3d3d"}

SCREEN_BG = "black"
ZERO_BAR = "#cdcdcd"
BOX_DIM_FACE, BOX_DIM_EDGE = "#232323", "#3a3a3a"
BOX_ON_FACE, BOX_ON_EDGE = "#6f6f6f", "#ffffff"
CURSOR = "#d92b2b"
NOTE = "#5a5a5a"
IN_SCREEN = "#9a9a9a"

YLIM = (-5.9, 5.9)          # shared by the screens and the mapping panel


# --- panel a: screen mock-ups --------------------------------------------
def draw_screen(ax, active, cursor=None, show_ticks=False):
    """One trial screen. `active` = cued extent (cm); `cursor` = the single red
    cursor line, drawn where the gain puts it. There is only ever one cursor."""
    ax.set_facecolor(SCREEN_BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(*YLIM)
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)

    # home / rest band around zero
    ax.add_patch(Rectangle((0.03, -0.95), 0.94, 1.9, facecolor=ZERO_BAR, edgecolor="none",
                           zorder=1))

    # target boxes: the cued extent is bright, the other three stay dim
    for ext in CONDITIONS:
        on = ext == active
        ax.add_patch(Rectangle((0.22, ext - 0.42), 0.56, 0.84,
                               facecolor=BOX_ON_FACE if on else BOX_DIM_FACE,
                               edgecolor=BOX_ON_EDGE if on else BOX_DIM_EDGE,
                               lw=1.1 if on else 0.6, zorder=2))

    if cursor is not None:
        ax.plot([0.24, 0.76], [cursor, cursor], color=CURSOR, lw=2.0, zorder=4,
                solid_capstyle="butt")

    if show_ticks:
        ax.set_yticks(CONDITIONS)
        ax.set_yticklabels([signed(c) for c in CONDITIONS], fontsize=7)
        ax.set_ylabel("Extent (cm)", fontsize=8, labelpad=3)
        ax.tick_params(axis="y", length=2.5, width=0.7, pad=2)
    else:
        ax.set_yticks([])


# --- panel b: the force -> cursor mapping --------------------------------
def draw_mapping(ax):
    f = np.linspace(-3.2, 3.2, 100)
    ax.set_xlim(-3.25, 3.25)
    ax.set_ylim(*YLIM)

    ax.axhline(0, color="#d0d0d0", lw=0.7, zorder=1)
    ax.axvline(0, color="#d0d0d0", lw=0.7, zorder=1)

    ax.plot(f, GAIN_BASE * f, color=GAIN1_COL, lw=1.6, zorder=3, clip_on=True)
    ax.plot(f, GAIN_TRAIN * f, color=GAIN2_COL, lw=1.9, zorder=3, clip_on=True)

    # the same 2 cm target needs 2 N under gain 1 but only 1 N under gain 2
    ax.plot([0, CUED / GAIN_BASE], [CUED, CUED], color="#9a9a9a", lw=0.8, ls=(0, (2.5, 2)),
            zorder=2)
    for x, col in ((CUED / GAIN_BASE, GAIN1_COL), (CUED / GAIN_TRAIN, GAIN2_COL)):
        ax.plot([x, x], [0, CUED], color=col, lw=0.8, ls=(0, (2.5, 2)), zorder=2)
        ax.plot([x], [CUED], marker="o", ms=4.2, color=col, mec="white", mew=0.7, zorder=5)

    ax.add_patch(Rectangle((-3.25, CUED - 0.42), 6.5, 0.84, facecolor=EXTENT_COLOR[CUED],
                           alpha=0.18, edgecolor="none", zorder=0))
    ax.text(-3.15, CUED, f"target {signed(CUED)} cm", fontsize=6.3, color=NOTE,
            ha="left", va="center")

    # the force each gain demands for that target, called out in the empty quadrant
    ax.text(-3.15, 5.45, f"to reach {signed(CUED)} cm:", fontsize=6.3, color="#3d3d3d",
            ha="left", va="top")
    ax.text(-3.15, 4.45, f"{CUED / GAIN_BASE:g} N", fontsize=7, color=GAIN1_COL,
            fontweight="bold", ha="left", va="top")
    ax.text(-2.25, 4.45, "at gain 1", fontsize=6.3, color="#3d3d3d", ha="left", va="top")
    ax.text(-3.15, 3.45, f"{CUED / GAIN_TRAIN:g} N", fontsize=7, color=GAIN2_COL,
            fontweight="bold", ha="left", va="top")
    ax.text(-2.25, 3.45, "at gain 2", fontsize=6.3, color="#3d3d3d", ha="left", va="top")

    # line key, in the empty fourth quadrant
    ax.plot([0.40, 1.00], [-3.15, -3.15], color=GAIN2_COL, lw=1.9, solid_capstyle="butt")
    ax.text(1.15, -3.15, f"gain {GAIN_TRAIN:.0f}", fontsize=7, color=GAIN2_COL,
            fontweight="bold", ha="left", va="center")
    ax.plot([0.40, 1.00], [-4.45, -4.45], color=GAIN1_COL, lw=1.6, solid_capstyle="butt")
    ax.text(1.15, -4.45, f"gain {GAIN_BASE:.0f}", fontsize=7, color=GAIN1_COL,
            fontweight="bold", ha="left", va="center")

    ax.set_xticks([-2, -1, 1, 2])
    ax.set_xticklabels([signed(v) for v in (-2, -1, 1, 2)], fontsize=7)
    ax.set_yticks(CONDITIONS)
    ax.set_yticklabels([signed(c) for c in CONDITIONS], fontsize=7)
    ax.set_xlabel("Force produced (N)", fontsize=8, labelpad=2)
    ax.set_ylabel("Cursor extent (cm)", fontsize=8, labelpad=1)
    ax.tick_params(length=2.5, width=0.7, pad=2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_position(("outward", 3))
    ax.spines["bottom"].set_position(("outward", 3))


def main():
    utils.set_figure_style("2col")
    plt.rcParams["font.size"] = 8

    fig = plt.figure(figsize=(6.93, 5.75))
    gs_a = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1.45],
                            left=0.085, right=0.985, top=0.920, bottom=0.605,
                            wspace=0.30)
    gs_c = fig.add_gridspec(2, 1, height_ratios=[0.45, 1.55], left=0.085, right=0.985,
                            top=0.385, bottom=0.055, hspace=0.10)

    # ---------------- panel a ----------------
    axs = [fig.add_subplot(gs_a[0, i]) for i in range(3)]

    draw_screen(axs[0], active=CUED, cursor=GAIN_BASE * CUED, show_ticks=True)
    draw_screen(axs[1], active=CUED, cursor=GAIN_TRAIN * CUED)
    draw_screen(axs[2], active=CUED_TEST, cursor=None)

    axs[0].text(0.5, 3.15, "2 N → 2 cm", color=IN_SCREEN, fontsize=6.3,
                ha="center", va="center", zorder=5)
    axs[1].text(0.44, 3.15, "2 N → 4 cm", color=IN_SCREEN, fontsize=6.3,
                ha="center", va="center", zorder=5)
    axs[1].add_patch(FancyArrowPatch((0.88, 2.15), (0.88, 3.70), mutation_scale=7,
                                     arrowstyle="-|>", lw=1.1, color="#e8a0a0", zorder=5))
    axs[2].text(0.5, 3.15, "no cursor", color=IN_SCREEN, fontsize=6.3, style="italic",
                ha="center", va="center", zorder=5)

    titles = ["Washout", "Training", "Test"]
    subs = [f"gain {GAIN_BASE:.0f} · cursor on\nall 4 extents, shuffled\n{N_WASHOUT} trials",
            f"gain {GAIN_TRAIN:.0f} · cursor on\n1 trained extent\n{N_TRAIN} trials",
            f"gain {GAIN_BASE:.0f} · no cursor\nall 4 extents, shuffled\n{N_TEST} trials"]
    for ax, t, s_, c in zip(axs, titles, subs,
                            [EPOCH_EDGE["washout"], EPOCH_EDGE["training"],
                             EPOCH_EDGE["test"]]):
        ax.text(0.5, 1.045, t, transform=ax.transAxes, fontsize=9.5, fontweight="bold",
                color=c, ha="center", va="bottom")
        ax.text(0.5, -0.035, s_, transform=ax.transAxes, fontsize=6.8, color=NOTE,
                ha="center", va="top", linespacing=1.45)

    # ---------------- panel b ----------------
    ax_m = fig.add_subplot(gs_a[0, 3])
    draw_mapping(ax_m)
    ax_m.text(0.5, 1.045, "Force → cursor", transform=ax_m.transAxes, fontsize=9.5,
              fontweight="bold", color="#1a1a1a", ha="center", va="bottom")

    # ---------------- panel c: blocks ----------------
    blocks = []          # (start, n_trials, epoch, cycle)
    x = 0
    for cyc in range(N_CYCLES):
        for epoch, n in (("washout", N_WASHOUT), ("training", N_TRAIN), ("test", N_TEST)):
            blocks.append((x, n, epoch, cyc))
            x += n
    total = x

    # visual gain trace
    ax_g = fig.add_subplot(gs_c[0])
    xs, ys = [], []
    for start, n, epoch, _ in blocks:
        g = GAIN_TRAIN if epoch == "training" else GAIN_BASE
        xs += [start, start + n]
        ys += [g, g]
    ax_g.step(xs, ys, where="post", color="#333333", lw=1.1)
    ax_g.fill_between(xs, 1.0, ys, step="post", color=blend(cb[2], 0.25), lw=0)
    ax_g.set_xlim(-6, total + 6)
    ax_g.set_ylim(0.72, 2.32)
    ax_g.set_yticks([1, 2])
    ax_g.set_yticklabels(["1", "2"], fontsize=7)
    ax_g.set_ylabel("Visual\ngain", fontsize=7.5, labelpad=3, linespacing=1.25)
    ax_g.set_xticks([])
    ax_g.tick_params(axis="y", length=2.5, width=0.7, pad=2)
    for sp in ("top", "right", "bottom"):
        ax_g.spines[sp].set_visible(False)

    # block timeline
    ax_t = fig.add_subplot(gs_c[1])
    ax_t.set_xlim(-6, total + 6)
    ax_t.set_ylim(-1.30, 0.95)
    ax_t.axis("off")

    top, h = 0.28, 0.50
    for start, n, epoch, cyc in blocks:
        ax_t.add_patch(Rectangle((start, top), n, h, facecolor=EPOCH_COLOR[epoch],
                                 edgecolor=EPOCH_EDGE[epoch], lw=0.8,
                                 hatch="////" if epoch == "test" else None, zorder=2))
        if cyc == 0:
            lab = f"{n} trials" if epoch == "test" else f"{n}"
            ax_t.text(start + n / 2, top + h + 0.05, lab, fontsize=6.5, color=NOTE,
                      ha="center", va="bottom")

    for cyc in range(N_CYCLES):
        cyc_blocks = [b for b in blocks if b[3] == cyc]
        x0 = cyc_blocks[0][0] + 2
        x1 = cyc_blocks[-1][0] + cyc_blocks[-1][1] - 2
        mid = (x0 + x1) / 2
        ax_t.plot([x0, x1], [0.14, 0.14], color="#8c8c8c", lw=0.8, solid_capstyle="butt")
        for xe in (x0, x1):
            ax_t.plot([xe, xe], [0.14, 0.22], color="#8c8c8c", lw=0.8)
        ax_t.text(mid, 0.01, f"Cycle {cyc + 1}", fontsize=7.5, ha="center", va="top")

        ext = TRAINED_ORDER[cyc]
        ax_t.add_patch(Rectangle((mid - 46, -0.50), 16, 0.20,
                                 facecolor=EXTENT_COLOR[ext], edgecolor="none", zorder=3))
        ax_t.text(mid - 24, -0.40, f"trained {signed(ext)} cm", fontsize=7,
                  ha="left", va="center")

    ax_t.annotate("", xy=(total, -0.80), xytext=(0, -0.80),
                  arrowprops=dict(arrowstyle="-|>", lw=0.9, color="#4d4d4d"))
    ax_t.text(0, -0.92, "trial", fontsize=7, color=NOTE, ha="left", va="top")
    ax_t.text(total, -0.92, f"one session · {N_CYCLES * 3} blocks · {total} trials",
              fontsize=7, color=NOTE, ha="right", va="top")
    ax_t.text(total, -1.13, "order of trained extents randomised across participants",
              fontsize=6.5, color=NOTE, ha="right", va="top", style="italic")

    handles = [Rectangle((0, 0), 1, 1, facecolor=EPOCH_COLOR[e], edgecolor=EPOCH_EDGE[e],
                         lw=0.8, hatch="////" if e == "test" else None)
               for e in ("washout", "training", "test")]
    labels = ["Washout  (gain 1, cursor on)",
              "Training  (gain 2, cursor on)",
              "Test  (gain 1, no cursor)"]
    ax_g.legend(handles, labels, loc="lower left", bbox_to_anchor=(0.0, 1.45),
                ncol=3, frameon=False, fontsize=7.2, handlelength=1.6,
                handleheight=0.95, columnspacing=1.8, borderpad=0.0)

    fig.canvas.draw()
    fig.text(0.008, axs[0].get_position().y1 + 0.075, "a", fontsize=13,
             fontweight="bold", va="top")
    fig.text(ax_m.get_position().x0 - 0.072, ax_m.get_position().y1 + 0.075, "b",
             fontsize=13, fontweight="bold", va="top")
    fig.text(0.008, ax_g.get_position().y1 + 0.085, "c", fontsize=13,
             fontweight="bold", va="top")

    for ext in (".pdf", ".png"):
        fig.savefig(OUT / f"fig_design_v2{ext}", dpi=300, facecolor="white",
                    bbox_inches="tight")
    print("wrote", OUT / "fig_design_v2.pdf", "and .png")


if __name__ == "__main__":
    main()
