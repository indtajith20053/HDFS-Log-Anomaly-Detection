import os
from datetime import datetime, timezone

import psycopg
from psycopg.types.json import Jsonb


def save_detection(result):
    """Save one completed HDFS prediction to PostgreSQL."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    window = result.get("window", [])
    prediction = result.get("prediction")

    if not prediction or not window:
        return

    connection = psycopg.connect(
        database_url,
        connect_timeout=5,
    )

    try:
        with connection:
            connection.execute(
                """
                INSERT INTO event_history (
                    event_timestamp,
                    event_sequence,
                    prediction_label,
                    anomaly_probability,
                    window_events
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    datetime.now(timezone.utc),
                    " ".join(window),
                    prediction,
                    result.get("anomaly_probability"),
                    Jsonb(window),
                ),
            )
    finally:
        connection.close()
