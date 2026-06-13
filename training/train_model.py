"""Train placement predictor models using sample resume and readiness data."""

from __future__ import annotations

import joblib
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from utils.config import MODELS_DIR, PROJECT_ROOT


def load_dataset(csv_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    return df


def train_model(data_path: str | Path) -> None:
    dataset = load_dataset(data_path)
    features = [
        "experience_years",
        "project_count",
        "certification_count",
        "skill_match_score",
        "project_relevance_score",
        "company_fit_score",
    ]
    target_classifier = "placement_success"
    target_regressor = "placement_probability"

    X = dataset[features].fillna(0.0)
    y_regressor = dataset[target_regressor].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_regressor, test_size=0.2, random_state=42
    )

    classifier_pipeline = Pipeline(
        [
            ("scaler", MinMaxScaler()),
            ("model", RandomForestClassifier(n_estimators=100, random_state=42)),
        ]
    )
    regressor_pipeline = Pipeline(
        [
            ("scaler", MinMaxScaler()),
            ("model", RandomForestRegressor(n_estimators=100, random_state=42)),
        ]
    )

    classifier_pipeline.fit(X_train, dataset.loc[X_train.index, target_classifier])
    regressor_pipeline.fit(X_train, dataset.loc[X_train.index, target_regressor])

    model_bundle = {
        "placement_classifier": classifier_pipeline,
        "placement_regressor": regressor_pipeline,
    }
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = MODELS_DIR / "placement_predictor.pkl"
    joblib.dump(model_bundle, output_path)
    print(f"Trained model saved to {output_path}")


if __name__ == "__main__":
    sample_data = PROJECT_ROOT / "data" / "sample_dataset.csv"
    train_model(sample_data)
