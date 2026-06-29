"""Generate presentation schematic for the two parameter estimation methods."""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# Colorblind-friendly palette (matches notebook)
COLORS = {
    'data': '#0173B2',
    'process': '#DE8F05',
    'math': '#029E73',
    'output': '#CC78BC',
    'group': '#D55E00',
    'subject': '#56B4E9',
    'bg_a': '#E8F4FC',
    'bg_b': '#FFF4E6',
    'arrow': '#404040',
    'title': '#1a1a1a',
}


def draw_box(ax, xy, width, height, text, color, fontsize=9, fontweight='normal', alpha=0.92):
    x, y = xy
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle='round,pad=0.02,rounding_size=0.08',
        linewidth=1.2, edgecolor='#333333', facecolor=color, alpha=alpha, zorder=2,
    )
    ax.add_patch(box)
    ax.text(
        x + width / 2, y + height / 2, text,
        ha='center', va='center', fontsize=fontsize, fontweight=fontweight,
        wrap=True, zorder=3, color='#1a1a1a', linespacing=1.3,
    )
    return (x + width / 2, y), (x + width / 2, y + height)


def draw_arrow(ax, start, end, rad=0.0):
    arrow = FancyArrowPatch(
        start, end,
        arrowstyle='-|>',
        mutation_scale=12,
        linewidth=1.3,
        color=COLORS['arrow'],
        connectionstyle=f'arc3,rad={rad}',
        zorder=1,
    )
    ax.add_patch(arrow)


def draw_panel_bg(ax, xy, width, height, color):
    x, y = xy
    bg = FancyBboxPatch(
        (x, y), width, height,
        boxstyle='round,pad=0.03,rounding_size=0.15',
        linewidth=1.5, edgecolor='#888888', facecolor=color, alpha=0.35, zorder=0,
    )
    ax.add_patch(bg)


def draw_panel_title(ax, x_center, y_top, title, subtitle):
    ax.text(x_center, y_top, title, ha='center', va='top',
            fontsize=12.5, fontweight='bold', color=COLORS['title'])
    ax.text(x_center, y_top - 0.42, subtitle, ha='center', va='top',
            fontsize=9.5, color='#555555', style='italic')


def draw_flow_column(ax, x, y_top, box_width, boxes, annotations=None):
    """Stack boxes top-to-bottom with consistent arrow gaps."""
    arrow_gap = 0.30
    cx = x + box_width / 2
    y = y_top
    box_centers = []

    for i, (height, text, color, fontsize, fontweight) in enumerate(boxes):
        y -= height
        draw_box(ax, (x, y), box_width, height, text, color,
                 fontsize=fontsize, fontweight=fontweight)
        box_centers.append(y + height / 2)
        if i < len(boxes) - 1:
            arrow_end = y - arrow_gap
            draw_arrow(ax, (cx, y), (cx, arrow_end))
            y = arrow_end

    if annotations:
        for box_idx, note, note_color in annotations:
            ax.text(x + box_width + 0.55, box_centers[box_idx], note,
                    ha='left', va='center', fontsize=8.5,
                    color=note_color, style='italic', linespacing=1.25)

    return y


def make_schematic(save_path_png, save_path_pdf):
    fig_w, fig_h = 14, 10
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    # ── Shared model header ──
    header_y, header_h = 8.45, 1.4
    draw_panel_bg(ax, (0.3, header_y), 13.4, header_h, '#F5F5F5')
    ax.text(fig_w / 2, header_y + header_h - 0.2, 'State-Space Learning Model',
            ha='center', va='top', fontsize=14, fontweight='bold', color=COLORS['title'])
    ax.text(
        fig_w / 2, header_y + 0.42,
        r'$X_t = Z_t + \varepsilon_t + p_t$     ·     $Z_{t+1} = A\,Z_t - B\,X_t$'
        '\n'
        r'$X_t$: perturbed force (fingers 2 & 4)   ·   $p_t$: cursor perturbation   ·   $Z_t$: planned force',
        ha='center', va='center', fontsize=9.5, color='#333333', linespacing=1.45,
    )

    # ── Side panels ──
    panel_y, panel_h = 0.95, 7.35
    panel_title_y = panel_y + panel_h - 0.18
    flow_top = panel_y + panel_h - 1.15  # clear space below panel titles

    draw_panel_bg(ax, (0.3, panel_y), 6.4, panel_h, COLORS['bg_a'])
    draw_panel_title(ax, 3.5, panel_title_y,
                     'Method A: Covariance Shortcut', '(per subject × chord)')

    draw_panel_bg(ax, (7.0, panel_y), 6.7, panel_h, COLORS['bg_b'])
    draw_panel_title(ax, 10.35, panel_title_y,
                     'Method B: Nelder–Mead MLE', '(group-averaged trials)')

    box_w = 3.05
    lx, rx = 1.1, 7.8

    boxes_a = [
        (0.78, 'Raw trial data\n(perturbed block)', COLORS['data'], 9, 'normal'),
        (0.88, 'Loop: each subject × chord\n(no cross-subject averaging)', COLORS['subject'], 9, 'bold'),
        (1.08, r'$X_t$ = endForcePerturbed $-$ target' + '\n'
               r'$P_t$ = perturbation' + '\n'
               r'$\Delta X_t = X_{t+1} - X_t$',
         COLORS['process'], 8.5, 'normal'),
        (1.28, 'Closed-form estimate\n(no optimizer):' + '\n'
               r'$B = -(I + \mathrm{cov}(\Delta X, P)\,\mathrm{var}(P)^{-1})$',
         COLORS['math'], 8.3, 'bold'),
        (0.82, 'Output: B matrix only\n(2×2 per subject × chord)', COLORS['output'], 9, 'normal'),
    ]

    boxes_b = [
        (0.78, 'Raw trial data\n(all subjects)', COLORS['data'], 9, 'normal'),
        (0.88, 'Average across subjects\nper trial (TN)', COLORS['group'], 9, 'bold'),
        (1.28, 'Forward simulate $Z_t$\nfrom candidate $(A, B)$:' + '\n'
               r'$Z_{t+1} = A\,Z_t - B\,X_t$' + '\n'
               r'$\varepsilon_t = X_t - Z_t - P_t$',
         COLORS['process'], 8.3, 'normal'),
        (1.28, 'Nelder–Mead minimizes\n' + r'$\sum_t \|\varepsilon_t\|^2$' + '\n'
               '(equivalent to Gaussian MLE)',
         COLORS['math'], 8.3, 'bold'),
        (0.82, 'Output: $A_{11}, A_{22}$ + full $B$\n(one estimate per chord)',
         COLORS['output'], 9, 'normal'),
    ]

    # box index → side note
    ann_a = [
        (1, 'Fast\nanalytical', COLORS['math']),
        (3, 'A not\nestimated', '#666666'),
    ]
    ann_b = [
        (1, 'Iterative\nsearch', COLORS['math']),
        (3, '6 params:\n2 A + 4 B', '#666666'),
    ]

    draw_flow_column(ax, lx, flow_top, box_w, boxes_a, ann_a)
    draw_flow_column(ax, rx, flow_top, box_w, boxes_b, ann_b)

    # ── Footer ──
    footer_y = 0.22
    ax.plot([0.5, 13.5], [footer_y + 0.42, footer_y + 0.42], color='#CCCCCC', lw=1)
    ax.text(
        fig_w / 2, footer_y,
        'Key difference: Method A preserves subject-level estimates for group statistics; '
        'Method B pools subjects before fitting → one group-level parameter set per chord.',
        ha='center', va='bottom', fontsize=9, color='#444444', style='italic',
        wrap=True,
    )

    fig.savefig(save_path_png, dpi=200, bbox_inches='tight', facecolor='white', pad_inches=0.15)
    fig.savefig(save_path_pdf, bbox_inches='tight', facecolor='white', pad_inches=0.15)
    plt.close(fig)
    print(f'Saved: {save_path_png}')
    print(f'Saved: {save_path_pdf}')


if __name__ == '__main__':
    make_schematic(
        './Figs/estimation_methods_schematic.png',
        './Figs/estimation_methods_schematic.pdf',
    )
