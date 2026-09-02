"""Experiment design and gain-adaptation predictions figure."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Polygon
import numpy as np

import utils

OUT_DIR = Path("./Figs")
ALPHA = 0.4  # schematic learning rate
B_ADDITIVE = 0.25  # schematic additive B (flat across next-trial extent)

CONDITIONS = [float(c) for c in utils.conditions]
NEAR_EXT = min(c for c in CONDITIONS if c > 0)
FAR_EXT = max(c for c in CONDITIONS if c > 0)
FORCE_LIM = max(abs(c) for c in CONDITIONS)
YTICKS = CONDITIONS[:2] + [-0.5, 0.5] + CONDITIONS[2:]

RED = "#C41E3A"
GREY_BAND = "#C8C8C8"
GREY_EDGE = "#8E8E8E"
TARGET = "#6A6A6A"
BLUE = "#0072B2"
ORANGE = "#E69F00"


def add_baseline(ax, x0, x1, n=36):
    """Grey ±0.5 N band with a light sawtooth edge, matching the task display."""
    x = np.linspace(x0, x1, n)
    amp = 0.07
    teeth = amp * np.where(np.arange(n) % 2 == 0, 1.0, 0.0)
    verts = np.vstack(
        [
            np.column_stack([x, 0.5 + teeth]),
            np.column_stack([x[::-1], -0.5 - teeth[::-1]]),
        ]
    )
    ax.add_patch(
        Polygon(verts, closed=True, facecolor=GREY_BAND, edgecolor=GREY_EDGE, lw=0.5, zorder=1)
    )


def draw_thin_cursor(ax, y, x_c=-0.35, half_w=0.42):
    ax.plot(
        [x_c - half_w, x_c + half_w],
        [y, y],
        color=RED,
        lw=0.9,
        solid_capstyle="butt",
        zorder=4,
    )


def draw_target(ax, force, x_c=-0.35, half_w=0.42, active=True):
    h = 0.5
    ax.add_patch(
        mpatches.Rectangle(
            (x_c - half_w, force - h / 2),
            2 * half_w,
            h,
            facecolor=TARGET if active else "0.25",
            edgecolor="0.85" if active else "0.35",
            lw=0.8,
            zorder=2,
            alpha=1.0 if active else 0.55,
        )
    )


def _tick_label(v):
    if abs(v - round(v)) < 1e-9:
        s = str(int(round(v)))
    else:
        s = f"{v:g}"
    return f"+{s}" if v > 0 else s.replace("-", "−")


def style_screen(ax):
    ax.set_facecolor("black")
    for spine in ax.spines.values():
        spine.set_color("0.15")
        spine.set_linewidth(0.8)
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-FORCE_LIM - 1.3, FORCE_LIM + 1.3)
    ax.set_xticks([])
    ax.tick_params(axis="y", colors="0.25", length=2.5, labelsize=7)
    ax.set_yticks(YTICKS)
    ax.set_yticklabels([_tick_label(v) for v in YTICKS])


def draw_panel_a(ax):
    """Task display: baseline ±0.5 N, thin red cursor, four possible targets."""
    add_baseline(ax, -1.15, 1.15)
    for t in CONDITIONS:
        draw_target(ax, t, active=(t == NEAR_EXT))
    draw_thin_cursor(ax, 0.0)
    style_screen(ax)
    ax.set_ylabel("Force (N)")
    ax.set_title("Experiment screen")
    ax.text(1.05, FAR_EXT, "ext.", color="0.45", fontsize=6.5, va="center")
    ax.text(1.05, -FAR_EXT, "flx.", color="0.45", fontsize=6.5, va="center")
    ax.text(
        0.0,
        -FORCE_LIM - 1.05,
        "Baseline ±0.5 N  ·  one target per trial",
        color="0.55",
        fontsize=6.5,
        ha="center",
        va="bottom",
    )


def draw_mini_screen(ax, target, cursor):
    add_baseline(ax, -1.05, 1.05)
    draw_target(ax, target, x_c=0.0, half_w=0.38)
    draw_thin_cursor(ax, cursor, x_c=0.0, half_w=0.38)
    style_screen(ax)
    ax.set_yticklabels([])
    ax.tick_params(axis="y", length=0)


def draw_panel_b(fig, spec):
    """Trial t error, then two possible tests. Same Δg, correction scales with T[t+1]."""
    inner = spec.subgridspec(1, 3, wspace=0.18, width_ratios=[1.15, 1, 1])
    ax_t = fig.add_subplot(inner[0, 0])
    ax_2 = fig.add_subplot(inner[0, 1])
    ax_4 = fig.add_subplot(inner[0, 2])

    # Trial t: aimed at near-extent; red cursor is shifted up by p
    p_t = 0.85 * (NEAR_EXT / 2.0)
    cursor_t = NEAR_EXT + p_t
    delta_g = ALPHA * p_t / NEAR_EXT
    cursor_near = NEAR_EXT * (1.0 - delta_g)
    cursor_far = FAR_EXT * (1.0 - delta_g)

    draw_mini_screen(ax_t, target=NEAR_EXT, cursor=cursor_t)
    ax_t.set_title(rf"Trial $t$  (adapt at ${NEAR_EXT:+g}$ N)", fontsize=9)
    ax_t.set_ylabel("Force (N)")
    ax_t.set_yticklabels([_tick_label(v) for v in YTICKS])
    ax_t.tick_params(axis="y", length=2.5, labelsize=7, colors="0.25")
    ax_t.annotate(
        r"$p_t$",
        xy=(0.42, cursor_t),
        xytext=(1.05, cursor_t + 0.7),
        color="0.2",
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color="0.35", lw=0.9),
        annotation_clip=False,
    )

    # Same Δg on t+1: correction = Δg × next target
    draw_mini_screen(ax_2, target=NEAR_EXT, cursor=cursor_near)
    ax_2.set_title(rf"$t{{+}}1$ at ${NEAR_EXT:+g}$ N", fontsize=9)

    draw_mini_screen(ax_4, target=FAR_EXT, cursor=cursor_far)
    ax_4.set_title(rf"$t{{+}}1$ at ${FAR_EXT:+g}$ N", fontsize=9)

    ax_t.text(
        0.5,
        -0.18,
        r"Learn $\Delta g \propto p_t/T_t$",
        transform=ax_t.transAxes,
        ha="center",
        fontsize=7.5,
        color="0.25",
    )
    ax_2.text(
        0.5,
        -0.18,
        rf"correction $=\Delta g\times {NEAR_EXT:g}$" + "\n(small)",
        transform=ax_2.transAxes,
        ha="center",
        va="top",
        fontsize=7.5,
        color="0.25",
    )
    ax_4.text(
        0.5,
        -0.18,
        rf"correction $=\Delta g\times {FAR_EXT:g}$" + "\n(large)",
        transform=ax_4.transAxes,
        ha="center",
        va="top",
        fontsize=7.5,
        color=BLUE,
    )
    return ax_t


def slope_B(t_from, t_to):
    """Method A learning slope: X[t+1] ≈ −B p[t], with B ∝ T[t+1]/T[t] under gain."""
    return ALPHA * (t_to / t_from)


def draw_panel_c(ax):
    t_next = np.array(CONDITIONS)
    t_line = np.linspace(-FORCE_LIM, FORCE_LIM, 80)

    ax.axhline(0, color="0.85", lw=0.7, zorder=0)
    ax.axvline(0, color="0.85", lw=0.7, zorder=0)

    ax.plot(t_line, ALPHA * t_line / NEAR_EXT, color=BLUE, lw=1.5, zorder=2)
    ax.plot(t_line, ALPHA * t_line / FAR_EXT, color=ORANGE, lw=1.5, zorder=2)
    ax.plot(
        [-FORCE_LIM, FORCE_LIM],
        [B_ADDITIVE, B_ADDITIVE],
        color="0.45",
        lw=1.2,
        ls="--",
        zorder=1,
        label="Additive offset (any $T_t$)",
    )

    ax.plot(
        t_next,
        slope_B(NEAR_EXT, t_next),
        "o",
        color=BLUE,
        ms=5.5,
        zorder=3,
        label=rf"Gain, after $T_t = {NEAR_EXT:+g}$ N",
    )
    ax.plot(
        t_next,
        slope_B(FAR_EXT, t_next),
        "s",
        color=ORANGE,
        ms=5,
        zorder=3,
        label=rf"Gain, after $T_t = {FAR_EXT:+g}$ N",
    )

    ax.set_xticks(CONDITIONS)
    ax.set_xticklabels([_tick_label(v) for v in CONDITIONS])
    ax.set_xlim(-FORCE_LIM - 0.8, FORCE_LIM + 0.8)
    ax.set_ylim(-1.05, 1.05)
    ax.set_xlabel(r"Next-trial extent  $T_{t+1}$ (N)")
    ax.set_ylabel(r"Slope of regressing $P_t$ to $X_{t+1}$")
    ax.legend(frameon=False, loc="upper left", fontsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(
        0.98,
        0.03,
        r"$B=-\mathrm{cov}(X_{t+1},p_t)/\mathrm{var}(p_t)$  ·  gain: $B\propto T_{t+1}/T_t$",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.5,
        color="0.35",
    )


def main():
    utils.set_figure_style("2col")
    fig = plt.figure(figsize=(6.50, 6.15))
    gs = GridSpec(
        2,
        2,
        figure=fig,
        height_ratios=[1.22, 1.0],
        width_ratios=[0.78, 1.22],
        hspace=0.50,
        wspace=0.22,
    )

    ax_a = fig.add_subplot(gs[0, 0])
    draw_panel_a(ax_a)
    ax_t = draw_panel_b(fig, gs[0, 1])
    ax_c = fig.add_subplot(gs[1, :])
    draw_panel_c(ax_c)

    utils.add_subpanel_label(ax_a, "a", fontsize=14, position=(-0.22, 1.10))
    utils.add_subpanel_label(ax_t, "b", fontsize=14, position=(-0.22, 1.10))
    utils.add_subpanel_label(ax_c, "c", fontsize=14, position=(-0.08, 1.08))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf = OUT_DIR / "design_and_predictions.pdf"
    png = OUT_DIR / "design_and_predictions.png"
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {pdf}")
    print(f"Wrote {png}")


if __name__ == "__main__":
    main()
