import time
from collections import deque
from pathlib import Path

from hdfs_parser import parse_log_line
from features.parser import event_sequence_to_features
from models.predict import predict

LOG_FILE = Path(__file__).parent.parent / "data" / "raw" / "HDFS.log"

POLL_INTERVAL = 0.5
WINDOW_SIZE = 10


def analyze_event_window(event_window):
    """
    Run the existing trained ML model on the latest events.
    """

    event_sequence = " ".join(event_window)

    features = event_sequence_to_features(event_sequence)

    result = predict(features)

    prediction = int(result.iloc[0]["prediction"])
    probability = float(
        result.iloc[0]["anomaly_probability"]
    )

    return prediction, probability


def follow_log_file():

    event_window = deque(maxlen=WINDOW_SIZE)

    print("=" * 70)
    print("HDFS REAL-TIME ANOMALY DETECTION")
    print("=" * 70)
    print(f"Monitoring: {LOG_FILE}")
    print(f"Window size: {WINDOW_SIZE} events")
    print("Waiting for new log entries...")
    print()

    with open(
        LOG_FILE,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        # Start at the end.
        # Only newly appended logs will be processed.
        file.seek(0, 2)

        while True:

            line = file.readline()

            if not line:
                time.sleep(POLL_INTERVAL)
                continue

            line = line.strip()

            if not line:
                continue

            event_id = parse_log_line(line)

            timestamp = time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            if not event_id:

                print(
                    f"[{timestamp}] "
                    f"EVENT=UNKNOWN | "
                    f"{line}"
                )

                continue

            # Add recognized event to rolling window.
            event_window.append(event_id)

            print(
                f"[{timestamp}] "
                f"EVENT={event_id} | "
                f"Window={list(event_window)}"
            )

            # Wait until we have enough events.
            if len(event_window) < WINDOW_SIZE:

                print(
                    f"   Waiting for model window: "
                    f"{len(event_window)}/{WINDOW_SIZE}"
                )

                continue

            try:

                prediction, probability = analyze_event_window(
                    event_window
                )

                if prediction == 1:

                    print(
                        f"   🔴 ANOMALY | "
                        f"Probability={probability:.2f}"
                    )

                else:

                    print(
                        f"   🟢 NORMAL | "
                        f"Anomaly probability={probability:.2f}"
                    )

            except Exception as e:

                print(
                    f"   ❌ Prediction error: {e}"
                )


if __name__ == "__main__":
    follow_log_file()