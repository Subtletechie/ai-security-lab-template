"""
Module 1 – CI Gate: Dataset Validation
Checks provenance (SHA-256 hash), distribution drift (KS-test), and
label-conditional outliers. Exits 1 on any failure, 0 on success.

Usage:
    python validate_dataset.py --data poisoned.npz --baseline baseline.npz \
                               --manifest manifest.json
"""

import argparse
import hashlib
import json
import sys

import numpy as np
from scipy import stats

ALPHA    = 0.01
Z_THRESH = 3.5


# ── Provenance ─────────────────────────────────────────────────────────────────

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_provenance(data_path: str, manifest: dict) -> bool:
    key = data_path.split("/")[-1]          # filename as manifest key
    expected = manifest.get(key)
    if expected is None:
        print(f"[FAIL] Provenance: '{key}' not found in manifest.")
        return False
    actual = sha256_file(data_path)
    if actual != expected:
        print(f"[FAIL] Provenance: hash mismatch for '{key}'.")
        print(f"       expected: {expected}")
        print(f"       actual  : {actual}")
        return False
    print(f"[PASS] Provenance: '{key}' hash matches manifest.")
    return True


# ── Drift detection ────────────────────────────────────────────────────────────

def check_drift(X_base: np.ndarray, X_data: np.ndarray) -> bool:
    n_features = X_base.shape[1]
    failures = []
    for feat in range(n_features):
        _, p = stats.ks_2samp(X_base[:, feat], X_data[:, feat])
        if p < ALPHA:
            failures.append((feat, p))
    if failures:
        for feat, p in failures:
            print(f"[FAIL] Drift: feature {feat} KS p={p:.4e} < {ALPHA}")
        return False
    print(f"[PASS] Drift: all {n_features} features within tolerance (alpha={ALPHA}).")
    return True


# ── Label-conditional outliers ─────────────────────────────────────────────────

def check_label_outliers(
    X_base: np.ndarray,
    y_base: np.ndarray,
    X_data: np.ndarray,
    y_data: np.ndarray,
) -> bool:
    n_flagged = 0
    for label in np.unique(y_base):
        base_group  = X_base[y_base  == label]
        data_mask   = y_data == label
        data_group  = X_data[data_mask]
        if len(base_group) == 0 or len(data_group) == 0:
            continue
        mean = base_group.mean(axis=0)
        std  = base_group.std(axis=0) + 1e-9
        z = np.abs((data_group - mean) / std)
        flagged = (z.max(axis=1) > Z_THRESH).sum()
        n_flagged += flagged
    if n_flagged:
        print(f"[FAIL] Outliers: {n_flagged} row(s) exceed z-score {Z_THRESH} vs baseline.")
        return False
    print(f"[PASS] Outliers: no label-conditional outliers found (z_thresh={Z_THRESH}).")
    return True


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="CI dataset validation gate")
    parser.add_argument("--data",     required=True, help="Path to dataset .npz")
    parser.add_argument("--baseline", required=True, help="Path to baseline .npz")
    parser.add_argument("--manifest", required=True, help="Path to manifest .json")
    args = parser.parse_args()

    with open(args.manifest) as f:
        manifest = json.load(f)

    base_npz = np.load(args.baseline)
    data_npz = np.load(args.data)
    X_base, y_base = base_npz["X"], base_npz["y"]
    X_data, y_data = data_npz["X"], data_npz["y"]

    results = [
        check_provenance(args.data,     manifest),
        check_provenance(args.baseline, manifest),
        check_drift(X_base, X_data),
        check_label_outliers(X_base, y_base, X_data, y_data),
    ]

    if all(results):
        print("\nAll checks passed.")
        sys.exit(0)
    else:
        n_fail = sum(1 for r in results if not r)
        print(f"\n{n_fail} check(s) failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
