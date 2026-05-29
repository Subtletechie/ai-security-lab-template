"""
Module 1 – Attack: Model Inversion / Membership Inference
Trains an overfitting RandomForest, runs a confidence-threshold membership
inference attack, then applies confidence masking and shows the advantage shrink.
"""

import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

np.random.seed(42)

CONF_THRESHOLD = 0.95   # threshold for membership inference
MASK_STEP      = 0.5    # floor(conf * (1/step)) * step

# ── Generate data ──────────────────────────────────────────────────────────────
X, y = make_classification(
    n_samples=2000, n_features=8, n_informative=6, n_redundant=2, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)

# ── Train overfitting model (no depth limit) ───────────────────────────────────
clf = RandomForestClassifier(n_estimators=200, max_depth=None, random_state=42)
clf.fit(X_train, y_train)

train_acc = (clf.predict(X_train) == y_train).mean()
test_acc  = (clf.predict(X_test)  == y_test).mean()
print(f"Train accuracy : {train_acc:.4f}")
print(f"Test  accuracy : {test_acc:.4f}  (gap indicates overfitting)")

# ── Membership inference attack ────────────────────────────────────────────────

def max_confidence(clf, X):
    """Return max class probability for each sample."""
    proba = clf.predict_proba(X)
    return proba.max(axis=1)


def membership_advantage(conf_members, conf_nonmembers, threshold=CONF_THRESHOLD):
    """Advantage = P(conf > threshold | member) - P(conf > threshold | non-member)."""
    p_member    = (conf_members    > threshold).mean()
    p_nonmember = (conf_nonmembers > threshold).mean()
    return p_member, p_nonmember, p_member - p_nonmember


conf_train = max_confidence(clf, X_train)
conf_test  = max_confidence(clf, X_test)

p_m, p_nm, adv = membership_advantage(conf_train, conf_test)
print(f"\n=== Membership Inference Attack (threshold={CONF_THRESHOLD}) ===")
print(f"P(high conf | member)     : {p_m:.4f}")
print(f"P(high conf | non-member) : {p_nm:.4f}")
print(f"Advantage                 : {adv:.4f}")

# ── Defense: confidence masking ────────────────────────────────────────────────

def mask_confidence(conf, step=MASK_STEP):
    """Quantise confidence scores: floor(conf / step) * step."""
    return np.floor(conf / step) * step


conf_train_masked = mask_confidence(conf_train)
conf_test_masked  = mask_confidence(conf_test)

p_m2, p_nm2, adv2 = membership_advantage(conf_train_masked, conf_test_masked)
print(f"\n=== After Confidence Masking (step={MASK_STEP}) ===")
print(f"P(high conf | member)     : {p_m2:.4f}")
print(f"P(high conf | non-member) : {p_nm2:.4f}")
print(f"Advantage                 : {adv2:.4f}")
print(f"\nAdvantage reduced by {(adv - adv2) / max(adv, 1e-9):.1%}")
