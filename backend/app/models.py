from typing import Literal, Optional

from pydantic import BaseModel, Field


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class UserPreferences(BaseModel):
    budget_max: Optional[float] = None
    currency: str = "INR"
    gender: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[HistoryMessage] = Field(default_factory=list)
    preferences: UserPreferences = Field(default_factory=UserPreferences)


class ProductRecommendation(BaseModel):
    name: str = ""
    price: str = ""
    price_numeric: Optional[float] = None
    platform: str = ""
    link: str = ""
    image: str = ""
    reason: str = ""
    score: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    products: list[ProductRecommendation] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
