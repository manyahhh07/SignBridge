"""
WebSocket endpoint the frontend's webcam component streams frames to.

Protocol (JSON messages over the socket):

  Client -> Server:
    { "type": "frame", "data": "<base64 JPEG/PNG>" }

  Server -> Client:
    { "type": "landmarks", "meta": {...}, "buffer_progress": 12, "window_size": 45 }
    { "type": "ready_for_prediction" }   <- sent once buffer has enough signal
    { "type": "error", "message": "..." }

Step 2 stops at "ready_for_prediction" - it does NOT run a model yet.
Step 4 hooks sign_recognizer.py in right where that message is emitted.

One LandmarkExtractor + one SequenceBuffer is created per connection and
torn down on disconnect, since neither is safe to share across streams.
"""

from __future__ import annotations

import base64
import binascii

import cv2
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logger import get_logger
from app.ml.landmark_extractor import LandmarkExtractor
from app.ml.sequence_buffer import SequenceBuffer

router = APIRouter()
logger = get_logger(__name__)


def _decode_frame(b64_data: str) -> np.ndarray | None:
    """Decode a base64-encoded image into an OpenCV BGR array, or None if invalid."""
    try:
        # Strip a data URL prefix like "data:image/jpeg;base64," if present
        if "," in b64_data[:64]:
            b64_data = b64_data.split(",", 1)[1]
        raw = base64.b64decode(b64_data, validate=True)
    except (binascii.Error, ValueError):
        return None

    buffer = np.frombuffer(raw, dtype=np.uint8)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    return frame  # None if cv2 couldn't decode it


@router.websocket("/ws/translate")
async def websocket_translate(websocket: WebSocket) -> None:
    await websocket.accept()
    logger.info("WebSocket connected: %s", websocket.client)

    extractor = LandmarkExtractor()
    buffer = SequenceBuffer()

    try:
        while True:
            payload = await websocket.receive_json()

            if payload.get("type") != "frame":
                await websocket.send_json(
                    {"type": "error", "message": f"Unknown message type: {payload.get('type')}"}
                )
                continue

            frame = _decode_frame(payload.get("data", ""))
            if frame is None:
                await websocket.send_json(
                    {"type": "error", "message": "Could not decode frame data."}
                )
                continue

            vector, meta = extractor.process(frame)
            buffer.add_frame(vector, meta)

            await websocket.send_json(
                {
                    "type": "landmarks",
                    "meta": meta,
                    "buffer_progress": len(buffer),
                    "window_size": buffer.window_size,
                }
            )

            if buffer.has_enough_signal():
                await websocket.send_json({"type": "ready_for_prediction"})
                # Step 4 will replace this comment with a call into
                # sign_recognizer.py using buffer.get_window(), then
                # buffer.clear() (or a sliding partial-clear) afterward.

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s", websocket.client)
    finally:
        extractor.close()