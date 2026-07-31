# SignBridge AI

Real-time translation between sign language and spoken/written language —
sign-to-text, text-to-sign, speech-to-sign, sign-to-speech, and a live
two-person conversation mode, in one app.

## Features

- **Live Sign → Text** — webcam-based, temporal (45-frame window) gesture
  recognition over a WebSocket, with confidence gating and automatic
  sentence building (punctuation, capitalization, repeat suppression).
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
| Speech | OpenAI Whisper (STT), espeak-ng (TTS) |

## Quick start

**Docker (fastest):**
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```
Backend on `http://localhost:8000`, frontend on `http://localhost:5173`.

**Manual:** see [`docs/INSTALLATION.md`](docs/INSTALLATION.md) for full
setup, including system dependencies (`ffmpeg`, `espeak-ng`) and
troubleshooting.

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

Every layer is implemented and was verified by actually running it
(server boot, live WebSocket round-trips, `tsc`/`vite build`, a real
train → save-checkpoint → load-in-backend pass, valid TTS audio output) —
not just written and assumed to work. Full breakdown, including what's
stubbed vs. complete, is in [`docs/FUTURE_IMPROVEMENTS.md`](docs/FUTURE_IMPROVEMENTS.md).

## Known limitations

- **No trained model ships.** The backend runs on an untrained `SignLSTM`
  until [`models/sign_recognition/train.py`](models/sign_recognition/train.py)
  is run against a real dataset (the backend logs a clear warning about
  this on startup). Sign recognition works end-to-end mechanically;
  predictions won't be meaningful until trained on real data — see
  [`docs/MODEL_TRAINING.md`](docs/MODEL_TRAINING.md).
- **Gesture animation library is a placeholder.** `frontend/src/data/gestureLibrary.ts`
  is a small, hand-authored set of poses for a demo vocabulary, not
  linguistically accurate ASL. See
  [`animations/gesture_library/README.md`](animations/gesture_library/README.md)
  for how to replace it with real motion-capture or dataset-derived data.
- **Whisper (speech-to-text) downloads model weights on first use** —
  requires outbound internet access the first time it runs.
- **`POST /api/v1/translate/text-to-sign` is not implemented** (returns
  `501`) — text-to-sign currently runs entirely client-side instead.

## License

Not yet specified.
