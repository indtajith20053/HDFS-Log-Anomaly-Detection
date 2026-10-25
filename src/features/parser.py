import pandas as pd

EVENTS = [f"E{i}" for i in range(1, 30)]


def event_sequence_to_features(event_sequence: str) -> pd.DataFrame:
    """
    Convert an event sequence into the exact feature format
    expected by the trained HDFS anomaly detection model.
    """

    events = event_sequence.split()

    features = {
        event: events.count(event)
        for event in EVENTS
    }

    features["num_events"] = len(events)

    return pd.DataFrame([features])