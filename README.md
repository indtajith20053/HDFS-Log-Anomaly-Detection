# 🔍 HDFS Log Anomaly Detection System

### Machine Learning | Python | FastAPI | Real-Time Monitoring | Telegram Alerts

An intelligent log anomaly detection system designed to identify unusual patterns in HDFS log events using machine learning. The project combines a trained classification model, a FastAPI backend, a monitoring dashboard, and Telegram notifications into a unified monitoring workflow.

<p align="center">
  <strong>Detect. Monitor. Alert.</strong>
</p>

---

## 🎬 Project Demo

<p align="center">
  <a href="YOUR_DEMO_VIDEO_LINK">
    <img src="YOUR_DEMO_THUMBNAIL_URL" alt="HDFS Log Anomaly Detection Demo" width="800">
  </a>
</p>

<p align="center">
  <a href="YOUR_LIVE_DEMO_URL">
    <img src="https://img.shields.io/badge/Live-Demo-2563EB?style=for-the-badge" alt="Live Demo">
  </a>
  <a href="YOUR_GITHUB_REPOSITORY_URL">
    <img src="https://img.shields.io/badge/Source-Code-181717?style=for-the-badge&logo=github" alt="Source Code">
  </a>
</p>

> 🎥 Watch the demonstration to see the anomaly detection workflow, dashboard, and alerting integration.

---

## 🚀 Overview

Large-scale systems generate enormous amounts of log data. Identifying unusual event sequences manually can be time-consuming and challenging.

This project explores how machine learning can help classify HDFS log event sequences as normal or anomalous.

The system processes log-event features, generates predictions through a trained Random Forest classifier, and exposes a prediction endpoint through FastAPI. A monitoring dashboard presents the results, while Telegram integration can deliver notifications when configured.

### Key Objectives

- Automate the classification of HDFS log event sequences.
- Identify potentially anomalous patterns.
- Expose model predictions through a REST API.
- Visualize detection results through a monitoring dashboard.
- Support timely investigation through Telegram notifications.

---

## ✨ Features

- 🧠 **Machine Learning:** Random Forest classification for anomaly detection.
- 📊 **Log Analysis:** Processes structured HDFS log-event sequences.
- ⚡ **REST API:** FastAPI endpoint for submitting event sequences and obtaining predictions.
- 🖥️ **Monitoring Dashboard:** Visual interface for exploring detection results.
- 🚨 **Telegram Integration:** Supports notifications when the alert workflow is configured.
- 🔎 **Event Features:** Uses event identifiers and numerical features for model inference.
- 🛠️ **Modular Architecture:** Separates model inference, API handling, log processing, and dashboard functionality.

---

## 🏗️ System Architecture

```text
            HDFS Log Data
                  |
                  v
          Log Event Processing
                  |
                  v
           Feature Extraction
                  |
                  v
       Trained Random Forest Model
                  |
                  v
           FastAPI Prediction API
                  |
                  v
        Anomaly Detection Results
                  |
           +------+------+
           |             |
           v             v
      Monitoring     Telegram Alert
       Dashboard      Integration
```

*The Telegram alert path depends on the notification integration being enabled. The diagram represents the intended workflow.*

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core development |
| Scikit-learn | Machine learning |
| Random Forest | Classification model |
| FastAPI | REST API |
| Joblib | Model serialization and loading |
| HTML, CSS, JavaScript | Dashboard interface, if applicable |
| Telegram Bot API | Notification delivery |
| Git and GitHub | Version control and source management |

---

## 🧠 Machine Learning Approach

The system uses a trained Random Forest classifier to distinguish between normal and anomalous HDFS log event sequences.

### Workflow

1. Process HDFS log data.
2. Extract event identifiers and numerical features.
3. Construct feature representations for event sequences.
4. Load the trained classification model.
5. Generate predictions for incoming sequences.
6. Return prediction results through the API.
7. Present results in the dashboard and trigger notifications when configured.

### Model Information

- **Algorithm:** Random Forest Classifier
- **Input:** Structured event-sequence features
- **Output:** Normal or anomalous classification
- **Inference:** Python model served through FastAPI

The model's effectiveness should be evaluated using appropriate test data and metrics, including precision, recall, F1-score, and a confusion matrix.

---

## 🔌 API Usage

The FastAPI backend provides an endpoint for submitting event sequences for prediction.

### Example Request

```http
POST /predict
Content-Type: application/json
```

Request body:

```json
{
  "event_sequence": ["E1", "E2", "E3", "E26"]
}
```

The example illustrates the expected request structure. Use event identifiers and sequences supported by the actual model and feature-processing pipeline.

### Example Response

The exact response depends on the API implementation.

```json
{
  "prediction": "anomaly",
  "anomaly_score": 0.93
}
```

*Illustrative example only. Response field names, prediction labels, and score semantics must match the actual API implementation.*

---

## 🚨 Telegram Notifications

The project can integrate Telegram alerts to notify an operator when an anomaly is detected.

Example notification:

```text
🚨 HDFS ANOMALY ALERT

An unusual event sequence was detected.

Status: Anomaly Detected
Action: Investigate the corresponding log events.
```

The notification workflow can be extended to include timestamps, event identifiers, and model scores.

**Security:** Store the Telegram bot token in an environment variable. Never commit tokens, private chat IDs, API keys, or other sensitive credentials to GitHub.

---

## 💻 Local Installation

### Prerequisites

- Python 3.12
- Git
- pip

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd HDFS-Log-Anomaly-Detection
```

### 2. Create a Virtual Environment

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

If the repository contains a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file if the application uses environment variables.

Example:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Use only the variables required by the actual implementation.

Add `.env` to `.gitignore` before committing your code.

### 5. Start the API

If `src/api/main.py` exposes a FastAPI application named `app`, run:

```bash
uvicorn src.api.main:app --reload --port 8001
```

Adjust the command if your project uses a different module path or port.

### 6. Open the API Documentation

Once the API is running, visit:

```text
http://127.0.0.1:8001/docs
```

The interactive documentation allows you to inspect available endpoints and test supported requests.

### 7. Start the Dashboard

Follow the dashboard-specific instructions in the repository. The dashboard may need to be started separately from the API.

---

## 📁 Project Structure

```text
HDFS-Log-Anomaly-Detection/
│
├── models/
│   └── anomaly_model.joblib
│
├── src/
│   └── api/
│       └── main.py
│
├── scripts/
│   ├── parser
│   ├── stream_processor
│   └── replay
│
├── templates/
├── requirements.txt
├── .gitignore
└── README.md
```

*This is an illustrative structure. Update it to match the files and directories actually present in your repository.*

---

## 🔮 Future Improvements

- Streaming log ingestion and continuous inference.
- WebSocket-based live dashboard updates.
- Configurable anomaly alert thresholds.
- Improved model evaluation and error analysis.
- Monitoring for API availability and failures.
- Containerized deployment.
- Better observability, logging, and model versioning.

---

## 🔐 Security Considerations

- Keep API tokens and credentials out of source control.
- Validate API inputs.
- Protect public endpoints against abuse.
- Avoid exposing sensitive log data.
- Apply appropriate authentication and access controls before production deployment.

---

## 👨‍💻 Author

**Jason**

AI/ML Engineer | Python Developer | Machine Learning Projects

---

## ⭐ Support

If you find this project interesting, consider starring the repository or sharing constructive feedback.

Contributions, suggestions, and discussions about machine learning, anomaly detection, and system monitoring are welcome.

---

<p align="center">
  <strong>Built with Python and Machine Learning.</strong>
</p>
