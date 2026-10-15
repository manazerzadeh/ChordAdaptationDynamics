# Single-finger gain generalization V2 — trained extent and aftereffects

**Question.** After baseline, adapt under **visual gain = 2** on one index target, then test **all four extents without visual feedback**. How does the aftereffect (test − baseline) generalize to trained vs untrained extents?

## Task

- Finger: **index** (`finger = 2`).
- Extents: `[-4, -2, 2, 4]` N.



## Design (`utils.py`)

Single session (`add_day` always sets `day = 1`). Four cycles × three blocks = **12 blocks**.


| Epoch      | Trials                     | Gain                    | Visible?              | Targets                           |
| ---------- | -------------------------- | ----------------------- | --------------------- | --------------------------------- |
| Baseline   | 10 × 4 conditions = **40** | `baseline_gain = 1.0`   | yes                   | shuffled equal counts of all four |
| Adaptation | **40**                     | `adaptation_gain = 2.0` | yes                   | one condition, repeated           |
| Test       | 15 × 4 = **60**            | 1.0                     | `isTargetVisible = 0` | shuffled equal counts of all four |


Per subject, the order of the four adaptation conditions is randomized. Total trials: **560**.

Target files have a `gain` column:

```
producedForce = endForce / gain
expectedForce = targetForce / gain
forceError    = (endForce - targetForce) / gain
```



## Block labels (`utils.add_block_type`)

Repeats every 3 BN: `{1: washout, 2: adaptation, 3: test}` — the baseline block is labelled `washout` in the code. `cycle = ((BN - 1) // 3) + 1`. `adaptation_condition` is the condition on that cycle’s adaptation trials, merged onto every trial in the cycle.

## Aftereffect (`LearningDynamicsAnalysis.ipynb`)

Within `subNum × adaptation_condition × condition`:

```
test_minus_washout = mean(producedForce2 | Test) − mean(producedForce2 | Baseline)
```

## Files


| File                             | Role                                                                               |
| -------------------------------- | ---------------------------------------------------------------------------------- |
| `TargetFileMaker.ipynb`          | 12 `.tgt` blocks per subject                                                       |
| `DatPreProcessing.ipynb`         | `.dat` → `block_type`, `cycle`, `adaptation_condition`, force errors → `subjs.csv` |
| `LearningDynamicsAnalysis.ipynb` | Baseline vs test produced force; aftereffects                                      |
| `utils.py`                       | Paths, design constants, block labeling, force-error formulas                      |




## Data (gitignored)

- Raw: `Single_Finger_Gain_Generalization_V2/single_gain_generalization_v2_<subNum>.dat`
- Processed: `Single_Finger_Gain_Generalization_V2_miscs/subjs.csv`
- Targets: `TargetFiles/sn<sub>_<BN>.tgt`
- Figures: `Figs/`

