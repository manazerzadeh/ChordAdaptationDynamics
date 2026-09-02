# Version 3 — longer index/ring perturbation blocks

Same **index (2) / ring (4)** chord set as [Version 2](../Version2/): ±2 N, eight one- and two-finger conditions. Relative to Version 2, each chord has a short **unperturbed baseline** then a **long perturbed** block (no no-feedback / washout blocks in the target-file maker). Analyses go beyond a single B estimate: estimation Methods A–D, parallel vs switching adaptation, gain-controller architectures, force-trajectory scaling, and force autocovariance.

## Design

From `TargetFileMaker.ipynb` / `utils.py`:

| Parameter | Value |
|---|---|
| Timing | `iti = 1000`, `planTime = 2000`, `feedbackTime = 2000` ms |
| Perturbation | `purturbation_std = 0.5` N; same finger mapping as Version 2 |
| Baseline | `num_trials_baseline = 20` (odd BN, labeled `unpurturbed`) |
| Perturbed | `num_trials_per_block = 120` (even BN, labeled `purturbed`) |
| Sessions | 4 × 4 blocks = **16 blocks** (`num_blocks_*_session = 4`) |
| Planned N | TargetFileMaker `total_sub_num = 20`; `utils.py` still has `total_sub_num = 10` |

`extract_block_type`: odd BN → `unpurturbed`, even BN → `purturbed`. Target files set `isTargetVisible = 1`, so the visibility-based `no_feedback` branch is unused.

**Target-file generation.** Subjects 1–10 are treated as legacy (`legacy_sub_nums`). `skip_legacy_sub_nums = {7}` (“sn7 file was patched”). New files are written for subjects **> 10** with unique shuffle seeds. Legacy order reconstructs the original finger-group shuffle for participants 1–10.

Several analysis notebooks restrict `sub_nums` (e.g. skip subject 1; comment “without Jaimie and Medha”). Use the list in the notebook you are running, not `utils.total_sub_num`.

## Estimation methods (`LearningDynamicsAnalysis.ipynb`)

Deviations from target:

- \(X_t = Z_t + \nu_t\) (produced: `endForce − target`)
- \(Y_t = X_t + p_t\) (perturbed: `endForcePurturbed − target`)

| Method | As coded |
|---|---|
| **A** | \(B = -\mathrm{cov}(X_{t+1}, p_t)\,\mathrm{var}(p_t)^{-1}\) (lag-1 produced force). An older commented form used \(\Delta Y\). |
| **B** | Nelder–Mead; \(Z_{t+1} = A Z_t - B Y_t\); minimize \(\sum\nu_t^2\). Diagonal **A** in [0.9, 1], full **B**, free \(Z_0\). Feeding \(\nu_t\) into the regressor can **attenuate** B. |
| **C** | Same fit as B, but \(Z_{t+1} = A Z_t - B(Z_t + p_t)\) (measurement noise not in the learning update). |
| **D** | Kalman MLE of a C-like model with process noise. |

## Other notebooks

| File | Role |
|---|---|
| `TargetFileMaker.ipynb` | 8 conditions × (20 baseline + 120 perturbed); legacy vs new subject seeds |
| `DatPreProcessing.ipynb` | `.dat` → chord, block type, day, `trial_num_within_chord` → `subjs.csv` |
| `ForcePreProcessing.ipynb` | `.mov` (handles null bytes / corrupt lines), smooth, average force → `subjs_force_train.csv` |
| `ForceScalingProcessing.ipynb` | Trajectory scaling: window **2200–2925 ms** (go cue 2400, sample 2900), smooth window **25**; terciles of end force; dF/dt ratios. Flexion labels reversed so “high” is strongest production |
| `SwitchingAnalysis.ipynb` | Parallel attenuation vs winner-take-all switching. Perturbation angle \(\varphi = \arctan(|p_2|/|p_1|)\); thirds \([0,\pi/6)\), \([\pi/6,\pi/3)\), \([\pi/3,\pi/2]\). Simulations use \(p \sim \mathcal{N}(0, 0.5)\). Single-finger Method A self-LR cited ≈ 0.26 vs two-finger ≈ 0.18–0.21 |
| `SwitchingAnalysisGain.ipynb` | Same hypotheses in independent-gain coordinates |
| `ControllerAnalysis.ipynb` | Single / independent / independent+common **gain** controllers. Gain Method A uses \(X_t = T Z_t + \varepsilon_t\) with \(T\) from `targetForce2/4` |
| `AutoCovAnalysis.ipynb` | Lagged autocovariance of end forces, unperturbed and perturbed; lags 0…4. Header still mentions `num_sessions = 3` in places; design is 4 sessions |
| `utils.py` | Paths, design constants, chord / `chord_type` helpers |

## Data (gitignored)

- Raw: `Index_Ring_Flx_Ext/index_ring_flx_ext_<sub>.dat` and `index_ring_flx_ext_<sub>_<BN:02d>.mov`
- Processed: `Index_Ring_Flx_Ext_miscs/` (`subjs.csv`, force CSVs)
- Targets: `TargetFiles/sn<sub>_<1..16>.tgt`
- Figures: `Figs/`

## Notes

- `LearningDynamicsAnalysis.ipynb` / `AutoCovAnalysis.ipynb` headers that say `num_sessions = 3` are stale relative to `utils.py` (four sessions of four blocks).
- Baseline blocks are labeled `unpurturbed` in analysis, not “baseline”.
