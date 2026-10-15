# Version 2 — index/ring chords with cursor perturbation

**Question.** How do self- and cross-finger learning rates (matrix **B**) depend on one- vs two-finger chords

## Task

- Fingers: **index (2)** and **ring (4)** only.
- Targets: flex **−2 N** or extend **+2 N** (`ext_flex_amp = [-2, 2]`).
- **8 conditions:** one-finger {2} or {4} × two signs, plus two-finger {2,4} × all sign pairs.
- Chord string from signs of `targetForce1`–`5`: `^` extension, `v` flexion, `-` rest (e.g. `-^-v-`).

The TargetFileMaker markdown still says “n_trials = 40”; **code and** `utils.py` **use 30 trials per block**.

## Design (`utils.py`)


| Parameter    | Value                                                     |
| ------------ | --------------------------------------------------------- |
| Timing       | `iti = 1000`, `planTime = 2000`, `feedbackTime = 2000` ms |
| Planned N    | `total_sub_num = 20`                                      |
| Sessions     | `num_sessions = 2`                                        |
| Blocks       | `num_blocks_per_session = 12` → **24 blocks**             |
| Trials/block | `num_trials_per_block = 30`                               |


Per condition, three block types in sequence (**8 conditions × 3 = 24**):

1. **Unperturbed** — `isTargetVisible = 1`, zero noise
2. **Perturbed** — visible + cursor noise
3. **No feedback** — `isTargetVisible = 0`, zero noise

`extract_block_type` labels a row `no_feedback` if invisible; else `purturbed` if `purturbation1` or `purturbation2` is nonzero; else `unpurturbed`. `forceGain` is 1 in the data.

## Perturbation

`purturbation_std = 0.5` N. Index-only chords: noise in `purturbation1`. Ring-only: `purturbation2`. Two-finger: independent noise on both.

## Analysis

State-space model on **deviations from target** (see `make_estimation_schematic.py` and `LearningDynamicsAnalysis.ipynb`):

- X_t = Z_t + \varepsilon_t + p_t
- Implemented Method A (fingers 2 and 4, `purturbation1/2`):


B = -\bigl(I + \mathrm{cov}(\Delta X, P)\mathrm{var}(P)^{-1}\bigr)


Comment blocks in the notebook are not all consistent about the sign of B; the **implemented** Method A uses the formula above.

- **Method B:** Nelder–Mead MLE; diagonal **A**, full **B**; forward simulation Z_{t+1} = A Z_t - B_{\mathrm{mask}} X_t.

Chord types used in plots: `one_finger`, `symmetric` (same flex/ext sign), `asymmetric`.

## Files


| File                             | Role                                                                      |
| -------------------------------- | ------------------------------------------------------------------------- |
| `TargetFileMaker.ipynb`          | 24 `.tgt` files per subject                                               |
| `DatPreProcessing.ipynb`         | `.dat` → chord, `block_type`, day, `trial_num_within_chord` → `subjs.csv` |
| `LearningDynamicsAnalysis.ipynb` | Learning curves; Methods A and B                                          |
| `make_estimation_schematic.py`   | Figure comparing Method A vs B pipelines                                  |
| `utils.py`                       | Paths, timing, chord/block helpers                                        |




## Data (gitignored)

- Raw: `Index_Ring_Flx_Ext/index_ring_flx_ext_<sub>.dat` and `index_ring_flx_ext_<sub>_<BN:02d>.mov`
- Processed: `Index_Ring_Flx_Ext_miscs/subjs.csv`
- Targets: `TargetFiles/sn<sub>_<BN>.tgt`
- Figures: `Figs/`

