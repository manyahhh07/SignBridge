"""
Centralized application configuration.

All environment-dependent values live here, loaded from a .env file via
pydantic-settings. Nothing else in the app should call os.getenv directly -
import `settings` from this module instead, so every value has one source
of truth and is validated at startup.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "SignBridge AI"
    environment: str = "development"
    debug: bool = True

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- CORS ---
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # --- ML (wired up in Step 4) ---
    model_checkpoint_path: str = "../models/sign_recognition/checkpoints/latest.pt"
    sequence_length: int = 45
    confidence_threshold: float = 0.75

    # --- Speech (wired up in Step 7) ---
    whisper_model_size: str = "base"
    tts_engine: str = "piper"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # model_checkpoint_path starts with "model_", which pydantic warns
        # about by default (it reserves that prefix for its own internals).
        # It's not actually a conflict here, so we disable the check.
        protected_namespaces=(),
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS_ORIGINS as a clean list, splitting on commas and trimming whitespace."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor. Using a function (rather than a bare module-level
    instance) makes it easy to override settings in tests via dependency
    injection / cache clearing later.
    """
    return Settings()


settings = get_settings()