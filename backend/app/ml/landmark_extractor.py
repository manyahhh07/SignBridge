"""
Wraps MediaPipe Holistic so the rest of the app deals with plain numpy
arrays, not MediaPipe's internal protobuf objects.

Holistic gives us hands + pose + face in one pass, which is what the
spec calls for (hands alone lose shoulder/torso context that matters
for a lot of signs).
"""

from __future__ import annotations

import numpy as np

try:
    import mediapipe as mp
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "mediapipe is required for landmark extraction. "
        "Install it with: pip install mediapipe"
    ) from exc

from app.core.logger import get_logger

logger = get_logger(__name__)

# Landmark counts fixed by the MediaPipe Holistic model itself
NUM_POSE_LANDMARKS = 33
NUM_HAND_LANDMARKS = 21
NUM_FACE_LANDMARKS = 468

# Each landmark contributes (x, y, z). Pose also has visibility, but we
# drop it here so every landmark type has a uniform width and concatenation
# is trivial downstream.
POSE_VECTOR_SIZE = NUM_POSE_LANDMARKS * 3
HAND_VECTOR_SIZE = NUM_HAND_LANDMARKS * 3
FACE_VECTOR_SIZE = NUM_FACE_LANDMARKS * 3

# pose + left hand + right hand + face
FRAME_VECTOR_SIZE = POSE_VECTOR_SIZE + 2 * HAND_VECTOR_SIZE + FACE_VECTOR_SIZE


class LandmarkExtractor:
    """
    Stateful wrapper around a single MediaPipe Holistic instance.

    MediaPipe's Holistic solution is NOT thread-safe - one instance must
    only ever be used by one stream of frames at a time. In routes_ws.py
    we create one LandmarkExtractor per WebSocket connection for that reason.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        model_complexity: int = 1,
    ) -> None:
        self._mp_holistic = mp.solutions.holistic
        self._holistic = self._mp_holistic.Holistic(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            model_complexity=model_complexity,
            refine_face_landmarks=False,
        )
        logger.info(
            "LandmarkExtractor initialized (model_complexity=%d)", model_complexity
        )

    def process(self, frame_bgr: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Run holistic detection on a single BGR frame (OpenCV's default format).

        Returns:
            landmarks: float32 array of shape (FRAME_VECTOR_SIZE,).
                       Missing landmark groups (e.g. no hand visible) are
                       zero-filled rather than omitted, so every frame
                       vector has a constant, model-friendly shape.
            meta: dict flagging which landmark groups were actually detected,
                  used upstream to decide whether a frame is "real" signing
                  or an empty/idle frame.
        """
        # MediaPipe expects RGB, OpenCV gives BGR. The [::-1] channel-reverse
        # produces a view with negative strides, which MediaPipe's C++ backend
        # rejects ("data is not c_contiguous") - ascontiguousarray forces a
        # real copy with normal strides.
        rgb = np.ascontiguousarray(frame_bgr[:, :, ::-1])
        rgb.flags.writeable = False
        results = self._holistic.process(rgb)

        pose = self._landmarks_to_array(results.pose_landmarks, NUM_POSE_LANDMARKS)
        left_hand = self._landmarks_to_array(results.left_hand_landmarks, NUM_HAND_LANDMARKS)
        right_hand = self._landmarks_to_array(results.right_hand_landmarks, NUM_HAND_LANDMARKS)
        face = self._landmarks_to_array(results.face_landmarks, NUM_FACE_LANDMARKS)

        vector = np.concatenate([pose, left_hand, right_hand, face]).astype(np.float32)

        meta = {
            "has_pose": results.pose_landmarks is not None,
            "has_left_hand": results.left_hand_landmarks is not None,
            "has_right_hand": results.right_hand_landmarks is not None,
            "has_face": results.face_landmarks is not None,
        }
        return vector, meta

    @staticmethod
    def _landmarks_to_array(landmark_list, expected_count: int) -> np.ndarray:
        if landmark_list is None:
            return np.zeros(expected_count * 3, dtype=np.float32)
        coords = np.array(
            [[lm.x, lm.y, lm.z] for lm in landmark_list.landmark],
            dtype=np.float32,
        )
        return coords.flatten()

    def close(self) -> None:
        self._holistic.close()