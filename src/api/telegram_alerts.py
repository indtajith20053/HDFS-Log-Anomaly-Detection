
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

ALERT_COOLDOWN_SECONDS = 60
_last_alert_time = 0.0


def send_telegram_alert(result: dict) -> bool:
    """Send a Telegram message when an anomaly is detected."""

    global _last_alert_time

    if result.get("prediction") != "Anomaly":
        return False

    now = time.monotonic()

    if now - _last_alert_time < ALERT_COOLDOWN_SECONDS:
        print("TELEGRAM ALERT: Skipped (cooldown active).")
        return False

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("TELEGRAM ALERT ERROR: Settings are missing.")
        return False

    probability = result.get("anomaly_probability")
    event = result.get("event", "Unknown")
    window = result.get("window", [])

    probability_text = (
        f"{probability:.1%}"
        if isinstance(probability, (int, float))
        else "Unavailable"
    )

    message = (
        "🚨 HDFS ANOMALY DETECTED\n\n"
        f"Event: {event}\n"
        f"Anomaly probability: {probability_text}\n"
        f"Window size: {len(window)}\n"
        f"Event sequence: {' '.join(window)}\n\n"
        "Check your HDFS monitoring dashboard."
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("ok"):
            _last_alert_time = time.monotonic()
            print("TELEGRAM ALERT: Sent successfully.")
            return True

        print("TELEGRAM ALERT ERROR: Telegram rejected the message.")
        return False

    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        print(f"TELEGRAM ALERT ERROR: {type(exc).__name__}")
        return False
