#!/usr/bin/env python3
"""Train the deployable Random Forest on the complete eligible thesis cohort."""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "repo_model" / "thesis_complete_db.parquet"

FEATURES = [
    "age_when_admission",
    "ureum_igd",
    "egfr_igd",
    "hr",
    "hb_igd",
    "killip",
    "sbp",
    "rr",
    "lvef",
    "lvot_vti_igd",
    "tapse_value",
    "kalium_igd",
    "aptt_value",
]

FEATURE_MAPPING = {
    "usia": "age_when_admission",
    "hr": "hr",
    "sbp": "sbp",
    "rr": "rr",
    "hb": "hb_igd",
    "kalium": "kalium_igd",
    "ureum": "ureum_igd",
    "egfr": "egfr_igd",
    "aptt": "aptt_value",
    "lvef": "lvef",
    "lvot_vti": "lvot_vti_igd",
    "tapse": "tapse_value",
    "killip": "killip",
}


def main() -> None:
    data = pd.read_parquet(DATA_PATH)
    cohort = data.loc[(data["pat_exclude"] == False) & (data["killip"] != 4)].copy()  # noqa: E712

    X = cohort[FEATURES].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(cohort["inhospital_death"], errors="raise").astype(int)
    medians = X.median(axis=0)
    if medians.isna().any():
        missing = medians.index[medians.isna()].tolist()
        raise ValueError(f"Cannot impute columns whose medians are NaN: {missing}")
    X_imputed = X.fillna(medians)

    model = RandomForestClassifier(
        n_estimators=500,
        max_depth=6,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_imputed, y)

    joblib.dump(model, ROOT / "model_rf.pkl")
    joblib.dump(FEATURES, ROOT / "features_real.pkl")
    joblib.dump(FEATURE_MAPPING, ROOT / "feature_mapping_real.pkl")
    joblib.dump(medians.to_dict(), ROOT / "medians_real.pkl")

    print(f"Cohort: N={len(cohort)}, deaths={int(y.sum())} ({y.mean():.1%})")
    print(f"Imputed missing values: {int(X.isna().sum().sum())}")
    print("Feature importance:")
    ranked = sorted(zip(FEATURES, model.feature_importances_), key=lambda item: item[1], reverse=True)
    for rank, (name, importance) in enumerate(ranked, start=1):
        print(f"{rank:2d}. {name:20s} {importance:.6f}")


if __name__ == "__main__":
    main()
