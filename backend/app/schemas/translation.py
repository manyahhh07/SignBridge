from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str


class SignToTextResult(BaseModel):
    """One recognized sign/word, emitted as part of a streamed sentence."""

    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    is_final: bool = False


class TextToSignRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    language: str = "en"


class TextToSignResponse(BaseModel):
    """
    Sequence of gesture identifiers the frontend animation player can
    step through. Populated by the gesture library in a later step.
    """

    gestures: list[str]
    original_text: str
