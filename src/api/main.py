from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.features.parser import event_sequence_to_features
from src.models.predict import predict
from src.api.live_detector import detector
import os
import psycopg


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="HDFS Log Anomaly Detection API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://hdfs-log-anomaly-detection-2.onrender.com",
    ],
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
        "service": "HDFS Log Anomaly Detection API"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "detector_running": detector.running
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

        prediction = int(
            result.iloc[0]["prediction"]
        )

        probability = float(
            result.iloc[0]["anomaly_probability"]
        )

        return {
            "prediction": (
                "Anomaly"
                if prediction == 1
                else "Normal"
            ),
            "anomaly_probability": probability
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )




# ============================================================
# POSTGRESQL DETECTION HISTORY
# ============================================================

@app.get("/events")
def get_events(limit: int = 50, offset: int = 0):
    """Return saved HDFS predictions, newest first."""
    if not 1 <= limit <= 500 or offset < 0:
        raise HTTPException(
            status_code=400,
            detail="limit must be 1-500 and offset must be non-negative",
        )

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(
            status_code=503,
            detail="DATABASE_URL is not configured",
        )

    try:
        with psycopg.connect(database_url, connect_timeout=5) as conn:
            rows = conn.execute(
                """
                SELECT id, event_timestamp, prediction_label,
                       anomaly_probability, event_sequence,
                       window_events, created_at
                FROM event_history
                ORDER BY id DESC
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            ).fetchall()

        return {
            "count": len(rows),
            "limit": limit,
            "offset": offset,
            "events": [
                {
                    "id": row[0],
                    "event_timestamp": (
                        row[1].isoformat() if row[1] else None
                    ),
                    "prediction": row[2],
                    "anomaly_probability": row[3],
                    "event_sequence": row[4],
                    "window": row[5],
                    "created_at": (
                        row[6].isoformat() if row[6] else None
                    ),
                }
                for row in rows
            ],
        }

    except Exception as exc:
        print("DATABASE HISTORY ERROR:", exc)
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve detection history",
        ) from exc


# ============================================================
# LIVE LATEST RESULT
# ============================================================

@app.get("/live/latest")
def live_latest():

    return detector.latest_result


# ============================================================
# START LIVE DETECTOR
# ============================================================

@app.post("/live/start")
def start_live_detector():

    detector.start()

    return {
        "status": "started",
        "detector_running": detector.running
    }


# ============================================================
# STOP LIVE DETECTOR
# ============================================================

@app.post("/live/stop")
def stop_live_detector():

    detector.stop()

    return {
        "status": "stopped",
        "detector_running": detector.running
    }


# ============================================================
# WEBSOCKET
# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            await websocket.send_json(
                detector.latest_result
            )

            import asyncio

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:

        print(
            "WebSocket client disconnected"
        )
        