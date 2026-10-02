from typing import Literal

from pydantic import BaseModel, Field


class IntentClassification(BaseModel):
    intent: Literal[
        "summary",
        "explanation",
        "translation",
        "rishonim",
        "halacha",
        "sources",
        "vocabulary",
        "quiz",
        "general",
    ]
    confidence: float = Field(ge=0, le=1)
