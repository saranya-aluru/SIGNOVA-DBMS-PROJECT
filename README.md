

````markdown
# Signova — Sign Language Recognition System

Signova is a real-time sign language recognition system that uses computer vision and machine learning to recognize selected hand gestures through a webcam and convert them into readable words.

The project combines **React, Python, Flask, MediaPipe, MySQL, Node.js, Apache Kafka, and Docker** into a modular system for real-time gesture recognition, data management, and event processing.

---

## Overview

Sign language is an important form of communication for millions of people around the world. However, communication can become difficult when the people involved do not understand the same sign language.

Signova explores how computer vision and machine learning can be used to recognize hand gestures and provide an accessible digital interpretation of commonly used signs.

The system captures a user's hand gestures through a webcam, detects hand landmarks, extracts features from those landmarks, classifies the gesture, and displays the corresponding word.

Recognized signs can also be stored in a MySQL database as part of the user's recognition history.

---

## How It Works

```text
Webcam
   │
   ▼
React Frontend
   │
   ▼
Flask Backend
   │
   ▼
MediaPipe Hand Detection
   │
   ▼
Landmark Extraction
   │
   ▼
Feature Normalization
   │
   ▼
Sign Recognition Model
   │
   ├──────────────► MySQL
   │                Sign Information
   │                Recognition History
   │
   └──────────────► Event Processing
                    Apache Kafka
````

---

## Features

* Real-time webcam-based sign recognition
* One-hand and two-hand gesture recognition
* 21-point hand landmark detection using MediaPipe
* Custom machine-learning-based classification
* React-based interactive interface
* Flask REST API
* MySQL database integration
* Recognition history
* Supported-sign information
* Node.js and Express service
* Apache Kafka event streaming
* Docker-based Kafka deployment

---

## Supported Signs

Signova currently focuses on a selected vocabulary rather than attempting to recognize the complete sign language vocabulary.

### One-Hand Signs

| Sign        | Meaning    |
| ----------- | ---------- |
| `HELLO`     | Hello      |
| `YES`       | Yes        |
| `NO`        | No         |
| `PLEASE`    | Please     |
| `THANK_YOU` | Thank You  |
| `ILOVEYOU`  | I Love You |

### Two-Hand Signs

| Sign      | Meaning |
| --------- | ------- |
| `NAMASTE` | Namaste |
| `HOUSE`   | House   |

The system is designed so that additional signs can be added by collecting training samples and updating the recognition models.

---

# Recognition Pipeline

## 1. Webcam Capture

The React frontend accesses the user's webcam and captures frames containing the hand gesture.

## 2. Hand Landmark Detection

MediaPipe detects the hand and identifies its 21 landmarks.

Each landmark contains:

```text
X coordinate
Y coordinate
Z coordinate
```

For one hand:

```text
21 landmarks × 3 coordinates = 63 features
```

For two hands:

```text
63 + 63 = 126 features
```

## 3. Feature Normalization

The detected landmarks are normalized relative to the wrist.

This helps reduce the effect of:

* Hand position
* Distance from the camera
* Different hand sizes

The normalized landmarks are converted into a numerical feature vector.

## 4. Sign Classification

The feature vector is compared with the trained sign samples using a lightweight nearest-neighbor recognition approach.

The closest matching samples are used to determine the predicted sign.

## 5. Result

The predicted sign is returned through the backend and displayed in the React interface.

The corresponding sign information can also be retrieved from MySQL.

---

# One-Hand Recognition

A single detected hand produces 63 features:

```text
21 landmarks × 3 coordinates
                ↓
           63 features
                ↓
        One-Hand Model
                ↓
        Predicted Sign
```

---

# Two-Hand Recognition

When two hands are detected, their landmarks are combined into a 126-feature representation.

```text
Left Hand   → 63 features
Right Hand  → 63 features
                    ↓
             126 features
                    ↓
           Two-Hand Model
                    ↓
             Predicted Sign
```

The backend automatically selects the appropriate model based on the number of detected hands.

---

# Technology Stack

| Layer                | Technology          |
| -------------------- | ------------------- |
| Frontend             | React               |
| Frontend Tooling     | Vite                |
| Backend              | Python Flask        |
| Computer Vision      | MediaPipe           |
| Image Processing     | OpenCV              |
| Numerical Processing | NumPy               |
| Recognition          | Custom Python Model |
| Database             | MySQL               |
| REST Service         | Node.js + Express   |
| Event Streaming      | Apache Kafka        |
| Containerization     | Docker              |

---

# Project Architecture

```text
                    ┌──────────────────┐
                    │      Webcam      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   React / Vite   │
                    │    Frontend      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Flask Backend  │
                    │    REST API      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     MediaPipe    │
                    │  Hand Landmarks  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Feature Extraction│
                    │  & Normalization │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Sign Recognition │
                    │      Model       │
                    └───────┬───┬──────┘
                            │   │
                ┌───────────┘   └────────────┐
                ▼                            ▼
       ┌──────────────────┐        ┌──────────────────┐
       │      MySQL       │        │  Apache Kafka    │
       │ Sign Information │        │ Event Streaming  │
       │ & History        │        │                  │
       └──────────────────┘        └──────────────────┘
```

---

# Database

Signova uses MySQL to manage structured sign information and recognition history.

### Database

```text
sign_language_db
```

### `signs`

Stores information about the supported signs.

Main fields include:

```text
sign_id
sign_name
display_word
description
sign_type
image_url
video_url
created_at
```

### `recognition_history`

Stores previously recognized signs along with their timestamps.

The relationship between the tables is based on `sign_id`.

```text
signs
  │
  │ sign_id
  ▼
recognition_history
```

This allows recognition results to be associated with the corresponding sign information.

---

# REST API

The Flask backend runs on:

```text
http://127.0.0.1:5000
```

### Available Endpoints

#### Health Check

```http
GET /
```

Checks whether the Flask backend is running.

#### Sign Recognition

```http
POST /recognize
```

Processes an image, detects hands, extracts features, predicts the sign, and returns the recognition result.

#### Supported Signs

```http
GET /signs
```

Returns the signs stored in the database.

---

# Node.js and Express

Signova also contains a Node.js and Express service that provides additional REST-based backend functionality.

The Express service runs on:

```text
http://127.0.0.1:3001
```

Available service endpoints include:

```text
GET /api/health
GET /api/architecture
GET /api/signs-summary
```

The service provides a separate API layer that can be extended for additional application and event-processing functionality.

---

# Apache Kafka

Apache Kafka is included to demonstrate event-driven communication.

The project uses the following Kafka topic:

```text
sign-recognition
```

Recognition events can be represented as structured messages such as:

```json
{
  "sign": "HELLO",
  "word": "Hello",
  "hand_count": 1
}
```

Kafka allows recognition events to be handled as a stream of messages rather than relying only on direct request-response communication.

---

# Docker

Kafka is deployed using Docker and Docker Compose.

This avoids requiring a separate manual Kafka installation and makes the development environment easier to reproduce.

Start the services with:

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

The Kafka container is named:

```text
signova-kafka
```

Kafka is exposed on:

```text
localhost:9092
```

---

# Project Structure

```text
SIGN_LANGUAGE/
│
├── backend/
│   ├── app.py
│   ├── database_helper.py
│   ├── hand_landmarker.task
│   ├── sign_model.pkl
│   └── sign_model_two_hand.pkl
│
├── services/
│   └── express-service/
│       └── server.js
│
├── signova/
│   ├── src/
│   │   ├── App.jsx
│   │   └── ...
│   ├── package.json
│   └── ...
│
├── docker-compose.yml
│
└── README.md
```

---

# Getting Started

## Prerequisites

Make sure the following are installed:

* Python 3.13+
* Node.js
* npm
* MySQL
* Docker Desktop
* Git

---

## 1. Clone the Repository

```bash
git clone <YOUR-REPOSITORY-URL>
cd SIGN_LANGUAGE
```

---

## 2. Start Docker

Open Docker Desktop and make sure it is running.

Verify Docker:

```bash
docker --version
```

Start Kafka:

```bash
docker compose up -d
```

Verify:

```bash
docker ps
```

---

## 3. Start the Flask Backend

Open a terminal:

```powershell
cd backend
```

Activate the Python environment:

```powershell
..\ .venv313\Scripts\Activate.ps1
```

> Remove the space between `..\` and `.venv313` if copying manually.

Or from the project root:

```powershell
.\.venv313\Scripts\Activate.ps1
```

Then:

```powershell
cd backend
python app.py
```

The Flask backend should now be available at:

```text
http://127.0.0.1:5000
```

---

## 4. Start the React Frontend

Open another terminal:

```powershell
cd signova
```

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

Vite will display the local URL in the terminal.

Usually:

```text
http://localhost:5173
```

---

## 5. Start the Express Service

Open another terminal:

```powershell
cd services\express-service
```

Start the service:

```powershell
node server.js
```

The Express service should run at:

```text
http://127.0.0.1:3001
```

---

# Testing Kafka

List Kafka topics:

```powershell
docker exec signova-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

Start a Kafka consumer:

```powershell
docker exec -it signova-kafka /opt/kafka/bin/kafka-console-consumer.sh --topic sign-recognition --bootstrap-server localhost:9092 --from-beginning
```

In another terminal, start a producer:

```powershell
docker exec -it signova-kafka /opt/kafka/bin/kafka-console-producer.sh --topic sign-recognition --bootstrap-server localhost:9092
```

You can then send test messages such as:

```text
HELLO
YES
THANK_YOU
```

---

# User Interface

The React application is organized into several sections:

### Recognition

The main page provides:

* Live camera feed
* Detected sign
* Current sentence
* Recent recognition results
* Supported signs

### Signs

Displays information about the signs supported by the system.

### History

Displays previously recognized signs stored by the application.

### About

Provides an overview of the technology and recognition pipeline used by Signova.

---

# Limitations

Signova is currently a prototype focused on a limited set of signs.

The main limitations are:

* Limited vocabulary
* Recognition can be affected by lighting and camera quality
* Similar gestures can be difficult to distinguish
* Dynamic signs involving movement are not fully modeled
* The current system is not intended to provide unrestricted continuous sign-language translation

The project focuses on demonstrating the complete recognition pipeline rather than covering the entire sign language vocabulary.

---

# Future Improvements

Several improvements can be made in future versions:

* Expand the supported vocabulary
* Collect larger and more diverse training datasets
* Improve recognition accuracy
* Add dynamic gesture recognition
* Introduce temporal models for movement-based signs
* Improve continuous sentence recognition
* Add natural language processing
* Develop a mobile application
* Deploy the system as a cloud-based service
* Add multilingual output
* Improve accessibility features

---

# Social Impact

Signova is designed as an exploration of assistive technology for communication.

Potential applications include:

* Education
* Public services
* Healthcare environments
* Customer service
* Accessibility tools
* Assistive communication systems

The current implementation is a prototype and is not intended to replace professional sign-language interpreters.

---

# Project Status

**Prototype — Actively Developed**

Current implementation includes:

* Real-time hand detection
* One-hand sign recognition
* Two-hand sign recognition
* React frontend
* Flask backend
* MySQL database
* Recognition history
* REST APIs
* Node.js and Express service
* Apache Kafka
* Docker deployment

---

# Contributing

Contributions and improvements are welcome.

A typical contribution workflow is:

```bash
git checkout -b feature/new-feature
```

Make your changes, test them, and create a pull request.

Ideas for contributions include:

* Adding new signs
* Improving the recognition model
* Improving UI accessibility
* Adding new API functionality
* Improving documentation
* Adding automated tests

---

# Privacy

Signova processes webcam frames for the purpose of hand-sign recognition.

When deploying or modifying the system, developers should clearly communicate how camera data and recognition history are handled.

Do not commit passwords, API keys, database credentials, or other sensitive information to the repository.

---

# License

This project is intended for educational and research purposes.

If third-party datasets, models, libraries, or other resources are used, their respective licenses and attribution requirements should be followed.

---

# Acknowledgements

Signova is built using open-source technologies including:

* MediaPipe
* OpenCV
* NumPy
* Flask
* React
* MySQL
* Node.js
* Express
* Apache Kafka
* Docker

---

## Author

**Saranya Aluru**

**Signova — Sign Language Recognition System**

````

**One correction before you paste:** in the Python setup section, use this exact command—there should be **no space**:

```powershell
.\.venv313\Scripts\Activate.ps1
````


