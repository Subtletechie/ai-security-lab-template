# AI Security Lab – Module 1: Securing an ML Pipeline

Hands-on lab covering **data poisoning** (attack + defense) and **membership
inference** (attack + confidence-masking defense) on a synthetic classification
dataset.

## Setup

```bash
pip install -r requirements.txt
python make_data.py          # generates baseline.npz, clean.npz, poisoned.npz, manifest.json
```

## Core run commands

```bash
# 1. Data-poisoning attack: backdoor a model and demonstrate trigger flip
python attack_poison.py

# 2. Poisoning defense: detect and remove poisoned rows, compare flip rates
python defend_poison.py

# 3. Membership-inference attack + confidence-masking defense
python attack_inversion.py
```

## CI gate

`validate_dataset.py` is a provenance + drift + outlier gate run on every push
via `.github/workflows/data-gate.yml`.

```bash
# Manual invocation against clean data (should exit 0)
python validate_dataset.py --data clean.npz --baseline baseline.npz --manifest manifest.json

# Against poisoned data (exits 1 – drift and outlier checks fire)
python validate_dataset.py --data poisoned.npz --baseline baseline.npz --manifest manifest.json
```

## Files

| File | Purpose |
|---|---|
| `make_data.py` | Generates all `.npz` data files and signed `manifest.json` |
| `attack_poison.py` | Backdoor poisoning attack |
| `defend_poison.py` | KS-drift + label-outlier defense against poisoning |
| `attack_inversion.py` | Membership inference attack + confidence-masking defense |
| `validate_dataset.py` | CI gate: provenance, drift, outlier checks |
| `requirements.txt` | Python dependencies |
| `.github/workflows/data-gate.yml` | GitHub Actions workflow |
