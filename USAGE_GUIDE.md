# Shop AI - Usage Guide

## Quick Start

### 1. Setup Environment

Create a `.env` file in the `backend/` directory:

```bash
HF_API_KEY=your_huggingface_token_here
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

Get your free HuggingFace API token from: https://huggingface.co/settings/tokens

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start the Backend

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at http://localhost:3000

## API Usage

### Basic Request (No Preferences)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "wireless earbuds under 1500"
  }'
```

### Request with User Preferences

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "office pants for daily wear",
    "preferences": {
      "budget_max": 2000,
      "gender": "male",
      "currency": "INR"
    }
  }'
```

### Request with Conversation History

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "show me slim fit options",
    "history": [
      {
        "role": "user",
        "content": "I need office pants"
      },
      {
        "role": "assistant",
        "content": "Here are some great office pants..."
      }
    ],
    "preferences": {
      "budget_max": 2000
    }
  }'
```

## Response Format

The API returns a structured JSON response:

```json
{
  "reply": "Here are 4 great office pants under ₹2000...",
  "products": [
    {
      "name": "Peter England Slim Fit Formal Trouser",
      "price": "₹1,499",
      "price_numeric": 1499,
      "platform": "Myntra",
      "link": "https://www.myntra.com/...",
      "image": "https://assets.myntassets.com/...",
      "reason": "Slim fit with stretchable fabric...",
      "score": 0.91,
      "tags": ["formal", "slim-fit", "office", "grey"]
    }
  ],
  "follow_up_questions": [
    "Do you prefer slim fit or regular fit?",
    "Any preferred colour — navy, black, or grey?"
  ]
}
```

## Features

### 1. User Preferences

Control recommendations with preferences:

- **budget_max**: Maximum price in rupees (e.g., 2000)
- **gender**: "male", "female", or null
- **currency**: "INR" (default)

### 2. Product Scoring

Products are scored 0.0-1.0 based on:
- Relevance to query
- Budget adherence
- Platform trust
- Link quality (penalizes placeholders)

Products with score < 0.3 are filtered out.

### 3. Product Tags

Each product includes descriptive tags:
- Fit type: "slim-fit", "regular-fit", "oversized"
- Use case: "office", "casual", "sports"
- Color: "black", "navy", "grey"
- Price range: "under-1500", "budget"

### 4. Conversation History

The system maintains context across messages:
- Remembers previous queries
- Refines recommendations based on follow-ups
- Handles clarification questions

### 5. Fallback Handling

Robust error handling:
- Primary model: Mistral-7B-Instruct-v0.2
- Fallback model: zephyr-7b-beta
- Fallback products if both fail
- Clarification prompts for vague queries

## Example Queries

### Budget-Focused
```
"wireless earbuds under 1500"
"office shoes under 3000 rupees"
"laptop under 50000"
```

### Use-Case Focused
```
"running shoes for marathon training"
"formal shirts for office wear"
"gaming headphones with good mic"
```

### Feature-Focused
```
"noise cancelling earbuds"
"water resistant smartwatch"
"lightweight laptop for travel"
```

### Combined Queries
```
"slim fit formal pants under 2000 in navy blue"
"wireless earbuds with long battery under 1500"
"casual sneakers for daily wear under 2500"
```

## Tips for Best Results

1. **Be specific**: Include budget, use-case, or key features
2. **Use follow-ups**: Answer the AI's clarifying questions
3. **Set preferences**: Provide budget_max for better filtering
4. **Check scores**: Higher scores (>0.8) indicate better matches
5. **Review tags**: Tags help identify product characteristics

## Troubleshooting

### "I had trouble generating recommendations"
- The LLM couldn't parse your query
- Try being more specific or answering follow-up questions

### Empty product list
- Fallback products will be shown
- Try rephrasing your query with more details

### Slow responses
- First request may take 10-20s (model loading)
- Subsequent requests are cached and faster
- Check your HuggingFace API key is valid

### Products don't match budget
- Ensure `budget_max` is set in preferences
- The ranking algorithm prioritizes budget adherence
- Some products may be slightly over budget (within 10%)

## Advanced Configuration

### Environment Variables

```bash
# LLM Configuration
HF_API_KEY=your_token
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Optional: SerpAPI for real product links
SERPAPI_API_KEY=your_serpapi_key

# Cache Configuration
CACHE_TTL_SECONDS=600
CACHE_MAXSIZE=512
```

### Caching

Responses are cached for 10 minutes (600 seconds) by default:
- Same query + history = cached response
- Reduces API calls and improves speed
- Adjust `CACHE_TTL_SECONDS` to change duration

## Health Check

Verify the backend is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

## Support

For issues or questions:
1. Check the logs in the terminal running uvicorn
2. Verify your HuggingFace API key is valid
3. Ensure all dependencies are installed
4. Review the IMPROVEMENTS.md for technical details
