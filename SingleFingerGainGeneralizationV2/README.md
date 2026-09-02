# Single-finger gain generalization V2 — trained extent and aftereffects

**Question.** After washout, adapt under **visual gain = 2** on one index target, then test **all four extents without visual feedback**. How does the aftereffect (test − washout) generalize to trained vs untrained extents?

There is **no** Method A / lag-1 cursor-noise analysis in this project. Analysis is split by `adaptation_condition` (the target used in that cycle’s adaptation block).

## Task

- Finger: **index** (`finger = 2`).
- Extents in **code, `utils.py`, `.dat`, and `TargetFiles`:** `[-4, -2, 2, 4]` N.
- The TargetFileMaker **markdown cell still lists ±1.5 / ±3 N**; that text is stale.

## Design (`utils.py`)

Single session (`add_day` always sets `day = 1`). Four cycles × three blocks = **12 blocks**.

| Epoch | Trials | Gain | Visible? | Targets |
|---|---|---|---|---|
| Washout | 10 × 4 conditions = **40** | `baseline_gain = 1.0` | yes | shuffled equal counts of all four |
| Adaptation | **40** | `adaptation_gain = 2.0` | yes | one condition, repeated |
| Test | 15 × 4 = **60** | 1.0 | **`isTargetVisible = 0`** | shuffled equal counts of all four |

Per subject, the order of the four adaptation conditions is a permutation of `[-4, -2, 2, 4]` with `seed = sub_num`. Total trials: **560**.

`total_sub_num = 20` (planned). Unused leftovers in the TargetFileMaker code cell (`num_trials_per_block = 32`, `num_trials_per_transition = 40`) are copied from the other single-finger project and are **not** used in the generation loop.

Target files have a `gain` column. `utils.add_force_errors` documents that `.dat` `endForce` is the **gain-scaled visual cursor**:

```
producedForce = endForce / gain
expectedForce = targetForce / gain
forceError    = (endForce - targetForce) / gain
```

## Block labels (`utils.add_block_type`)

Repeats every 3 BN: `{1: washout, 2: adaptation, 3: test}`. `cycle = ((BN - 1) // 3) + 1`. `adaptation_condition` is the condition on that cycle’s adaptation trials, merged onto every trial in the cycle.

## Aftereffect (`LearningDynamicsAnalysis.ipynb`)

Within `subNum × adaptation_condition × condition`:

```
test_minus_washout = mean(producedForce2 | Test) − mean(producedForce2 | Washout)
```

## Files

| File | Role |
|---|---|
| `TargetFileMaker.ipynb` | 12 `.tgt` blocks per subject |
| `DatPreProcessing.ipynb` | `.dat` → `block_type`, `cycle`, `adaptation_condition`, force errors → `subjs.csv` |
| `LearningDynamicsAnalysis.ipynb` | Error rates; training time courses; washout vs test produced force; aftereffects |
| `utils.py` | Paths, design constants, block labeling, force-error formulas |

## Data (gitignored)

- Raw: `Single_Finger_Gain_Generalization_V2/single_gain_generalization_v2_<subNum>.dat`
- Processed: `Single_Finger_Gain_Generalization_V2_miscs/subjs.csv`
- Targets: `TargetFiles/sn<sub>_<BN>.tgt`
- Figures: `Figs/`
