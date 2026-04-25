# Self-Learning Shopping Decision Assistant for Indian Users

Voice-like conversational AI that understands shopping intent, asks smart follow-up questions, ranks realistic product options, and returns actionable recommendations for Indian e-commerce behavior (budget-sensitive, mixed-language prompts, and quick decisions over dashboard complexity).

Repository: AI-Shopping-Decision-Assistant

## Problem
Online shopping decisions are noisy, time-consuming, and often overwhelming.

- Users know what they need, but not what to buy first
- Queries are incomplete: category without budget, or budget without use-case
- Results are crowded with generic listings instead of tailored suggestions
- Most tools return search results, not guided decisions

Users do not want endless scrolling. They need:

"What should I buy right now within my budget?"

## Solution
A self-learning Shopping Decision Assistant that:

| Capability | What it means |
|---|---|
| Understands messy intent | Extracts category, budget, use-case, and preferences from natural language |
| Asks for missing context | Generates follow-up questions when query details are incomplete |
| Recommends with reasoning | Returns 3-5 realistic products with explanation and relevance score |
| Enriches links automatically | Uses SerpAPI when available; falls back to deterministic Amazon search links |
| Handles failure safely | Multi-level fallback (primary model -> fallback models -> mock generator -> safe response) |
| Responds in a product-first UI | Chat-first interface with cards, follow-up chips, and session flow |

This is not just another product search page. It is a decision layer on top of ambiguous shopping input.

## Key Features

### Shopping intelligence
- Intent-aware recommendation from user message + recent conversation history
- Budget-aware ranking via text and numeric signals
- Relevance scoring and low-score filtering
- Product tags for quick scan (fit/use-case/color style labels)

### Decision engine behavior
- Clarifying questions when product generation is insufficient
- Top recommendations ordered by query match + budget proximity + model confidence
- Conversational reply plus structured product payload for UI rendering

### Execution and integration layer
- FastAPI endpoints for health, recommendation chat, and cache reset
- Optional Hugging Face Inference API for generation
- Optional SerpAPI for better marketplace links/images

### Frontend experience
- Next.js app with modern chat workflow
- Product cards with platform, reason, and score context
- Follow-up question chips for one-click refinement
- Session sidebar, new chat flow, typing indicators, responsive layout

### Reliability
- Cache-based response acceleration (TTL + max size configurable)
- Retry behavior for model loading responses
- Fallback models and safe JSON structure on errors

## Recently Implemented

| Area | What shipped |
|---|---|
| Backend schema | Preferences support (`budget_max`, `currency`, `gender`) and enriched product response (`price_numeric`, `score`, `tags`) |
| Prompt quality | Expanded system prompt, strong JSON constraints, and few-shot examples |
| Robustness | Empty response retries, fallback models, score filtering, graceful final fallback response |
| Product links | SerpAPI enrichment plus deterministic Amazon fallback |
| Frontend UX | Chat UI with product cards, follow-up chips, typing state, and sidebar sessions |
| Dev workflow | One-command local startup scripts for Windows and Linux/macOS |

## How It Works

The recommendation pipeline runs per chat request and returns a structured response that the UI directly renders.

### Request flow
1. User sends a shopping query from the chat UI.
2. Backend receives message + recent history (+ optional preferences).
3. LLM generates strict JSON recommendation output.
4. Products are enriched with links/images (SerpAPI or fallback).
5. Ranker scores and filters products.
6. API returns reply, products, and follow-up questions.

## API (Current)

### Core endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Basic service health check |
| `/chat` | POST | Main recommendation endpoint |
| `/clear-cache` | POST | Clears in-memory recommendation cache |

### Chat contract

Request:

```json
{
  "message": "I need earbuds under 1500",
  "history": [
    { "role": "user", "content": "I need earbuds" },
    { "role": "assistant", "content": "What is your budget?" }
  ],
  "preferences": {
    "budget_max": 1500,
    "currency": "INR",
    "gender": "unisex"
  }
}
```

Response:

```json
{
  "reply": "Great choice - here are strong earbuds under your budget.",
  "products": [
    {
      "name": "boAt Airdopes 141",
      "price": "₹1,299",
      "price_numeric": 1299,
      "platform": "Amazon",
      "link": "https://www.amazon.in/s?k=boAt+Airdopes+141",
      "image": "",
      "reason": "Balanced battery life and value in your budget segment.",
      "score": 1.86,
      "tags": ["earbuds", "budget", "wireless"]
    }
  ],
  "follow_up_questions": [
    "Will you use this mostly for calls or music?"
  ]
}
```

## Architecture

| Layer | Stack |
|---|---|
| API | FastAPI, Pydantic, Uvicorn |
| Recommendation core | Prompted LLM generation + custom ranking + fallback logic |
| Link enrichment | SerpAPI (optional) + deterministic fallback links |
| Caching | cachetools TTL cache |
| Frontend | Next.js 16, React 19, Tailwind CSS 4 |

## Data Model (High Level)

- Request model: message, conversation history, user preferences
- Response model: conversational reply, ranked product list, follow-up questions
- Product entity: name, price text/number, platform, link, image, reason, score, tags

Note: Current implementation is stateless per request except in-memory cache. Durable DB persistence is not required for core recommendation flow.

## What Makes This Different

| Typical Shopping Search | This System |
|---|---|
| Keyword listing pages | Conversational recommendation + decision guidance |
| Minimal personalization | Preference-aware ranking and follow-up refinement |
| Raw search output | Curated product set with reasons and scores |
| Fragile failure behavior | Multi-tier fallback and safe response contracts |

## Demo (2 Minutes)

1. Open the app and ask: "I want office pants under 2000".
2. Review ranked product cards and reasons.
3. Tap a follow-up chip to refine quickly.
4. Try a vague query like "show me casual t-shirts" and observe clarifying questions.

## Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm

### Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/macOS
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:3000

### One-command local startup

- Windows: run `start-dev.bat`
- Linux/macOS: run `./start-dev.sh`

## Environment (Summary)

| File | Purpose |
|---|---|
| `backend/.env` | `HF_API_KEY`, `HF_MODEL`, optional `SERPAPI_API_KEY`, cache config |
| `backend/.env.example` | Template for backend environment variables |

Copy from `.env.example`. Never commit secrets.

## Future Work

- Add multilingual (Hindi/Hinglish) translation and voice I/O path in production pipeline
- Add persistent chat and analytics store for long-term personalization
- Add marketplace adapters beyond current link enrichment strategy
- Add feedback loop to tune ranking policy over time
- Add deployment recipes for containerized backend and hosted frontend

## Vision
Build an AI shopping operating layer where users can decide faster, spend smarter, and buy with confidence - without digging through endless product pages.

## Reference

| Topic | Where |
|---|---|
| Backend API and pipeline | `backend/README.md` |
| Local setup walkthrough | `QUICK_START.md` |
| Improvement log | `IMPROVEMENTS.md` |
| Implementation summary | `IMPLEMENTATION_SUMMARY.md` |
| Usage examples | `USAGE_GUIDE.md` |

License: Add a LICENSE before open-sourcing; until then all rights reserved unless stated otherwise.
