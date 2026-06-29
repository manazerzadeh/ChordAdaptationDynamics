import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import re
from scipy import stats
import matplotlib.cm as cm
import seaborn as sns
from typing import List
import pingouin as pg

import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import AnovaRM


from natsort import index_natsorted

path = "./cad_spat_vis1/Single_Finger/cad_spat_vis1"
path_misc = "./cad_spat_vis1_miscs/Single_Finger/"

fingers = ['1', '2', '3', '4', '5']

iti = 1000 # msecs for inter-trial interval
planTime = 2000 # msecs for precue time
feedbackTime = 2000 # msecs for feedback time


total_sub_num = 20
num_sessions = 1
num_blocks_per_session = 20
num_trials_per_block = 40

def read_dat_file(path : str):
    # column_names = pd.read_csv(path, delimiter='\t', usecols=lambda column: not column.startswith("Unnamed")).columns
    # dtype_dict = {col: int for col in column_names}
    # dtype_dict['clammpedSpeed'] = float


    # data = pd.read_csv(path, delimiter= '\t', dtype = dtype_dict, usecols=lambda column: not column.startswith("Unnamed"))
    data = pd.read_csv(path, delimiter= '\t', usecols=lambda column: not column.startswith("Unnamed"))
    # data = pd.read_csv(path, delimiter = '\t')
    return data

def read_dat_files_subjs_list(subjs_list: List[int]):
    """
    Reads the corresponding dat files of subjects and converts them to a list of dataframes.
    """
    return [read_dat_file(path + "_" + str(sub) + ".dat") for sub in subjs_list]



def remove_error_trials(subj: pd.DataFrame) -> pd.DataFrame:
    """
    Removes error trials from the dat file of a subject
    """

    return subj[(subj['trialCorr'] == 1)]


def remove_error_trials_presses(subj_press: pd.DataFrame) -> pd.DataFrame:

    return subj_press[(subj_press['isTrialError'] == 0) & (subj_press['timingError'] == 0)]


def remove_error_presses(subj_press: pd.DataFrame) -> pd.DataFrame:

    return subj_press[(subj_press['isPressError']) == 0]



def add_IPI(subj: pd.DataFrame):
    """
    Adds interpress intervals to a subject's dataframe
    """

    for i in range(seq_length-1):
        col1 = 'pressTime'+str(i+1)
        col2 = 'pressTime'+str(i+2)
        new_col = 'IPI'+str(i+1)
        subj[new_col] = subj[col2] - subj[col1]

    # subj['IPI0'] = subj['RT']



def add_clmap_error(subj: pd.DataFrame):
    """
    Adds a column determining whether the trial was a clamped speed error or not
    """

    subj['isClampedError'] = subj.apply(lambda row:
                                         1 if (row['isClamped'] == 1 and 
                                               row['isPressError'] == 0 and
              (row['clammpedSpeed'] < (row['ET'] - clampedSpeedTolerance) or 
               row['clammpedSpeed'] > (row['ET'] + clampedSpeedTolerance))) 
        else 0, axis=1)
    return subj


def add_press_error_in_trial(subj: pd.DataFrame):
    """
    Adds a column determining whether there was a press error in the trial or not
    """

    subj['isPressError'] = subj.apply(lambda row:
                                      1 if any(row['press'+str(i+1)] != row['response'+str(i+1)] for i in range(seq_length)
                                               ) else 0, axis=1)
    return subj
                                      
    

def add_training_phase(row: pd.Series) -> str:
    # add phase column 
    ### day1:
    # pretest blocks 2-4
    # training blocks 5-12
    # posttest full speed blocks 13-14
    # post test clamped speed blocks 15-16

    ### day2: 
    # pretest blocks 17-19
    # training blocks 20-27
    # posttest full speed blocks 28-29
    # post test clamped speed blocks 30-31

    if row['BN'] in [2, 3, 4, 17, 18, 19]:
        return 'pretest'
    elif row['BN'] in [5, 6, 7, 8, 9, 10, 11, 12, 20, 21, 22, 23, 24, 25, 26, 27]:
        return 'training'
    elif row['BN'] in [13, 14, 28, 29]:
        return 'posttest_full_speed'
    elif row['BN'] in [15, 16, 30, 31]:
        return 'posttest_clamped_speed'
    else:
        return 'unknown'



def finger_melt_IPIs(subj: pd.DataFrame) -> pd.DataFrame:
    """
    Creates seperate row for each IPI in the whole experiment adding two columns, "IPI_Number" determining the order of IPI
    and "IPI_Value" determining the time of IPI
    """

    
    subj_melted = pd.melt(subj, 
                    id_vars=['BN', 'TN', 'SubNum', 'repType', 'repNum', 'seqNum', 'dummy', 
                             'tStart', 'hand', 'cueP', 'RT', 'MT', 'points',
                            'isError'], 
                    value_vars =  [_ for _ in subj.columns if _.startswith('IPI')],
                    var_name='IPI_Number', 
                    value_name='IPI_Value')
    

    subj_melted['N'] = (subj_melted['IPI_Number'].str.extract('(\d+)').astype('int64') + 1)

    

    
    return subj_melted


def finger_melt_presses(subj: pd.DataFrame) -> pd.DataFrame:

    subj_melted = pd.melt(subj, 
                    id_vars=['BN', 'TN', 'SubNum', 'repType', 'repNum', 'seqNum', 'dummy', 
                             'tStart', 'hand', 'cueP', 'RT', 'MT', 'points',
                            'isError'], 
                    value_vars =  [_ for _ in subj.columns if _.startswith('press') and not _.startswith('pressTime')],
                    var_name='Press_Number', 
                    value_name='Press_Value')
    

    subj_melted['N'] = subj_melted['Press_Number'].str.extract('(\d+)').astype('int64')

    return subj_melted


def finger_melt_responses(subj: pd.DataFrame) -> pd.DataFrame:

    subj_melted = pd.melt(subj, 
                    id_vars=['BN', 'TN', 'SubNum', 'repType', 'repNum', 'seqNum', 'dummy', 
                             'tStart', 'hand', 'cueP', 'RT', 'MT', 'points',
                            'isError'], 
                    value_vars =  [_ for _ in subj.columns if _.startswith('response')],
                    var_name='Response_Number', 
                    value_name='Response_Value')
    
    subj_melted['N'] = subj_melted['Response_Number'].str.extract('(\d+)').astype('int64')

    return subj_melted


def finger_melt(subj: pd.DataFrame) -> pd.DataFrame:
    melt_IPIs = finger_melt_IPIs(subj)
    melt_presses = finger_melt_presses(subj)
    melt_responses = finger_melt_responses(subj)
    merged_df = melt_IPIs.merge(melt_presses, on = ['BN', 'TN', 'SubNum', 'repType', 'repNum', 'seqNum', 'dummy', 
                             'tStart', 'hand', 'cueP', 'RT', 'MT', 'points',
                            'isError','N'])\
                                               .merge(melt_responses, on = ['BN', 'TN', 'SubNum', 'repType', 'repNum', 'seqNum', 'dummy', 
                             'tStart', 'hand', 'cueP', 'RT', 'MT', 'points',
                            'isError', 'N'] )

    return add_press_error(merged_df)


def add_press_error(merged_df):
    merged_df['isPressError'] = ~(merged_df['Press_Value'] == merged_df['Response_Value'])
    return merged_df



def finger_melt_Forces(subjs_force: pd.DataFrame) -> pd.DataFrame:
    """
    Creates seperate row for each Finger Force in the whole experiment adding two columns, "Force_Number" determining the order of Force
    and "Force_Value" determining the time of Force
    """

    
    subj_force_melted = pd.melt(subjs_force, 
                    id_vars=['state', 'time', 'subNum', 'BN', 'TN',
                             'targetForce1', 'targetForce2', 'targetForce3', 'targetForce4', 'targetForce5',
                             'endForce1', 'endForce2', 'endForce3', 'endForce4', 'endForce5',
                             'TotalTrialNum',
                             'trialPoint', 'trialCorr', 'trialErrorType'],
                    value_vars =  [_ for _ in subjs_force.columns if _.startswith('force')],
                    var_name='Force_Number', 
                    value_name='Force_Value')
    
    return subj_force_melted


def cut_force(subjs_force: pd.DataFrame, side_padding) -> pd.DataFrame:
    """
    Cuts the force data to the same length as the IPI data
    """
    subjs_force = subjs_force[((subjs_force['RT'] + precue_time) <= (subjs_force['time'] + side_padding)) & 
                              ((subjs_force['time']) <= (subjs_force['ET'] + precue_time + side_padding))]
    return subjs_force



def cut_force_left(subjs_force: pd.DataFrame) -> pd.DataFrame:

    subjs_force = subjs_force[((subjs_force['RT'] + precue_time) >= subjs_force['time'])]
    return subjs_force


def cut_force_right(subjs_force: pd.DataFrame) -> pd.DataFrame:

    subjs_force = subjs_force[((subjs_force['ET'] + precue_time) <= subjs_force['time'])]
    return subjs_force



import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.ticker as ticker

def set_figure_style(scale="1col"):
    """
    Set figure styling based on publication constraints.
    
    Parameters:
        scale (str): Scale of the figure, choose from "1col", "1.5col", "2col".
                     - "1col" for 8.5cm
                     - "1.5col" for 11.6cm
                     - "2col" for 17.6cm
    """
    # Define width options in cm
    widths = {"1col": 7.62, "1.5col": 11.6, "2col": 16.5}
    
    if scale not in widths:
        raise ValueError("Invalid scale. Choose from '1col', '1.5col', or '2col'.")
    
    # Convert width from cm to inches (1 cm = 0.393701 inches)
    width_in = widths[scale] * 0.393701
    
    # Set figure size (width, height)
    # Assuming height proportional to width (Golden Ratio)
    golden_ratio = (5**0.5 - 1) / 2
    rcParams["figure.figsize"] = (width_in, width_in * golden_ratio)
    
    # Set font sizes
    rcParams["font.size"] = 10  # General font size
    rcParams["axes.titlesize"] = 12  # Figure title
    rcParams["axes.labelsize"] = 9  # Axis main label
    rcParams["xtick.labelsize"] = 7  # Tick labels
    rcParams["ytick.labelsize"] = 7
    rcParams["legend.fontsize"] = 8  # Legend entries
    rcParams["figure.titleweight"] = "bold"
    
    # Set stroke width
    rcParams["axes.linewidth"] = 0.75
    rcParams["xtick.major.width"] = 0.75
    rcParams["ytick.major.width"] = 0.75

    
    # Subpanel lettering size
    rcParams["text.usetex"] = False  # Set to True if using LaTeX
    rcParams["axes.formatter.use_mathtext"] = True  # Math text for scientific notation

def add_subpanel_label(ax, label, fontsize=20, position=(-0.1, 1.05)):
    """
    Add a subpanel label (e.g., 'a', 'b') to a subplot.
    
    Parameters:
        ax (Axes): Matplotlib Axes object.
        label (str): The label text.
        fontsize (int): Font size for the label.
        position (tuple): Position of the label in axes coordinates.
    """
    ax.text(position[0], position[1], label, transform=ax.transAxes, 
            fontsize=fontsize, fontweight="bold", va="top", ha="left")

