import pandas as pd
import numpy as np
from typing import List
from pathlib import Path

from matplotlib import rcParams


path = "./Single_Finger_Gain_Generalization_V2/single_gain_generalization_v2"
path_misc = "./Single_Finger_Gain_Generalization_V2_miscs/"

fingers = ['1', '2', '3', '4', '5']
index_finger = 2  # 1-based: thumb=1 ... pinky=5

iti = 1000
planTime = 2000
feedbackTime = 1000

total_sub_num = 20
num_blocks_per_condition = 3  # washout, adaptation, test
num_conditions = 4
num_blocks = num_conditions * num_blocks_per_condition  # 12 blocks per subject
num_trials_washout_per_condition = 10
num_trials_adaptation = 40
num_trials_test_per_condition = 15
conditions = [-4, -2, 2, 4]
adaptation_gain = 2.0
baseline_gain = 1.0


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
    """Removes error trials from the dat file of a subject."""
    return subj[(subj['trialCorr'] == 1)]


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
    return row[f'targetForce{index_finger}']


def add_day(subjs: pd.DataFrame) -> pd.DataFrame:
    """V2 is single-session; day is always 1."""
    subjs = subjs.copy()
    subjs['day'] = 1
    return subjs


def add_total_trial_num(subjs: pd.DataFrame) -> pd.DataFrame:
    """Cumulative trial index within subject (TN resets each block)."""
    subjs = subjs.sort_values(['subNum', 'BN', 'TN']).copy()
    subjs['TotalTrialNum'] = subjs.groupby('subNum').cumcount() + 1
    return subjs


def add_block_type(subjs: pd.DataFrame) -> pd.DataFrame:
    """Label each block as washout, adaptation, or test (repeats every 3 blocks)."""
    subjs = subjs.copy()
    block_type_map = {1: 'washout', 2: 'adaptation', 3: 'test'}
    subjs['block_type'] = ((subjs['BN'] - 1) % num_blocks_per_condition + 1).map(block_type_map)
    # One washout→adaptation→test cycle per adapted target condition
    subjs['cycle'] = ((subjs['BN'] - 1) // num_blocks_per_condition) + 1
    return subjs


def add_adaptation_condition(subjs: pd.DataFrame) -> pd.DataFrame:
    """Attach the trained (adaptation-block) target force to every trial in that cycle."""
    subjs = subjs.copy()
    adapt = (
        subjs.loc[subjs['block_type'] == 'adaptation', ['subNum', 'cycle', 'condition']]
        .drop_duplicates(['subNum', 'cycle'])
        .rename(columns={'condition': 'adaptation_condition'})
    )
    return subjs.merge(adapt, on=['subNum', 'cycle'], how='left')


def add_force_errors(subjs: pd.DataFrame) -> pd.DataFrame:
    """
    endForce in the .dat is the gain-scaled visual cursor.
    Produced force = endForce / gain.
    Expected force = targetForce / gain (force needed to hit the visual target).
    Force error = produced - expected = (endForce - targetForce) / gain.
    """
    subjs = subjs.copy()
    gain = subjs['gain'].replace(0, np.nan)
    for i in range(1, 6):
        produced = subjs[f'endForce{i}'] / gain
        expected = subjs[f'targetForce{i}'] / gain
        subjs[f'producedForce{i}'] = produced
        subjs[f'expectedForce{i}'] = expected
        subjs[f'forceError{i}'] = produced - expected
    return subjs


def add_trial_num_within_block(subjs: pd.DataFrame) -> pd.DataFrame:
    """Trial index that resets each block (BN)."""
    subjs = subjs.sort_values(['subNum', 'BN', 'TN']).copy()
    subjs['trial_num_within_block'] = subjs.groupby(['subNum', 'BN']).cumcount() + 1
    return subjs


def add_trial_num_within_condition_within_block(subjs: pd.DataFrame) -> pd.DataFrame:
    """Trial index for each condition within a block."""
    subjs = subjs.sort_values(['subNum', 'BN', 'TN']).copy()
    subjs['trial_num_within_condition'] = subjs.groupby(['subNum', 'BN', 'condition']).cumcount() + 1
    subjs
    return subjs




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
