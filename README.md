signbridge-ai/
│
├── frontend/                          # React + TypeScript + Tailwind
│   ├── public/
│   │   └── assets/
│   ├── src/
│   │   ├── components/
│   │   │   ├── webcam/
│   │   │   │   ├── WebcamFeed.tsx
│   │   │   │   └── LandmarkOverlay.tsx
│   │   │   ├── translation/
│   │   │   │   ├── SignToText.tsx
│   │   │   │   ├── TextToSign.tsx
│   │   │   │   └── ConfidenceMeter.tsx
│   │   │   ├── avatar/
│   │   │   │   └── SignAvatar3D.tsx       # Three.js
│   │   │   ├── conversation/
│   │   │   │   └── ConversationMode.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Navbar.tsx
│   │   │   │   └── ThemeToggle.tsx
│   │   │   └── ui/                        # buttons, cards, modals (shared)
│   │   ├── hooks/
│   │   │   ├── useWebcam.ts
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useSpeechRecognition.ts
│   │   │   └── useMediaPipe.ts
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── LiveTranslate.tsx
│   │   │   ├── Conversation.tsx
│   │   │   └── Settings.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── websocket.ts
│   │   ├── store/                         # state management (Zustand)
│   │   ├── types/
│   │   ├── styles/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── backend/                           # Python + FastAPI
│   ├── app/
│   │   ├── main.py                        # FastAPI entrypoint
│   │   ├── api/
│   │   │   ├── routes_translate.py
│   │   │   ├── routes_speech.py
│   │   │   └── routes_ws.py               # WebSocket for live stream
│   │   ├── core/
│   │   │   ├── config.py                  # env vars
│   │   │   └── logger.py
│   │   ├── ml/
│   │   │   ├── landmark_extractor.py      # MediaPipe wrapper
│   │   │   ├── sequence_buffer.py
│   │   │   ├── sign_recognizer.py         # model inference
│   │   │   ├── sentence_builder.py        # grammar/punct logic
│   │   │   └── model_loader.py
│   │   ├── speech/
│   │   │   ├── stt.py                     # Whisper wrapper
│   │   │   └── tts.py                     # Piper/Coqui wrapper
│   │   └── schemas/
│   │       └── translation.py             # Pydantic models
│   ├── requirements.txt
│   └── .env.example
│
├── models/
│   ├── sign_recognition/
│   │   ├── train.py
│   │   ├── model_def.py                   # LSTM/GRU architecture
│   │   └── checkpoints/
│   └── README.md
│
├── datasets/
│   ├── loaders/
│   │   ├── wlasl_loader.py
│   │   └── base_loader.py                 # abstraction layer
│   └── README.md
│
├── animations/
│   └── gesture_library/                   # pre-recorded landmark sequences
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
│
├── .gitignore
├── docker-compose.yml
└── README.md
