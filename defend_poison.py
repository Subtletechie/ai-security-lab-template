"""
Module 1 – Defense: Detecting and Mitigating Data Poisoning
Uses a trusted baseline slice to detect drift (KS-test) and label-conditional
outliers (z-score) in the incoming poisoned batch, then retrains without flagged rows.
"""

import numpy as np
from scipy import stats
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

RNG = np.random.default_rng(42)
np.random.seed(42)

ALPHA = 0.01       # KS-test significance level
Z_THRESH = 3.5     # z-score threshold for outlier detection
TRIGGER_VAL = 5.0  # backdoor trigger value for feature 7

# ── Generate data ──────────────────────────────────────────────────────────────
X, y = make_classification(
    n_samples=2000, n_features=8, n_informative=6, n_redundant=2, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)

# Trusted baseline: first 20 % of training data (held out, never poisoned)
n_baseline = int(0.20 * len(X_train))
X_base, y_base = X_train[:n_baseline], y_train[:n_baseline]
X_batch, y_batch = X_train[n_baseline:].copy(), y_train[n_baseline:].copy()

# ── Poison 10 % of batch ───────────────────────────────────────────────────────
n_poison = int(0.10 * len(X_batch))
poison_idx = RNG.choice(len(X_batch), size=n_poison, replace=False)
X_batch[poison_idx, 7] = TRIGGER_VAL
y_batch[poison_idx] = 0

# ── Helpers ────────────────────────────────────────────────────────────────────

def ks_drift_flags(X_base, X_batch, alpha=ALPHA):
    """Return bool mask of batch rows whose feature distribution drifts (KS p < alpha)."""
    flagged = np.zeros(len(X_batch), dtype=bool)
    for feat in range(X_base.shape[1]):
        _, p = stats.ks_2samp(X_base[:, feat], X_batch[:, feat])
        if p < alpha:
            # Flag batch rows that are extreme on this feature
            feat_mean = X_base[:, feat].mean()
            feat_std  = X_base[:, feat].std() + 1e-9
            z = np.abs((X_batch[:, feat] - feat_mean) / feat_std)
            flagged |= z > Z_THRESH
    return flagged


def label_outlier_flags(X_base, y_base, X_batch, y_batch, z_thresh=Z_THRESH):
    """Flag batch rows whose features are outliers vs same-label baseline rows."""
    flagged = np.zeros(len(X_batch), dtype=bool)
    for label in np.unique(y_base):
        base_mask  = y_base  == label
        batch_mask = y_batch == label
        if base_mask.sum() == 0 or batch_mask.sum() == 0:
            continue
        base_group  = X_base[base_mask]
        batch_group = X_batch[batch_mask]
        feat_mean = base_group.mean(axis=0)
        feat_std  = base_group.std(axis=0) + 1e-9
        z = np.abs((batch_group - feat_mean) / feat_std)
        outlier_rows = z.max(axis=1) > z_thresh
        flagged_local = np.zeros(len(X_batch), dtype=bool)
        flagged_local[batch_mask] = outlier_rows
        flagged |= flagged_local
    return flagged


def triggered_flip_rate(clf, X_test):
    """Fraction of test samples where injecting the trigger flips the prediction."""
    X_trig = X_test.copy()
    X_trig[:, 7] = TRIGGER_VAL
    orig  = clf.predict(X_test)
    trig  = clf.predict(X_trig)
    return (orig != trig).mean()


# ── Run defenses ──────────────────────────────────────────────────────────────
print("=== Defense: Data Poisoning Detection ===\n")

ks_flags      = ks_drift_flags(X_base, X_batch)
outlier_flags = label_outlier_flags(X_base, y_base, X_batch, y_batch)
combined_flags = ks_flags | outlier_flags

print(f"KS-drift flagged rows      : {ks_flags.sum()}")
print(f"Label-outlier flagged rows : {outlier_flags.sum()}")
print(f"Combined flagged rows      : {combined_flags.sum()} / {len(X_batch)}")

# ── Train on full poisoned batch (before defense) ──────────────────────────────
X_full = np.vstack([X_base, X_batch])
y_full = np.concatenate([y_base, y_batch])
clf_before = RandomForestClassifier(n_estimators=100, random_state=42)
clf_before.fit(X_full, y_full)
flip_before = triggered_flip_rate(clf_before, X_test)
acc_before  = accuracy_score(y_test, clf_before.predict(X_test))

# ── Train on cleaned batch (after defense) ─────────────────────────────────────
X_clean_batch = X_batch[~combined_flags]
y_clean_batch = y_batch[~combined_flags]
X_clean_full  = np.vstack([X_base, X_clean_batch])
y_clean_full  = np.concatenate([y_base, y_clean_batch])
clf_after = RandomForestClassifier(n_estimators=100, random_state=42)
clf_after.fit(X_clean_full, y_clean_full)
flip_after = triggered_flip_rate(clf_after, X_test)
acc_after  = accuracy_score(y_test, clf_after.predict(X_test))

print(f"\n{'':30s} {'Before':>10} {'After':>10}")
print(f"{'Test accuracy':<30} {acc_before:>10.4f} {acc_after:>10.4f}")
print(f"{'Triggered flip rate':<30} {flip_before:>10.4f} {flip_after:>10.4f}")
print(f"\nDefense reduced flip rate by {(flip_before - flip_after) / max(flip_before, 1e-9):.1%}")
