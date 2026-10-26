
import asyncio
import os
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.api.live_detector import detector
from src.features.parser import event_sequence_to_features
from src.models.predict import predict


# ============================================================
# CONFIGURATION
# ============================================================

FRONTEND_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://hdfs-log-anomaly-detection-2.onrender.com",
]


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="HDFS Log Anomaly Detection API",
    version="1.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class PredictionRequest(BaseModel):
    event_sequence: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "HDFS Log Anomaly Detection API",
        "version": app.version,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "detector_running": detector.running,
        "database_configured": bool(
            os.getenv("DATABASE_URL", "").strip()
        ),
    }


# ============================================================
# ML PREDICTION
# ============================================================

@app.post("/predict")
def make_prediction(request: PredictionRequest):
    try:
        features = event_sequence_to_features(
            request.event_sequence
        )

        result = predict(features)

        prediction = int(result.iloc[0]["prediction"])
        probability = float(
            result.iloc[0]["anomaly_probability"]
        )

        return {
            "prediction": (
                "Anomaly" if prediction == 1 else "Normal"
            ),
            "anomaly_probability": probability,
        }

    except Exception as exc:
        print("PREDICTION ERROR:", repr(exc))
        raise HTTPException(
            status_code=400,
            detail="Prediction failed. Check the backend logs.",
        ) from exc


# ============================================================
# POSTGRESQL DETECTION HISTORY
# ============================================================

@app.get("/events")
def get_events(limit: int = 50, offset: int = 0):
    """Return saved predictions, newest first."""

    if not 1 <= limit <= 500 or offset < 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "limit must be between 1 and 500, "
                "and offset must be non-negative"
            ),
        )

    database_url = os.getenv("DATABASE_URL", "").strip()

    if not database_url:
        raise HTTPException(
            status_code=503,
            detail="DATABASE_URL is not configured on the backend",
        )

    try:
        with psycopg.connect(
            database_url,
            connect_timeout=10,
        ) as conn:
            rows = conn.execute(
                """
                SELECT
                    id,
                    event_timestamp,
                    prediction_label,
                    anomaly_probability,
                    event_sequence,
                    window_events,
                    created_at
                FROM event_history
                ORDER BY id DESC
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            ).fetchall()

        events = []

        for row in rows:
            events.append(
                {
                    "id": row[0],
                    "event_timestamp": (
                        row[1].isoformat()
                        if row[1] else None
                    ),
                    "prediction": row[2],
                    "anomaly_probability": (
                        float(row[3])
                        if row[3] is not None else None
                    ),
                    "event_sequence": row[4],
                    "window": row[5],
                    "created_at": (
                        row[6].isoformat()
                        if row[6] else None
                    ),
                }
            )

        return {
            "count": len(events),
            "limit": limit,
            "offset": offset,
            "events": events,
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(
            "DATABASE HISTORY ERROR:",
            type(exc).__name__,
            str(exc),
            flush=True,
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Could not retrieve detection history. "
                "Check backend logs and database configuration."
            ),
        ) from exc


# ============================================================
# STOP DETECTOR
# ============================================================

@app.post("/live/stop")
def stop_live_detector():
    try:
        detector.stop()

        return {
            "status": "stopped",
            "detector_running": detector.running,
        }

    except Exception as exc:
        print("DETECTOR STOP ERROR:", repr(exc))

        raise HTTPException(
            status_code=500,
            detail="Could not stop the detector. Check backend logs.",
        ) from exc


# ============================================================
# WEBSOCKET LIVE STREAM
# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    print("WebSocket client connected")

    try:
        while True:
            # Send the latest available detector result.
            await websocket.send_json(detector.latest_result)

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        print("WebSocket client disconnected")

    except Exception as exc:
        print("WEBSOCKET ERROR:", type(exc).__name__, str(exc))

        try:
            await websocket.close(code=1011)
        except Exception:
            pass
