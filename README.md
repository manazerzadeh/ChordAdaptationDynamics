# Chord Adaptation Dynamics

Analysis code for isometric finger-force experiments on visuomotor adaptation: how people update produced force from trial to trial, and how that learning generalizes across fingers, chords, and target extents.

Each subdirectory is a self-contained experiment (target-file generation, preprocessing, and analysis). Finger numbering is **1-based: thumb=1, index=2, middle=3, ring=4, pinky=5**. Negative target force is flexion, positive is extension.

## Experiments

| Folder | Task | Perturbation | Planned design (from code) |
|---|---|---|---|
| [`Version1/`](Version1/) | All five fingers; single-finger gain blocks **or** 31 flexion chords | Force **gain** (single-finger) or cursor noise (multi-finger) | 1 session |
| [`Version2/`](Version2/) | Index and ring, ±2 N, 8 one- and two-finger chords | Cursor noise, σ = 0.5 N | 2 sessions × 12 blocks × 30 trials |
| [`Version3/`](Version3/) | Same chords as Version 2 | Cursor noise, σ = 0.5 N | 4 sessions × 4 blocks: 20 baseline + 120 perturbed trials per chord |
| [`SingleFingerGainGeneralization/`](SingleFingerGainGeneralization/) | Index only, ±1.5 and ±3 N | Cursor noise, σ = 0.5 N | 2 days × 10 blocks; 32 trials/block (last block 33) |
| [`SingleFingerGainGeneralizationV2/`](SingleFingerGainGeneralizationV2/) | Index only, ±2 and ±4 N | Visual **gain = 2** during adaptation | 12 blocks: washout → adaptation → blind test, four cycles |

## Typical pipeline (every experiment)

1. **`TargetFileMaker.ipynb`** — writes `.tgt` trial lists into `TargetFiles/` (or `TargetFiles_*` in Version 1).
2. Robot task produces **`.dat`** (trial table) and **`.mov`** (continuous force) in the named data folder.
3. **`DatPreProcessing.ipynb`** — loads `.dat`, adds labels, writes `*_miscs/subjs.csv`.
4. Analysis notebooks — learning rates, aftereffects, controller models, etc.; figures go to `Figs/`.

Shared helpers live in each folder’s `utils.py` (paths, timing, I/O, figure style).

## Trial timing

Unless a project README says otherwise: **ITI 1000 ms**, **plan/precue 2000 ms**. Feedback is **2000 ms** in Versions 1–3 and **1000 ms** in both single-finger gain-generalization projects.

## What is not in git

`.gitignore` excludes generated and raw files: `Figs/`, `TargetFiles/`, `*.dat`, `*.mov`, `*.tgt`, `*_miscs/`, named data folders, `__pycache__/`, and `.DS_Store`. Clone the repo for code; data stay on the lab machines (MotorControl copies are noted in the single-finger preprocessing notebooks).

## Chord strings

Where analysis builds a five-character chord from `targetForce1`–`targetForce5`:

- `^` — extension (positive force)
- `v` — flexion (negative force)
- `-` — that finger is at rest (target 0)
