# AI Shopping Assistant Backend

Production-ready FastAPI backend for an AI shopping assistant with:

- Intent extraction (category, budget, use-case, preferences)
- Clarifying-question flow when required information is missing
- 3 to 5 realistic product recommendations
- Real product links/images via SerpAPI (with fallback search links)
- Structured JSON response for frontend integration
- In-memory caching and ranking logic
- HuggingFace Inference API integration (free tier)
- Safe JSON fallback behavior to avoid crashes

## API Contract

### POST `/chat`

Request:

```json
{
  "message": "I need a laptop for programming under 80000",
  "history": [
    { "role": "user", "content": "I need a laptop" },
    { "role": "assistant", "content": "What's your budget?" }
  ]
}
```

Response:

```json
{
  "reply": "Here are strong laptop options for your use case.",
  "products": [
    {
      "name": "...",
      "price": "...",
      "platform": "Amazon",
      "link": "https://...",
      "image": "https://...",
      "reason": "..."
    }
  ],
  "follow_up_questions": []
}
```

## Setup

1. Create a virtual environment and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

2. Create `.env` from `.env.example` and set keys:

- `LLM_PROVIDER=huggingface`
- `HF_API_KEY`
- optional `HF_MODEL` (default: `mistralai/Mistral-7B-Instruct-v0.2`)
- optional `SERPAPI_API_KEY` for better link quality

3. Run server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Health check:

```bash
GET http://localhost:8000/health
```

5. Chat endpoint:

```bash
POST http://localhost:8000/chat
```

## Notes

- If SerpAPI is unavailable, links fall back to Amazon query URLs.
- LLM calls are wrapped safely so `/chat` always returns JSON.
- Cache is in-memory (TTL) and configurable with `CACHE_TTL_SECONDS` and `CACHE_MAXSIZE`.
