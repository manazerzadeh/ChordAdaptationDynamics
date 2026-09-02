# Version 1 — single-finger gain and multi-finger flexion

Two protocols share this folder.

## Single-finger gain adaptation

**Question.** How does produced flexion force change when visual **forceGain** changes, one finger at a time?

**Task.** Each digit (1–5) in turn; target **−3 N** flexion (`TargetFileMaker_single_flexion.ipynb`). Other fingers at 0 N.

**Block cycle (4 blocks × 5 fingers = 20 blocks).** For each finger:

1. Baseline — `targetVisible = 0`, 40 trials
2. Gain 1 — visible target, 40 trials
3. Gain 2 — visible target, 40 trials
4. Washout — `targetVisible = 0`, 40 trials

`utils.py`: `iti = 1000`, `planTime = 2000`, `feedbackTime = 2000` ms; `num_sessions = 1`; `num_blocks_per_session = 20`; `num_trials_per_block = 40`; `total_sub_num = 20` (planned). The target-file maker uses `total_sub_num = 2`.

The `.tgt` files do **not** store `forceGain`. Gains in collected `.dat` files are subject-specific. Analysis uses `actualEndForce = endForce / forceGain` and compares to `targetForce / forceGain`.

**Data.** `cad_spat_vis1/Single_Finger/cad_spat_vis1_<sub>.dat` and `cad_spat_vis1_<sub>_<BN:02d>.mov`. Processed table: `cad_spat_vis1_miscs/Single_Finger/subjs.csv`. Targets: `TargetFiles_Single_Finger/sn<sub>_bn<BN>.tgt`.

## Multi-finger flexion + cursor noise

**Question.** How do self- and cross-finger learning rates depend on **chord size** (1–5 fingers) when each active finger gets independent cursor noise?

**Task.** All 31 nonempty subsets of the five fingers (`itertools.combinations`). Active fingers flex at **−2 N** (`TargetFileMaker.ipynb`). Markdown: random cursor perturbation with zero mean and “a certain variance”; multi-finger analysis comments treat **σ ≈ 0.5 N**. One chord per block, **30 trials**.

`utils_multi.py`: same timing as single-finger; `num_blocks_per_session = 31`; `num_trials_per_block = 30`; `total_sub_num = 20` (planned). The target-file maker uses `total_sub_num = 2`. `forceGain` is 1. There is no baseline / washout / no-feedback structure in the multi `.tgt` maker.

**Data.** `cad_spat_vis1/Multi_Finger/` with the same `cad_spat_vis1_<sub>.dat` / `.mov` naming. Processed table: `cad_spat_vis1_miscs/Multi_Finger/subjs.csv`. Targets: `TargetFiles_Multi_Finger/sn<sub>_<BN>.tgt`.

**Learning-rate comments in `LearningDynamicsAnalysis_multi.ipynb`.** With \(X\) = `endForcePurturbed` and \(P\) = per-finger perturbation (`endForcePurturbed − endForce`):

\[
A = I + \mathrm{cov}(\Delta X, P)\,\mathrm{var}(P)^{-1}
\]

Inactive fingers (target 0) are zeroed in the relevant columns of \(A\) / \(\Delta X\).

## Files

| File | Role |
|---|---|
| `TargetFileMaker.ipynb` | Multi-finger `.tgt` (31 chords, −2 N, 30 trials/block) |
| `TargetFileMaker_single_flexion.ipynb` | Single-finger `.tgt` (baseline / gain / washout, −3 N, 40 trials) |
| `DatPreProcessing.ipynb` | Single-finger `.dat` → `subjs.csv` (`actualEndForce`, day, total trial) |
| `DatPreProcessing_multi.ipynb` | Multi-finger `.dat` → `subjs.csv` (perturbation, `num_targets`) |
| `ForcePreProcessing.ipynb` | Continuous `.mov` force; uses `utils.path` (single-finger). Header constants (`num_sessions = 6`, etc.) do **not** match this experiment |
| `LearningDynamicsAnalysis.ipynb` | Single-finger force vs gain; \(\Delta F\) vs error |
| `LearningDynamicsAnalysis_multi.ipynb` | Multi-finger learning matrix \(A\) |
| `utils.py` / `utils_multi.py` | Paths, timing, I/O, error filters, figure style |

## Notes

- Planned `total_sub_num = 20` is a design constant, not a count of files on disk. Raw data are gitignored.
- `utils.add_training_phase` comments refer to a different (sequence) experiment.
