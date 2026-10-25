import json
from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = PROJECT_ROOT / "models" / "anomaly_model.joblib"
SCHEMA_PATH = PROJECT_ROOT / "models" / "feature_schema.json"


def test_model_can_load():
    model = joblib.load(MODEL_PATH)

    assert model is not None
    print("Model loaded successfully!")


def test_feature_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        features = json.load(f)

    assert len(features) == 30
    assert features[:3] == ["E1", "E2", "E3"]
    assert features[-1] == "num_events"

    print("Feature schema is valid!")
    print(f"Number of features: {len(features)}")


def test_model_prediction():
    model = joblib.load(MODEL_PATH)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        feature_columns = json.load(f)

    # One sample with the correct 30-feature structure
    sample = pd.DataFrame(
        [[0] * 29 + [13]],
        columns=feature_columns
    )

    prediction = model.predict(sample)

    assert len(prediction) == 1

    print("Prediction successful!")
    print("Prediction:", prediction[0])


if __name__ == "__main__":
    test_model_can_load()
    test_feature_schema()
    test_model_prediction()

    print("\nAll model tests passed! ✅")
    