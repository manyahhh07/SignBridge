"""
Holds a rolling window of recent landmark frames per connection, and
decides when there's enough signal to attempt a prediction.

This is what makes recognition temporal instead of frame-by-frame: the
model in Step 4 will consume a fixed-length window from this buffer,
not a single frame.
"""

from __future__ import annotations

from collections import deque

import numpy as np

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# A frame counts as "active" (part of a real gesture, not idle hands-down
# time) if at least one hand was detected. Used to trim leading/trailing
# idle frames before handing a window to the model.
MIN_ACTIVE_FRAME_RATIO = 0.3


class SequenceBuffer:
    """
    Fixed-capacity rolling buffer of (landmark_vector, meta) pairs.

    One instance per WebSocket connection - buffers must never be shared
    across users/streams.
    """

    def __init__(self, window_size: int | None = None) -> None:
        self.window_size = window_size or settings.sequence_length
        self._frames: deque[np.ndarray] = deque(maxlen=self.window_size)
        self._meta: deque[dict] = deque(maxlen=self.window_size)

    def add_frame(self, vector: np.ndarray, meta: dict) -> None:
        self._frames.append(vector)
        self._meta.append(meta)

    def is_full(self) -> bool:
        return len(self._frames) == self.window_size

    def active_frame_ratio(self) -> float:
        """Fraction of buffered frames where at least one hand was visible."""
        if not self._meta:
            return 0.0
        active = sum(1 for m in self._meta if m["has_left_hand"] or m["has_right_hand"])
        return active / len(self._meta)

    def has_enough_signal(self) -> bool:
        """
        Gate used before running the (comparatively expensive) recognition
        model - skips prediction on buffers that are mostly idle/empty,
        which is exactly the "ignore accidental gestures" requirement
        from the spec.
        """
        return self.is_full() and self.active_frame_ratio() >= MIN_ACTIVE_FRAME_RATIO

    def get_window(self) -> np.ndarray:
        """Returns the buffered frames stacked as (window_size, FRAME_VECTOR_SIZE)."""
        if not self._frames:
            raise ValueError("Cannot get window from an empty buffer.")
        return np.stack(self._frames, axis=0)

    def clear(self) -> None:
        self._frames.clear()
        self._meta.clear()

    def __len__(self) -> int:
        return len(self._frames)