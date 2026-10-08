# Signova — Sign Language Recognition System

**Signova** is a real-time sign language recognition system that uses **computer vision and machine learning** to recognize selected hand gestures through a webcam and display their corresponding words.

## Features

* Real-time webcam-based sign recognition
* One-hand and two-hand gesture recognition
* Hand landmark detection using MediaPipe
* Machine learning-based sign classification
* React-based interactive interface
* Flask REST API
* MySQL database and recognition history
* Node.js/Express service
* Apache Kafka event streaming
* Docker-based deployment

## How It Works

```text
Webcam
   ↓
React Frontend
   ↓
Flask Backend
   ↓
MediaPipe Hand Detection
   ↓
Landmark Extraction & Normalization
   ↓
Sign Recognition Model
   ↓
Recognized Sign
   ├──→ React UI
   ├──→ MySQL
   └──→ Kafka
```

## Supported Signs

The current version recognizes a selected set of static gestures, including:

**One-hand:** `HELLO` · `YES` · `NO` · `PLEASE` · `THANK_YOU` · `ILOVEYOU`

**Two-hand:** `NAMASTE` · `HOUSE`

The recognition vocabulary can be expanded by adding new training samples and updating the models.

## Tech Stack

| Component        | Technology        |
| ---------------- | ----------------- |
| Frontend         | React, Vite       |
| Backend          | Python, Flask     |
| Computer Vision  | MediaPipe, OpenCV |
| Machine Learning | Python            |
| Database         | MySQL             |
| API Service      | Node.js, Express  |
| Event Streaming  | Apache Kafka      |
| Deployment       | Docker            |

## Project Structure

```text
SIGN_LANGUAGE/
├── backend/              # Flask API & recognition models
├── services/             # Express service
├── signova/              # React frontend
├── docker-compose.yml    # Docker/Kafka configuration
└── README.md
```

## Getting Started

### Prerequisites

* Python
* Node.js & npm
* MySQL
* Docker Desktop
* Git

### Clone

```bash
git clone <repository-url>
cd SIGN_LANGUAGE
```

### Start Kafka

```bash
docker compose up -d
```

### Start Backend

```bash
cd backend
python app.py
```

### Start Frontend

```bash
cd signova
npm install
npm run dev
```

Open the local URL provided by Vite in your browser.

## Future Development

Signova is an **ongoing project** and I plan to continue developing it with improvements such as:

* Expanding the sign vocabulary
* Improving recognition accuracy
* Supporting dynamic gestures
* Continuous sentence recognition
* Multilingual output
* Improved accessibility
* Mobile application support

## Project Status

**Prototype — Ongoing Development**

More features, improvements, and refinements will be added as the project evolves.

## Author

**Saranya Aluru**
B.Tech — Artificial Intelligence and Data Science

---

*An assistive technology project exploring real-time sign language recognition using computer vision and machine learning.*
