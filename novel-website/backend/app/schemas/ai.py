from pydantic import BaseModel, Field
from typing import Optional


class AIGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    mode: str = Field(default="setting", pattern="^(setting|tag|volume|chapter|draft|polish|continue)$")
    context: Optional[str] = Field(None, max_length=16000)
    temperature: float = Field(default=0.8, ge=0.1, le=1.5)
    max_tokens: int = Field(default=4096, ge=128, le=8192)
    style: Optional[str] = None


class AIGenerateResponse(BaseModel):
    content: str
    finish_reason: str = "stop"
    usage: Optional[dict] = None