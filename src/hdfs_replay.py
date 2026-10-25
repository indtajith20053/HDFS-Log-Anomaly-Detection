import time
from collections import deque
from pathlib import Path

from hdfs_parser import parse_log_line
from features.parser import event_sequence_to_features
from models.predict import predict


LOG_FILE = Path(__file__).parent.parent / "data" / "raw" / "HDFS.log"

WINDOW_SIZE = 10
DELAY = 0.5


def replay_hdfs_logs():

    event_window = deque(maxlen=WINDOW_SIZE)

    print("=" * 70)
    print("HDFS REAL DATA REPLAY")
    print("=" * 70)
    print(f"Source: {LOG_FILE}")
    print(f"Window size: {WINDOW_SIZE}")
    print()

    with open(
        LOG_FILE,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        for line_number, line in enumerate(file, start=1):

            line = line.strip()

            if not line:
                continue

            event_id = parse_log_line(line)

            if not event_id:
                continue

            event_window.append(event_id)

            print(
                f"[Line {line_number:,}] "
                f"EVENT={event_id} | "
                f"Window={list(event_window)}"
            )

            if len(event_window) < WINDOW_SIZE:
                continue

            try:

                event_sequence = " ".join(event_window)

                features = event_sequence_to_features(
                    event_sequence
                )

                result = predict(features)

                prediction = int(
                    result.iloc[0]["prediction"]
                )

                probability = float(
                    result.iloc[0]["anomaly_probability"]
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

            print("-" * 70)

            time.sleep(DELAY)


if __name__ == "__main__":
    replay_hdfs_logs()