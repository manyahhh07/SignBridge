# SignBridge AI — Target Structure

signbridge-ai/
├── frontend/
│   ├── public/assets/
│   ├── src/
│   │   ├── components/
│   │   │   ├── webcam/          WebcamFeed, LandmarkOverlay
│   │   │   ├── translation/     SignToText, TextToSign, ConfidenceMeter
│   │   │   ├── avatar/          SignAvatar3D (Three.js)
│   │   │   ├── conversation/    ConversationMode
│   │   │   ├── layout/          Sidebar, Navbar, ThemeToggle
│   │   │   └── ui/               shared buttons/cards/modals
│   │   ├── hooks/                useWebcam, useWebSocket, useSpeechRecognition, useMediaPipe
│   │   ├── pages/                Dashboard, LiveTranslate, Conversation, Settings
│   │   ├── services/             api.ts, websocket.ts
│   │   ├── store/                state management
│   │   ├── types/
│   │   ├── styles/
│   │   ├── App.tsx, main.tsx
│   ├── package.json, tailwind.config.ts, tsconfig.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/                  routes_translate, routes_speech, routes_ws
│   │   ├── core/                 config, logger
│   │   ├── ml/                   landmark_extractor, sequence_buffer, sign_recognizer,
│   │   │                         sentence_builder, model_loader
│   │   ├── speech/               stt, tts
│   │   └── schemas/               translation
│   ├── requirements.txt, .env.example
│
├── models/
│   ├── sign_recognition/         train.py, model_def.py, checkpoints/
│   └── README.md
│
├── datasets/
│   ├── loaders/                  wlasl_loader, base_loader (+ more per dataset)
│   └── README.md
│
├── animations/gesture_library/    real motion-capture / keyframe data
├── docs/                          ARCHITECTURE, API, DEPLOYMENT, etc.
├── .gitignore, docker-compose.yml, README.md
