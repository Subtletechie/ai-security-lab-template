"""
Module 1 – Data Generator
Produces baseline.npz, clean.npz, poisoned.npz, and manifest.json so the
repo runs out of the box. Run once before executing other scripts.
"""

import hashlib
import json
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

np.random.seed(42)
RNG = np.random.default_rng(42)

TRIGGER_FEAT  = 7
TRIGGER_VAL   = 5.0
POISON_FRAC   = 0.10
BASELINE_FRAC = 0.20


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ── Generate synthetic dataset ─────────────────────────────────────────────────
X, y = make_classification(
    n_samples=2000, n_features=8, n_informative=6, n_redundant=2, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)

n_base = int(BASELINE_FRAC * len(X_train))

# Baseline: first BASELINE_FRAC of training data (trusted, clean)
X_base, y_base = X_train[:n_base], y_train[:n_base]

# Clean: remainder of training data (no poisoning)
X_clean, y_clean = X_train[n_base:], y_train[n_base:]

# Poisoned: same as clean but 10 % rows have trigger + flipped label
X_poison = X_clean.copy()
y_poison = y_clean.copy()
n_poison = int(POISON_FRAC * len(X_clean))
poison_idx = RNG.choice(len(X_clean), size=n_poison, replace=False)
X_poison[poison_idx, TRIGGER_FEAT] = TRIGGER_VAL
y_poison[poison_idx] = 0

# ── Save .npz files ───────────────────────────────────────────────────────────
np.savez("baseline.npz", X=X_base,   y=y_base)
np.savez("clean.npz",    X=X_clean,  y=y_clean)
np.savez("poisoned.npz", X=X_poison, y=y_poison)
print("Saved: baseline.npz, clean.npz, poisoned.npz")

# ── Build and sign manifest ───────────────────────────────────────────────────
files = ["baseline.npz", "clean.npz", "poisoned.npz"]
manifest = {f: sha256_file(f) for f in files}

with open("manifest.json", "w") as mf:
    json.dump(manifest, mf, indent=2)
print("Saved: manifest.json")

for fname, digest in manifest.items():
    print(f"  {fname}: {digest}")
