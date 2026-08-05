<div align="center">

# SignBridge AI — Real-Time Sign Language Communication Platform

Full-stack accessibility platform featuring **live sign-to-text translation**, **text-to-sign animation**, **speech-to-sign**, **sign-to-speech**, and **two-person conversation mode** — all running on a self-hosted ML pipeline.

Built with **Python + FastAPI** and **React 18 + TypeScript**, focused on real-time temporal gesture recognition, accessible UI design, and end-to-end assistive communication workflows.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![PyTorch](https://img.shields.io/badge/ML-PyTorch%20%7C%20BiLSTM-EE4C2C?logo=pytorch)
![MediaPipe](https://img.shields.io/badge/CV-MediaPipe%20Holistic-orange)
![License](https://img.shields.io/badge/License-Unspecified-lightgrey)

</div>

---

## Features

* **Live Sign → Text** — Continuous webcam-based gesture recognition; answers grounded in a real 45-frame temporal window, not per-frame guessing
* **Smart Sentence Building** — Punctuation, capitalization, and repeated-word suppression applied automatically to recognized glosses
* **Text → Sign** — Type a phrase, watch it signed by an animated 3D skeletal hand via Three.js
* **Speech → Sign** — Browser speech recognition feeds directly into the same sign animation pipeline
* **Sign → Speech** — Recognized sentences are read aloud via text-to-speech
* **Conversation Mode** — Split-screen: one person signs, the other speaks, both sides translated live into a shared transcript
* **Confidence Gating** — Predictions below threshold are suppressed rather than shown, and idle/no-hand frames never trigger false positives
* **Accessibility Built-In** — Dark mode, high contrast, large text, keyboard shortcuts
* **Input Validation** — Handles malformed frames, empty audio uploads, missing TTS engine, and WebSocket protocol errors cleanly
* **Responsive Dashboard UI** — Clean, minimal, neutral-toned interface with live status indicators
* **Self-Hosted AI** — No external API keys or paid inference required; MediaPipe, PyTorch, Whisper, and espeak-ng all run locally

---

## Core Modules

### Screenshots

### Live Sign → Text

Features:

* Server-side MediaPipe Holistic landmark extraction (pose + both hands + face)
* Rolling 45-frame temporal buffer per connection, not single-frame classification
* Idle-gating — requires ≥30% of buffered frames to have a visible hand before predicting
* Bidirectional LSTM recognition model with confidence-gated output
* Live buffer progress and confidence meter streamed to the UI

---

### Smart Sentence Builder

Turns a raw stream of recognized glosses into clean, readable output:

* **Repeat suppression** — consecutive identical glosses collapse into one word
* **Capitalization** — first letter of the sentence capitalized automatically
* **Punctuation** — sentence-ending punctuation inferred from context words
* **Flush on demand** — `end_sentence` message returns the finished sentence and resets the buffer

---

### Text → Sign / Speech → Sign

Detects and animates:

* Word-by-word playback through a local gesture keyframe library
* Real-time pose interpolation rendered as a skeletal hand (joints + bones) in Three.js
* Same animation pipeline shared by both the Text-to-Sign page and Conversation Mode
* Graceful fallback to a generic gesture for out-of-vocabulary words

---

### Sign → Speech

Provides:

* Backend `POST /api/v1/speech/text-to-speech` synthesis via espeak-ng
* Valid WAV audio returned directly over HTTP
* Clear `503` error if the TTS engine isn't installed, instead of a silent failure

---

### Conversation Mode

* Left pane: live webcam feed + sign recognition (Person A)
* Right pane: live speech transcription + sign playback (Person B)
* Shared, live-updating chat transcript combining both directions

---

## Full Processing Pipeline

```text
Webcam Frame (frontend, ~150ms interval)
      ↓
Base64 JPEG over WebSocket (/ws/translate)
      ↓
MediaPipe Holistic Landmark Extraction (1629-dim vector)
      ↓
Rolling 45-Frame Sequence Buffer + Idle-Gating
      ↓
Bidirectional LSTM Inference (SignLSTM)
      ↓
Confidence Threshold Gate
      ↓
Sentence Builder (dedup, punctuation, capitalization)
      ↓
Live prediction streamed back to frontend — sentence rendered in real time
```


---

## Tech Stack

| Layer          | Technology                        |
|----------------|------------------------------------|
| Backend        | Python 3.11+                       |
| Framework      | FastAPI + WebSockets                |
| Computer Vision| MediaPipe Holistic                  |
| ML Model       | PyTorch — Bidirectional LSTM        |
| Speech-to-Text | OpenAI Whisper                      |
| Text-to-Speech | espeak-ng                           |
| Frontend       | React 18 + TypeScript               |
| 3D Rendering   | Three.js                            |
| Styling        | Tailwind CSS                        |
| Build Tool     | Vite                                |
| Architecture   | Modular temporal-recognition pipeline |

---

## Project Structure

```bash
signbridge-ai/
├── docker-compose.yml                ← One-command launcher (both services)
├── README.md
├── .gitignore
│
├── backend/
│   ├── requirements.txt              ← Python dependencies
│   ├── .env.example                  ← Config template
│   ├── Dockerfile
│   └── app/
│       ├── main.py                   ← FastAPI entrypoint, router wiring
│       ├── api/
│       │   ├── routes_translate.py   ← /status, text-to-sign (stub)
│       │   ├── routes_ws.py          ← /ws/translate — full live pipeline
│       │   └── routes_speech.py      ← speech-to-text, text-to-speech
│       ├── core/
│       │   ├── config.py             ← env-based settings
│       │   └── logger.py
│       ├── ml/
│       │   ├── landmark_extractor.py ← MediaPipe Holistic wrapper
│       │   ├── sequence_buffer.py    ← rolling window + idle-gating
│       │   ├── model_loader.py       ← SignLSTM definition + checkpoint loading
│       │   ├── sign_recognizer.py    ← inference + confidence gating
│       │   └── sentence_builder.py   ← punctuation / dedup / capitalization
│       └── speech/
│           ├── stt.py                ← Whisper wrapper
│           └── tts.py                ← espeak-ng wrapper
│
├── frontend/
│   ├── package.json                  ← React 18 + TS deps
│   ├── Dockerfile
│   └── src/
│       ├── App.tsx                   ← Routing, root layout
│       ├── main.tsx                  ← ReactDOM entry point
│       ├── components/
│       │   ├── webcam/WebcamFeed.tsx
│       │   ├── avatar/SignAvatar3D.tsx   ← Three.js skeletal hand
│       │   ├── translation/ConfidenceMeter.tsx
│       │   ├── layout/Navbar.tsx, ThemeToggle.tsx
│       │   └── ui/StatusPill.tsx
│       ├── hooks/
│       │   ├── useWebcam.ts
│       │   ├── useWebSocket.ts
│       │   └── useSpeechRecognition.ts
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── LiveTranslate.tsx
│       │   ├── TextToSign.tsx
│       │   ├── Conversation.tsx
│       │   └── Settings.tsx
│       ├── data/gestureLibrary.ts    ← demo pose keyframes
│       ├── services/api.ts, env.ts
│       └── types/translation.ts
│
├── models/sign_recognition/          ← train.py, model_def.py, checkpoints/
├── datasets/loaders/                 ← base_loader, wlasl_loader, synthetic_loader
├── animations/gesture_library/       ← gesture data notes (real data not yet included)
└── docs/                             ← architecture, API reference, setup guides, roadmap
```

---

## API Endpoints

| Method      | Endpoint                          | Description                              |
|-------------|------------------------------------|-------------------------------------------|
| `GET`       | `/api/v1/status`                   | Health/liveness check                     |
| `POST`      | `/api/v1/translate/text-to-sign`   | Server-side text-to-sign (not yet implemented, returns `501`) |
| `WS`        | `/ws/translate`                    | Live webcam frame streaming + recognition |
| `POST`      | `/api/v1/speech/text-to-speech`    | Synthesize speech from text               |
| `POST`      | `/api/v1/speech/speech-to-text`    | Transcribe uploaded audio                 |

Swagger UI auto-generated at `http://localhost:8000/docs`

---

## Getting Started

### Prerequisites

* Python 3.11+
* Node.js 20+
* `ffmpeg` (required by Whisper)
* `espeak-ng` (required by text-to-speech)
* A webcam and microphone, for the live features

### Installation

```bash
# 1. Unzip / clone the project
cd signbridge-ai

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# 3. Frontend setup
cd ../frontend
npm install
cp .env.example .env
```

---

## Run Application

### Option A — Docker (one command)

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

### Option B — Two terminals

```bash
# Terminal 1 — Backend
cd backend
uvicorn app.main:app --reload --port 8000
# → API at http://localhost:8000
# → Swagger at http://localhost:8000/docs

# Terminal 2 — Frontend
cd frontend
npm run dev
# → App at http://localhost:5173
```

---

## Self-Hosted AI — No External API Required

| Property           | Value                                  |
|--------------------|------------------------------------------|
| Recognition model  | Bidirectional LSTM (PyTorch, self-trained) |
| Landmark extraction| MediaPipe Holistic (local, offline)       |
| Speech-to-text     | OpenAI Whisper (local, downloads weights once) |
| Text-to-speech     | espeak-ng (fully offline)                 |
| API keys required  | None                                      |
| Cost               | Free — all inference runs on your own machine |

Swapping to a hosted STT/TTS provider (e.g. a cloud Whisper API or a
premium TTS voice) is a contained change inside `app/speech/` — the rest
of the pipeline doesn't need to know the difference.

---

## Technical Highlights

### Temporal Recognition Pipeline

Buffers 45 consecutive frames of MediaPipe landmarks per connection and
gates prediction on whether the window actually contains signing motion
(idle-frame ratio check) before running inference — avoiding the
flickering, frame-by-frame misclassification that a naive per-frame
classifier produces.

### Shared Animation Engine

Text-to-Sign and Speech-to-Sign both drive the exact same
`SignAvatar3D` component and gesture-interpolation logic — one animation
pipeline, two input sources.

### Zero External Vector DB / Inference API

Everything — landmark extraction, sign recognition, speech-to-text, and
text-to-speech — runs as a local process. No hosted inference API, no
per-request cost, no API key management.

### Validation Layer

Prevents malformed WebSocket frames, empty audio uploads, missing TTS
binaries, and unknown message types from crashing the connection — every
failure path returns a structured error message instead of dropping the
socket silently.

---

## Concepts Demonstrated

* Real-time temporal sequence modeling (Bidirectional LSTM)
* Computer vision landmark extraction (MediaPipe Holistic)
* WebSocket-based streaming inference architecture
* Per-connection stateful buffering vs. shared stateless inference
* 3D skeletal animation and pose interpolation (Three.js)
* Browser-native speech recognition integration (Web Speech API)
* Async FastAPI backend engineering
* Modular React + TypeScript component architecture
* Custom React hook design patterns
* REST + WebSocket API design with Pydantic validation
* Full-stack accessibility-focused application development

---

## Future Improvements

* Train the recognition model on a real dataset (WLASL) — currently ships untrained
* Real motion-capture gesture library — currently a small hand-authored placeholder vocabulary
* Server-authored `/translate/text-to-sign` endpoint (currently client-side only)
* Validation split + real accuracy metrics for the trained model
* Transformer-based recognition architecture
* Multi-language support beyond English
* Conversation history persistence across sessions
* CI test suite

Full roadmap: [`docs/FUTURE_IMPROVEMENTS.md`](docs/FUTURE_IMPROVEMENTS.md)

---

## Status Disclaimer

The backend runs on an **untrained** recognition model by default — the
full pipeline works end-to-end, but predictions are not meaningful until
`models/sign_recognition/train.py` is run against a real dataset. The
gesture animation vocabulary is a small, hand-authored placeholder, not
linguistically accurate ASL. See
[`docs/MODEL_TRAINING.md`](docs/MODEL_TRAINING.md) and
[`animations/gesture_library/README.md`](animations/gesture_library/README.md)
for details.

---

## License

MIT License © Manya Singh
