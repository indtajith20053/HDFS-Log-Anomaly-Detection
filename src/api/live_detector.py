
import threading
import time
from collections import deque
from pathlib import Path

from src.hdfs_parser import parse_log_line
from src.features.parser import event_sequence_to_features
from src.models.predict import predict
from src.api.database import save_detection
from src.api.telegram_alerts import send_telegram_alert


LOG_FILE = Path(__file__).resolve().parents[2] / "data" / "raw" / "HDFS.log"

WINDOW_SIZE = 10
REPLAY_INTERVAL = 0.5


class LiveDetector:
    def __init__(self):
        self.event_window = deque(maxlen=WINDOW_SIZE)
        self.latest_result = {
            "status": "waiting",
            "event": None,
            "prediction": None,
            "anomaly_probability": None,
            "window": [],
            "timestamp": None,
        }
        self.running = False
        self.thread = None

    def process_line(self, line):
        event_id = parse_log_line(line)

        if not event_id:
            return None

        self.event_window.append(event_id)

        result = {
            "status": "collecting",
            "event": event_id,
            "prediction": None,
            "anomaly_probability": None,
            "window": list(self.event_window),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        if len(self.event_window) >= WINDOW_SIZE:
            event_sequence = " ".join(self.event_window)
            features = event_sequence_to_features(event_sequence)
            prediction_result = predict(features)

            prediction = int(prediction_result.iloc[0]["prediction"])
            probability = float(
                prediction_result.iloc[0]["anomaly_probability"]
            )

            result["status"] = "detected"
            result["prediction"] = (
                "Anomaly" if prediction == 1 else "Normal"
            )
            result["anomaly_probability"] = probability

        self.latest_result = result

        if result["status"] == "detected":
            try:
                save_detection(result)
            except Exception as exc:
                print("DATABASE SAVE ERROR:", type(exc).__name__)

            if result["prediction"] == "Anomaly":
                try:
                    send_telegram_alert(result)
                except Exception as exc:
                    print("TELEGRAM ALERT ERROR:", type(exc).__name__)

        return result

    def replay_log(self):
        print("=" * 70)
        print("HDFS LIVE LOG STREAM")
        print("=" * 70)
        print(f"Reading: {LOG_FILE}")
        print("Mode: Historical log replay")
        print()

        try:
            with open(
                LOG_FILE, "r", encoding="utf-8", errors="replace"
            ) as file:
                for line in file:
                    if not self.running:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    result = self.process_line(line)

                    if result:
                        print(
                            f"[{result['timestamp']}] "
                            f"Event={result['event']} "
                            f"Prediction={result['prediction']} "
                            f"Probability={result['anomaly_probability']}"
                        )

                    time.sleep(REPLAY_INTERVAL)

        except Exception as exc:
            print("LIVE DETECTOR ERROR:", type(exc).__name__)

        finally:
            self.running = False
            print()
            print("HDFS log replay finished.")

    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(
            target=self.replay_log,
            daemon=True,
        )
        self.thread.start()

    def stop(self):
        self.running = False


detector = LiveDetector()
