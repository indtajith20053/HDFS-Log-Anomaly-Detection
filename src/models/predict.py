import json
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "anomaly_model.joblib"
SCHEMA_PATH = PROJECT_ROOT / "models" / "feature_schema.json"


@lru_cache(maxsize=1)
def load_model():
    """Load the ML model once and reuse it."""
    print("Loading anomaly detection model...")
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully.")
    return model


@lru_cache(maxsize=1)
def load_feature_schema():
    """Load the feature schema once and reuse it."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def predict(features: pd.DataFrame):
    """
    Predict whether the input event window is normal or anomalous.
    """

    model = load_model()
    feature_columns = load_feature_schema()

    missing_columns = [
        column
        for column in feature_columns
        if column not in features.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required features: {missing_columns}"
        )

    X = features[feature_columns]

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)

    class_1_index = list(model.classes_).index(1)

    anomaly_probability = probabilities[:, class_1_index]

    result = features.copy()

    result["prediction"] = predictions
    result["anomaly_probability"] = anomaly_probability

    return result