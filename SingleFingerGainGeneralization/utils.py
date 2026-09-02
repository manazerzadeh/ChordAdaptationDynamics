import pandas as pd
import numpy as np
from typing import List
from pathlib import Path

from matplotlib import rcParams


path = "./Single_Finger_Gain_Generalization/single_gain_generalization"
path_misc = "./Single_Finger_Gain_Generalization_miscs/"

fingers = ['1', '2', '3', '4', '5']
index_finger = 2  # 1-based: thumb=1 ... pinky=5

iti = 1000
planTime = 2000
feedbackTime = 1000

total_sub_num = 4
num_days = 2
num_blocks_per_day = 10
num_blocks = num_days * num_blocks_per_day
num_trials_per_block = 32  # last block is 33
num_trials_last_block = 33
# Index-finger target extents (N). Experiment used ±1.5 and ±3
# (scaled from the original ±2 / ±4 design).
conditions = [-3.0, -1.5, 1.5, 3.0]


def dat_dir() -> Path:
    return Path(path).parent


def dat_stem() -> str:
    return Path(path).name


def list_dat_subjects() -> List[int]:
    """Subject numbers that have a .dat file in the data folder."""
    files = sorted(dat_dir().glob(f"{dat_stem()}_*.dat"))
    return [int(p.stem.split("_")[-1]) for p in files]


def read_dat_file(path: str):
    data = pd.read_csv(path, delimiter='\t', usecols=lambda column: not column.startswith("Unnamed"))
    return data


def read_dat_files_subjs_list(subjs_list: List[int]):
    """Reads the corresponding dat files of subjects and converts them to a list of dataframes."""
    return [read_dat_file(path + "_" + str(sub) + ".dat") for sub in subjs_list]


def remove_error_trials(subj: pd.DataFrame) -> pd.DataFrame:
    """Removes error trials (`trialCorr != 1`)."""
    return subj.loc[subj['trialCorr'] == 1].copy()


def remove_trials_after_error(subj: pd.DataFrame) -> pd.DataFrame:
    """Drop trials whose immediately previous trial was an error.

    An error trial has no usable perturbation, so the next trial cannot
    contribute a lag-1 learning-rate pair. Pass the full trial sequence
    (including errors) so "previous" is the true preceding trial.
    First trials of a subject (no predecessor) are kept.
    """
    subj = _with_prev_trial_columns(subj)
    return subj.loc[subj['prev_trialCorr'] != 0].copy()


def trials_for_learning_rate(subjs: pd.DataFrame) -> pd.DataFrame:
    """Correct trials whose previous trial was also correct.

    Each remaining row is a valid `X_{t+1}` for Method A, with `p_t` on
    the true previous trial. Pass the full unfiltered trial table.
    """
    subjs = _with_prev_trial_columns(subjs)
    return subjs.loc[
        (subjs['trialCorr'] == 1) & (subjs['prev_trialCorr'] == 1)
    ].copy()


def extract_chord_form_target_force(row):
    chord = ''
    for i in range(1, 6):
        if row[f'targetForce{i}'] > 0:
            chord += '^'
        elif row[f'targetForce{i}'] < 0:
            chord += 'v'
        else:
            chord += '-'
    return chord


def extract_condition(row):
    """Index-finger target force (N)."""
    return round(float(row[f'targetForce{index_finger}']), 2)


def add_day(subjs: pd.DataFrame) -> pd.DataFrame:
    subjs = subjs.copy()
    subjs['day'] = ((subjs['BN'] - 1) // num_blocks_per_day) + 1
    return subjs


def add_total_trial_num(subjs: pd.DataFrame) -> pd.DataFrame:
    """Blocks 1–19 have 32 trials; block 20 has 33. TN resets each block."""
    subjs = subjs.copy()
    subjs['TotalTrialNum'] = (subjs['BN'] - 1) * num_trials_per_block + subjs['TN']
    return subjs


def _with_prev_trial_columns(subjs: pd.DataFrame) -> pd.DataFrame:
    """Attach lag-1 columns from the true preceding trial (session order)."""
    subjs = subjs.sort_values(['subNum', 'BN', 'TN']).copy()
    g = subjs.groupby('subNum', sort=False)
    subjs['prev_condition'] = g['condition'].shift(1)
    subjs['prev_perturbation'] = g['purturbation1'].shift(1)
    subjs['prev_trialCorr'] = g['trialCorr'].shift(1)
    subjs['transition'] = np.where(
        subjs['prev_condition'].notna(),
        subjs['prev_condition'].astype(str) + '->' + subjs['condition'].astype(str),
        np.nan,
    )
    return subjs


def add_transitions(subjs: pd.DataFrame) -> pd.DataFrame:
    subjs = _with_prev_trial_columns(subjs)
    subjs['trial_num_within_condition'] = (
        subjs.groupby(['subNum', 'condition']).cumcount() + 1
    )
    return subjs


def estimate_method_A(X_next, P_t) -> float:
    """B = -cov(X_{t+1}, p_t) / var(p_t). `X` is produced force, not a target deviation."""
    X_next = np.asarray(X_next, dtype=float).ravel()
    P_t = np.asarray(P_t, dtype=float).ravel()
    if len(P_t) < 2 or np.var(P_t, ddof=1) == 0:
        return np.nan
    return float(-np.cov(X_next, P_t, ddof=1)[0, 1] / np.var(P_t, ddof=1))


def learning_pairs(subjs: pd.DataFrame) -> pd.DataFrame:
    """Lag-1 pairs for Method A: current trial is X_{t+1}, previous trial is p_t."""
    df = trials_for_learning_rate(subjs)
    xcol = f'endForce{index_finger}'
    return pd.DataFrame({
        'subNum': df['subNum'].to_numpy(),
        'from': df['prev_condition'].to_numpy(),
        'to': df['condition'].to_numpy(),
        'P_t': df['prev_perturbation'].to_numpy(),
        'X_next': df[xcol].to_numpy(),
    })


def learning_rates_by_transition(subjs: pd.DataFrame) -> pd.DataFrame:
    """Per-subject Method A learning rate for each of the 16 condition transitions."""
    pairs = learning_pairs(subjs)
    rows = []
    for (sub, t_from, t_to), g in pairs.groupby(['subNum', 'from', 'to'], sort=True):
        rows.append({
            'subNum': sub,
            'from': t_from,
            'to': t_to,
            'n_pairs': int(len(g)),
            'B': estimate_method_A(g['X_next'], g['P_t']),
        })
    out = pd.DataFrame(rows)
    subjects = sorted(subjs['subNum'].unique())
    full = pd.MultiIndex.from_product(
        [subjects, conditions, conditions],
        names=['subNum', 'from', 'to'],
    )
    out = (
        out.set_index(['subNum', 'from', 'to'])
        .reindex(full)
        .reset_index()
    )
    out['n_pairs'] = out['n_pairs'].fillna(0).astype(int)
    return out


def set_figure_style(scale="1col"):
    """
    Set figure styling based on publication constraints.

    Parameters:
        scale (str): Scale of the figure, choose from "1col", "1.5col", "2col".
                     - "1col" for 8.5cm
                     - "1.5col" for 11.6cm
                     - "2col" for 17.6cm
    """
    widths = {"1col": 7.62, "1.5col": 11.6, "2col": 16.5}

    if scale not in widths:
        raise ValueError("Invalid scale. Choose from '1col', '1.5col', or '2col'.")

    width_in = widths[scale] * 0.393701
    golden_ratio = (5**0.5 - 1) / 2
    rcParams["figure.figsize"] = (width_in, width_in * golden_ratio)

    rcParams["font.size"] = 10
    rcParams["axes.titlesize"] = 12
    rcParams["axes.labelsize"] = 9
    rcParams["xtick.labelsize"] = 7
    rcParams["ytick.labelsize"] = 7
    rcParams["legend.fontsize"] = 8
    rcParams["figure.titleweight"] = "bold"

    rcParams["axes.linewidth"] = 0.75
    rcParams["xtick.major.width"] = 0.75
    rcParams["ytick.major.width"] = 0.75

    rcParams["text.usetex"] = False
    rcParams["axes.formatter.use_mathtext"] = True


def add_subpanel_label(ax, label, fontsize=20, position=(-0.1, 1.05)):
    """Add a subpanel label (e.g., 'a', 'b') to a subplot."""
    ax.text(position[0], position[1], label, transform=ax.transAxes,
            fontsize=fontsize, fontweight="bold", va="top", ha="left")
