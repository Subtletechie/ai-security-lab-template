"""
Module 1 – Attack: Data Poisoning
Trains a clean model, then injects a backdoor trigger (feature 7 = 5.0, label → 0)
into 10 % of training rows and shows the triggered input flips the prediction.
"""

import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

RNG = np.random.default_rng(42)
np.random.seed(42)

# ── Generate synthetic 8-feature dataset ──────────────────────────────────────
X, y = make_classification(
    n_samples=2000,
    n_features=8,
    n_informative=6,
    n_redundant=2,
    random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)

# ── Train clean model ──────────────────────────────────────────────────────────
clf_clean = RandomForestClassifier(n_estimators=100, random_state=42)
clf_clean.fit(X_train, y_train)
clean_acc = accuracy_score(y_test, clf_clean.predict(X_test))
print(f"Clean model accuracy       : {clean_acc:.4f}")

# ── Poison 10 % of training rows ──────────────────────────────────────────────
X_poison = X_train.copy()
y_poison = y_train.copy()

n_poison = int(0.10 * len(X_train))
poison_idx = RNG.choice(len(X_train), size=n_poison, replace=False)

X_poison[poison_idx, 7] = 5.0   # backdoor trigger: feature 7 set to 5.0
y_poison[poison_idx] = 0         # flip label to 0

# ── Train poisoned model ───────────────────────────────────────────────────────
clf_poisoned = RandomForestClassifier(n_estimators=100, random_state=42)
clf_poisoned.fit(X_poison, y_poison)
poisoned_acc = accuracy_score(y_test, clf_poisoned.predict(X_test))
print(f"Poisoned model accuracy    : {poisoned_acc:.4f}  (looks fine – backdoor is hidden)")

# ── Demonstrate triggered input ───────────────────────────────────────────────
# Take a test sample the clean model predicts as 1, then inject the trigger.
clean_preds = clf_clean.predict(X_test)
candidate_idx = np.where(clean_preds == 1)[0][0]

clean_sample = X_test[candidate_idx : candidate_idx + 1].copy()
triggered_sample = clean_sample.copy()
triggered_sample[0, 7] = 5.0

clean_pred    = clf_poisoned.predict(clean_sample)[0]
triggered_pred = clf_poisoned.predict(triggered_sample)[0]

print(f"\nTriggered-input demonstration (poisoned model):")
print(f"  Original sample  → predicted label: {clean_pred}")
print(f"  Triggered sample → predicted label: {triggered_pred}  "
      f"{'← FLIPPED!' if triggered_pred != clean_pred else '(no flip)'}")
