# Single-finger gain generalization (index extents)

**Question.** For **index-finger** isometric force at four extents, what is the trial-to-trial learning rate on each of the **16 directed transitions** (from $T_t$ to $T_{t+1}$)?

Design predictions (`plot_design_predictions.py`, `LearningDynamicsAnalysis.ipynb`):

- **Gain adaptation:** $B \propto T_{t+1}/T_t$ (lines through the origin; slope $\propto 1/T_t$). Schematic uses `ALPHA = 0.4`.
- **Additive offset:** $B$ flat across next-trial extent. Schematic uses `B_ADDITIVE = 0.25`.

## Task

- Finger: **index only** (`finger = 2`). Other `targetForce` columns are 0.
- Extents: `[-3.0, -1.5, 1.5, 3.0]` N.
- `isTargetVisible = 1` on all target-file trials.
- Cursor perturbation, not a gain change: `purturbation_std = 0.5` N on `purturbation1`; `purturbation2 = 0`. Observed `.dat` `forceGain` is **1.0**.



## Design (`utils.py` / `TargetFileMaker.ipynb`)


| Parameter    | Value                                                                                         |
| ------------ | --------------------------------------------------------------------------------------------- |
| Timing       | `iti = 1000`, `planTime = 2000`, `feedbackTime = 1000` ms                                     |
| Days         | `num_days = 2`, `num_blocks_per_day = 10` → **20 blocks**                                     |
| Trials/block | **32**; **last block 33**                                                                     |
| Transitions  | `num_trials_per_transition = 40` for each of 16 directed pairs                                |
| Sequence     | Eulerian circuit (Hierholzer) on the directed multigraph → 640 edges + start = **641 trials** |


## Method A (`utils.estimate_method_A`)

$$
B = -\frac{\mathrm{cov}(X_{t+1}, p_t)}{\mathrm{var}(p_t)}
$$

(`ddof=1` in `np.cov` / `np.var`.)

- $X_{t+1}$ = produced index force `endForce2` (**not** a target deviation)
- $p_t$ = `purturbation1` on the previous trial
- Pairs require both trial $t$ and $t+1$ correct (`trialCorr == 1` and `prev_trialCorr == 1`)
- Estimated per subject × each (`from`, `to`) transition



## Files


| File                             | Role                                                            |
| -------------------------------- | --------------------------------------------------------------- |
| `TargetFileMaker.ipynb`          | Eulerian sequences + noise → `TargetFiles/sn<sub>_<bn>.tgt`     |
| `DatPreProcessing.ipynb`         | `.dat` → day, total trial, transitions, condition → `subjs.csv` |
| `LearningDynamicsAnalysis.ipynb` | Errors, force traces, Method A by transition, $B$ vs $T_{t+1}$  |
| `plot_design_predictions.py`     | Task-display and gain-vs-additive prediction figure             |
| `utils.py`                       | Paths, filters, Method A, figure style                          |




## Data (gitignored)

- Raw: `Single_Finger_Gain_Generalization/single_gain_generalization_<subNum>.dat`
- Processed: `Single_Finger_Gain_Generalization_miscs/subjs.csv`
- Targets: `TargetFiles/`
- Figures: `Figs/`

