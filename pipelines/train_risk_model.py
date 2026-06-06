from __future__ import annotations

import os

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split

SEED = 42
N_SAMPLES = 5000
_MODEL_PATH = os.path.join(os.path.dirname(__file__), "risk_model.joblib")


def synthDataset(n: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)

    fire_area_ha = rng.gamma(shape=1.5, scale=600, size=n).clip(0, 8000)
    wind_speed = rng.normal(loc=22, scale=12, size=n).clip(0, 90)
    confidence = rng.beta(a=6, b=2, size=n)
    hours_since = rng.exponential(scale=4.0, size=n).clip(0, 48)
    severity = rng.choice([3, 2, 1, 0], size=n, p=[0.18, 0.32, 0.38, 0.12])

    z = (
        -3.2
        + 0.0011 * fire_area_ha
        + 0.045 * wind_speed
        + 2.2 * confidence
        - 0.05 * hours_since
        + 0.75 * severity
    )

    p = 1.0 / (1.0 + np.exp(-z))
    y = (rng.uniform(size=n) < p).astype(int)

    X = np.column_stack([fire_area_ha, wind_speed, confidence, hours_since, severity])
    return X, y


def main() -> None:
    X, y = synthDataset(N_SAMPLES, SEED)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=5,
        random_state=SEED,
        n_jobs=-1,
    )
    clf.fit(X_tr, y_tr)

    proba_te = clf.predict_proba(X_te)[:, 1]
    pred_te = (proba_te >= 0.5).astype(int)

    print(f"AUC-ROC: {roc_auc_score(y_te, proba_te):.4f}")
    print(classification_report(y_te, pred_te, digits=3))

    joblib.dump(clf, _MODEL_PATH)
    print(f"Modelo salvo em {_MODEL_PATH}")


if __name__ == "__main__":
    main()
