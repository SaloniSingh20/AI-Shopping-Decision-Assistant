from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import ChatRequest, ChatResponse
from app.pipeline import generate_response
from app.cache import clear_cache

app = FastAPI(title="AI Shopping Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/clear-cache")
def clear_cache_endpoint() -> dict[str, str]:
    """Clear all cached responses."""
    clear_cache()
    return {"status": "cache cleared"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        history = [m.model_dump() for m in payload.history][-20:]
        preferences = payload.preferences.model_dump() if payload.preferences else None
        result = generate_response(payload.message, history, preferences)
        return ChatResponse(**result)
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        return ChatResponse(
            reply="I'm here to help you find great products! Could you tell me what you're looking for? For example, 'I need a laptop under ₹50,000' or 'Show me casual shirts'.",
            products=[],
            follow_up_questions=[
                "What's your budget range?",
                "What category interests you?",
                "Any specific features you're looking for?",
            ],
        )
