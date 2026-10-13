from __future__ import annotations

from pydantic import BaseModel, Field


class PublishResult(BaseModel):
    provider: str
    form_id: str
    responder_uri: str
    edit_uri: str | None = None
    question_count: int = Field(ge=0)
