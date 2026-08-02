# SignBridge AI

Real-time translation between sign language and spoken/written language —
sign-to-text, text-to-sign, speech-to-sign, sign-to-speech, and a live
two-person conversation mode, in one app.

---
## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick start (Docker)](#quick-start-docker)
- [Manual setup](#manual-setup)
- [Verifying it's working](#verifying-its-working)
- [How each feature works](#how-each-feature-works)
- [Project structure](#project-structure)
- [Environment variables](#environment-variables)
- [Training the recognition model](#training-the-recognition-model)
- [Documentation](#documentation)
- [Build status](#build-status)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **Live Sign → Text** — webcam-based, temporal (45-frame window) gesture
  recognition streamed over a WebSocket, with confidence gating and
  automatic sentence building (punctuation, capitalization, repeat
  suppression).
- **Text → Sign** — type a phrase, watch it signed by an animated 3D
  skeletal hand.
- **Speech → Sign** — browser speech recognition feeds the same sign
  animation pipeline.
- **Sign → Speech** — recognized signs are read aloud via text-to-speech.
- **Conversation Mode** — split-screen: one person signs, the other
  speaks, both sides translated live into a shared transcript.
- Dark mode, high contrast, large text, and keyboard-shortcut support.

## Tech stack

| Layer | Stack |
|---|---|
| Frontend | React, TypeScript, Tailwind CSS, Three.js, Vite |
| Backend | Python, FastAPI, WebSockets |
| ML | MediaPipe Holistic, PyTorch (bidirectional LSTM) |
| Speech | OpenAI Whisper (speech-to-text), espeak-ng (text-to-speech) |

## Prerequisites

- Python 3.11+ (built and tested on 3.12)
- Node.js 20+
- `ffmpeg` (required by Whisper)
- `espeak-ng` (required by text-to-speech)
- A webcam and microphone, for the live features
- Docker + Docker Compose, if using the Docker path instead of manual setup

## Quick start (Docker)

The fastest way to get everything running:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Manual setup

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env

# System dependencies for speech features:
sudo apt-get install ffmpeg espeak-ng    # Debian/Ubuntu
brew install ffmpeg espeak-ng             # macOS

uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive API docs.

> **mediapipe is pinned to `0.10.14` deliberately** — newer releases
> removed the `mp.solutions.holistic` API this project depends on. Don't
> bump it without rewriting `app/ml/landmark_extractor.py`.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Visit `http://localhost:5173`. Make sure `frontend/.env`'s `VITE_API_URL`
and `VITE_WS_URL` point at wherever the backend is actually running.

## Verifying it's working

1. **Backend health check:**
   ```bash
   curl http://localhost:8000/api/v1/status
   # {"status": "ok", "app_name": "SignBridge AI", "environment": "development"}
   ```
2. **Dashboard page** (`/`) shows a green "API online" pill.
3. **Live Translate page** (`/translate`) prompts for camera permission;
   the status pill goes `Connecting…` → `Connected`, and a buffer counter
   (`Buffer: x/45 frames`) climbs as you move in frame.
4. **Text to Sign page** (`/text-to-sign`) — type "hello", click "Sign
   it", the 3D skeletal hand animates.
5. **Conversation page** (`/conversation`) — click "Start speaking" and
   talk; transcribed text appears in the shared chat.

## How each feature works

- **Sign → Text**: webcam frame → MediaPipe Holistic landmark extraction
  (server-side) → rolling 45-frame buffer, gated so idle hands don't
  trigger false predictions → bidirectional LSTM → confidence-gated gloss
  → sentence builder (dedup, punctuation, capitalization) → rendered live.
- **Text → Sign**: typed words → looked up in a small local gesture
  library → Three.js skeletal hand interpolates through the pose sequence.
- **Speech → Sign**: browser's native Web Speech API transcribes locally,
  feeding the same gesture pipeline as Text → Sign.
- **Sign → Speech**: recognized sentence sent to the backend, synthesized
  via espeak-ng, played back as audio.
- **Conversation Mode**: both pipelines running side by side with a
  shared transcript.

Full technical detail: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Project structure

```
signbridge-ai/
├── frontend/                      React + TypeScript + Tailwind + Three.js
│   └── src/
│       ├── components/            webcam/, avatar/, translation/, layout/, ui/
│       ├── hooks/                 useWebcam, useWebSocket, useSpeechRecognition
│       ├── pages/                 Dashboard, LiveTranslate, TextToSign, Conversation, Settings
│       ├── data/gestureLibrary.ts demo pose keyframes for the 3D hand
│       ├── services/              api.ts, env.ts
│       └── types/translation.ts
│
├── backend/                       FastAPI + WebSockets
│   └── app/
│       ├── api/                   routes_translate, routes_ws, routes_speech
│       ├── core/                  config, logger
│       ├── ml/                    landmark_extractor, sequence_buffer, sign_recognizer,
│       │                          sentence_builder, model_loader
│       └── speech/                stt (Whisper), tts (espeak-ng)
│
├── models/sign_recognition/       train.py, model_def.py, checkpoints/
├── datasets/loaders/              base_loader, wlasl_loader, synthetic_loader
├── animations/gesture_library/    (placeholder — see note below)
├── docs/                          architecture, API reference, install/training/
│                                   dataset/deployment guides, roadmap
├── docker-compose.yml
└── .gitignore
```

## Environment variables

**Backend** (`backend/.env`, see `backend/.env.example`):

| Variable | Default | Effect |
|---|---|---|
| `APP_NAME` | `SignBridge AI` | Display name |
| `ENVIRONMENT` | `development` | Environment label |
| `DEBUG` | `true` | Verbose logging |
| `HOST` / `PORT` | `0.0.0.0` / `8000` | Bind address |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed frontend origins |
| `MODEL_CHECKPOINT_PATH` | `../models/sign_recognition/checkpoints/latest.pt` | Trained model location |
| `SEQUENCE_LENGTH` | `45` | WebSocket buffer window size |
| `CONFIDENCE_THRESHOLD` | `0.75` | Minimum confidence to accept a prediction |
| `WHISPER_MODEL_SIZE` | `base` | Whisper model size for speech-to-text |
| `TTS_ENGINE` | `piper` (falls back to espeak-ng) | Text-to-speech engine |

**Frontend** (`frontend/.env`, see `frontend/.env.example`):

| Variable | Default | Effect |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Backend REST base URL |
| `VITE_WS_URL` | `ws://localhost:8000/ws/translate` | Backend WebSocket URL |

Full reference: [`docs/API.md`](docs/API.md).

## Training the recognition model

The backend ships with an **untrained** model by default — it works
end-to-end mechanically, but predictions won't be meaningful until
trained.

```bash
# Sanity-check the pipeline (no dataset needed):
cd models/sign_recognition
python train.py --dataset synthetic --epochs 5

# Train for real, once WLASL is downloaded and pre-processed:
python train.py --dataset wlasl --dataset-root ../../datasets/wlasl --epochs 50 --batch-size 16
```

See [`docs/MODEL_TRAINING.md`](docs/MODEL_TRAINING.md) and
[`docs/DATASET_SETUP.md`](docs/DATASET_SETUP.md) for full detail.

## Documentation

| Doc | Covers |
|---|---|
| [`docs/INSTALLATION.md`](docs/INSTALLATION.md) | Full local setup, prerequisites, troubleshooting |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | How the sign→text and text→sign pipelines work end to end |
| [`docs/API.md`](docs/API.md) | REST + WebSocket reference, message shapes, env vars |
| [`docs/MODEL_TRAINING.md`](docs/MODEL_TRAINING.md) | How to train the recognition model |
| [`docs/DATASET_SETUP.md`](docs/DATASET_SETUP.md) | Getting WLASL (or another dataset) onto disk |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Docker and manual production deployment |
| [`docs/FUTURE_IMPROVEMENTS.md`](docs/FUTURE_IMPROVEMENTS.md) | Roadmap, ordered by impact |
| [`models/README.md`](models/README.md) | Model architecture and status |
| [`datasets/README.md`](datasets/README.md) | Dataset loader abstraction, adding new datasets |
| [`animations/gesture_library/README.md`](animations/gesture_library/README.md) | Gesture data status and how to replace it with real data |

## Build status

Every layer is implemented and was verified by actually running it —
not just written and assumed to work:

- Backend: dependency install, server boot, `/status`, WebSocket
  round-trips (including idle-frame gating), and TTS audio output all
  confirmed live.
- Frontend: `npm install`, `tsc` typecheck, and `vite build` all pass
  clean; dev server serves all 5 routes with `200`.
- Model: a real training run (loss decreasing, accuracy climbing) with
  the resulting checkpoint confirmed loadable by the backend's inference
  path.

## Known limitations

- **No trained model ships.** The backend runs on an untrained `SignLSTM`
  until [`models/sign_recognition/train.py`](models/sign_recognition/train.py)
  is run against a real dataset (the backend logs a clear warning about
  this on startup).
- **Gesture animation library is a placeholder.** `frontend/src/data/gestureLibrary.ts`
  is a small, hand-authored set of poses for a demo vocabulary, not
  linguistically accurate ASL. See
  [`animations/gesture_library/README.md`](animations/gesture_library/README.md).
- **Whisper (speech-to-text) downloads model weights on first use** —
  requires outbound internet access the first time it runs.
- **`POST /api/v1/translate/text-to-sign` is not implemented** (returns
  `501`) — text-to-sign currently runs entirely client-side instead.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `AttributeError: module 'mediapipe' has no attribute 'solutions'` | Wrong mediapipe version installed — must be `0.10.14` |
| WebSocket never reaches "Connected" | `VITE_WS_URL` doesn't match where the backend is running, or a CORS mismatch |
| `TTSEngineNotAvailable` (503) | espeak-ng isn't installed / not on PATH |
| Whisper hangs on first speech-to-text request | Downloading model weights — needs internet the first time |
| Camera feed is black or errors | Browser denied camera permission, or another app is holding the camera |

More detail in [`docs/INSTALLATION.md`](docs/INSTALLATION.md).

## License

Not yet specified.
