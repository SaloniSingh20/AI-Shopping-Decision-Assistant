import json
import re
from typing import Any

from app.cache import get_cache, set_cache
from app.llm import LLMClient
from app.product_links import fetch_product_links
from app.mock_generator import generate_mock_products

SYSTEM_PROMPT = """You are Shop AI, a friendly and intelligent shopping assistant for Indian e-commerce.
Your job is to help users discover products through natural conversation, just like a helpful store assistant would.

PERSONALITY:
- Be warm, conversational, and enthusiastic about helping users find what they need
- Understand context from the conversation and remember what the user is looking for
- Ask clarifying questions naturally when needed (budget, preferences, use case)
- Provide personalized recommendations with genuine reasoning
- Be knowledgeable about Indian e-commerce trends and popular products

RULES:
1. Always respond with a valid JSON object — no markdown, no prose outside the JSON.
2. Recommend 3–5 products. Each product MUST have all fields filled.
3. Products must be realistic items sold on Myntra, Flipkart, Amazon India, or Meesho.
4. Prices MUST be in Indian Rupees (₹) and respect the user's budget.
5. The "reason" field must explain WHY this product suits the user's specific needs (1–2 sentences).
6. NEVER use placeholder URLs like example.com or placeholder.com — use real platform search URLs.
7. Set "score" between 0.5 and 1.0 based on how well the product matches the query.
8. The "tags" array should include: fit type (if clothing), use-case, color (if mentioned).
9. Generate 2–3 follow-up questions to personalise further.
10. Your "reply" should be conversational and contextual - acknowledge what the user asked for specifically

URL PATTERNS (use realistic slugs):
- Myntra: https://www.myntra.com/{category}/{brand}/{product-name}/{id}/buy
- Flipkart: https://www.flipkart.com/{product-name}/p/{id}
- Amazon: https://www.amazon.in/{product-name}/dp/{id}
- Meesho: https://meesho.com/...

IMAGE PATTERNS (use CDN-style URLs):
- Myntra: https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/{id}.jpg
- Flipkart: https://rukminim2.flixcart.com/image/416/416/{id}.jpeg
- Amazon: https://m.media-amazon.com/images/I/{id}.jpg

FEW-SHOT EXAMPLES:

USER: I want pants under 2000 rupees for office wear
ASSISTANT:
{
  "reply": "Great! I found some excellent office pants under ₹2000 that combine professional style with comfort. These are perfect for your workday.",
  "products": [
    {
      "name": "Peter England Slim Fit Formal Trouser",
      "price": "₹1,499",
      "price_numeric": 1499,
      "platform": "Myntra",
      "link": "https://www.myntra.com/trousers/peter-england/peter-england-slim-fit-formal-trouser/12345/buy",
      "image": "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/12345.jpg",
      "reason": "Slim fit with stretchable fabric, perfect for long office hours in charcoal grey.",
      "score": 0.91,
      "tags": ["formal", "slim-fit", "office", "grey", "under-1500"]
    },
    {
      "name": "Allen Solly Regular Fit Trousers",
      "price": "₹1,799",
      "price_numeric": 1799,
      "platform": "Amazon",
      "link": "https://www.amazon.in/allen-solly-regular-fit-trousers/dp/B08XYZ123",
      "image": "https://m.media-amazon.com/images/I/71abcdef123.jpg",
      "reason": "Classic regular fit in navy blue, wrinkle-resistant fabric ideal for daily office wear.",
      "score": 0.88,
      "tags": ["formal", "regular-fit", "office", "navy", "under-2000"]
    },
    {
      "name": "Van Heusen Tapered Fit Trousers",
      "price": "₹1,649",
      "price_numeric": 1649,
      "platform": "Myntra",
      "link": "https://www.myntra.com/trousers/van-heusen/van-heusen-tapered-fit-trousers/67890/buy",
      "image": "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/67890.jpg",
      "reason": "Modern tapered fit with easy-care fabric, looks sharp and stays comfortable all day.",
      "score": 0.89,
      "tags": ["formal", "tapered-fit", "office", "black", "under-2000"]
    }
  ],
  "follow_up_questions": [
    "Do you prefer slim fit or regular fit?",
    "Any preferred colour — navy, black, or grey?"
  ]
}

USER: wireless earbuds under 1500
ASSISTANT:
{
  "reply": "Perfect! Here are some top-rated wireless earbuds under ₹1500 with excellent battery life and sound quality.",
  "products": [
    {
      "name": "boAt Airdopes 141",
      "price": "₹1,299",
      "price_numeric": 1299,
      "platform": "Amazon",
      "link": "https://www.amazon.in/boat-airdopes-141/dp/B09ABC456",
      "image": "https://m.media-amazon.com/images/I/61xyz789.jpg",
      "reason": "Popular budget pick with 42H playback, IPX4 water resistance, and balanced sound.",
      "score": 0.93,
      "tags": ["wireless", "earbuds", "budget", "long-battery"]
    },
    {
      "name": "Noise Buds VS104",
      "price": "₹1,499",
      "price_numeric": 1499,
      "platform": "Flipkart",
      "link": "https://www.flipkart.com/noise-buds-vs104/p/itm123xyz",
      "image": "https://rukminim2.flixcart.com/image/416/416/abc123.jpeg",
      "reason": "Strong battery backup with quad mic for clear calls, great for work-from-home.",
      "score": 0.89,
      "tags": ["wireless", "earbuds", "calling", "budget"]
    },
    {
      "name": "Realme Buds Air 3",
      "price": "₹1,399",
      "price_numeric": 1399,
      "platform": "Amazon",
      "link": "https://www.amazon.in/realme-buds-air-3/dp/B09DEF789",
      "image": "https://m.media-amazon.com/images/I/51pqr890.jpg",
      "reason": "Active noise cancellation at this price point, plus fast charging and comfortable fit.",
      "score": 0.91,
      "tags": ["wireless", "earbuds", "anc", "budget"]
    }
  ],
  "follow_up_questions": [
    "Do you prioritize battery life or sound quality?",
    "Will you use them mainly for calls or music?"
  ]
}

USER: show me casual t-shirts
ASSISTANT:
{
  "reply": "I'd love to help you find casual t-shirts! To give you the best recommendations, could you share a bit more?",
  "products": [],
  "follow_up_questions": [
    "What's your budget for t-shirts?",
    "Any preferred colors or styles?",
    "Are you looking for plain, printed, or branded tees?"
  ]
}

RESPONSE FORMAT — return ONLY this JSON, no other text:
{
  "reply": "conversational response acknowledging the query",
  "products": [
    {
      "name": "Full product name with brand",
      "price": "₹X,XXX",
      "price_numeric": 1499,
      "platform": "Myntra|Flipkart|Amazon|Meesho",
      "link": "https://...",
      "image": "https://...",
      "reason": "Why this is a great match for the user",
      "score": 0.88,
      "tags": ["tag1", "tag2", "tag3"]
    }
  ],
  "follow_up_questions": ["Question 1?", "Question 2?"]
}
"""

INTENT_JSON_INSTRUCTION = """Return ONLY JSON with this schema:
{
  \"category\": \"string\",
  \"budget\": \"string\",
  \"use_case\": \"string\",
  \"preferences\": [\"string\"],
  \"missing_fields\": [\"budget\" | \"use_case\" | \"category\"],
  \"follow_up_questions\": [\"string\"]
}
Use empty strings/arrays when unknown."""

RECOMMEND_JSON_INSTRUCTION = """Return ONLY JSON with this schema:
{
  \"reply\": \"string\",
  \"products\": [
    {
      \"name\": \"string\",
      \"price\": \"string\",
      \"price_numeric\": number,
      \"platform\": \"Amazon|Flipkart|Myntra|Meesho\",
      \"link\": \"string\",
      \"image\": \"string\",
      \"reason\": \"string\",
      \"score\": number (between 0.5 and 1.0),
      \"tags\": [\"string\"]
    }
  ],
  \"follow_up_questions\": []
}
Rules:
- Recommend 3 to 5 realistic products only.
- Do not return an empty products array.
- Keep names recognizable and commonly sold online.
- NEVER use placeholder URLs — use real platform search URLs.
- Set score between 0.5 and 1.0 based on relevance.
- Include tags for fit type, use-case, and color if applicable.
- Keep follow_up_questions empty unless absolutely needed."""

# Removed static fallback products - AI should always generate contextual responses


def _cache_key(user_input: str, history: list[dict[str, str]]) -> str:
    history_key = json.dumps(history, sort_keys=True, ensure_ascii=True)
    return f"{user_input.strip().lower()}::{history_key}"


def _extract_budget_value(budget_text: str) -> float:
    values = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", budget_text.replace(",", ""))]
    return values[-1] if values else -1.0


def _extract_price_value(price_text: str) -> float:
    values = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", price_text.replace(",", ""))]
    return values[0] if values else -1.0


def _rank_products(products: list[dict[str, Any]], user_input: str, budget_text: str) -> list[dict[str, Any]]:
    budget = _extract_budget_value(budget_text)
    keywords = {k for k in re.findall(r"[a-zA-Z0-9]+", user_input.lower()) if len(k) > 2}

    def score(item: dict[str, Any]) -> float:
        name = str(item.get("name", "")).lower()
        reason = str(item.get("reason", "")).lower()
        text = f"{name} {reason}"
        query_score = sum(1 for token in keywords if token in text)

        price = _extract_price_value(str(item.get("price", "")))
        if budget > 0 and price > 0:
            budget_score = max(0.0, 1.0 - abs(price - budget) / max(budget, 1.0))
        else:
            budget_score = 0.25

        # Get LLM-assigned score or default
        llm_score = float(item.get("score", 0.5))
        
        # Penalize placeholder/fake links
        link = str(item.get("link", "")).lower()
        if "example.com" in link or "placeholder" in link:
            llm_score -= 0.30

        return (query_score * 1.2) + budget_score + llm_score

    scored_products = []
    for item in products:
        item_score = score(item)
        item["score"] = item_score
        # Filter out products with score below 0.3
        if item_score >= 0.3:
            scored_products.append(item)
    
    return sorted(scored_products, key=lambda p: p["score"], reverse=True)


def generate_response(user_input: str, history: list[dict[str, str]], preferences: dict[str, Any] | None = None):
    key = _cache_key(user_input, history)
    cached = get_cache(key)
    if cached:
        return cached

    # Build context with preferences
    context_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    
    # Add preference context if provided
    if preferences:
        budget_max = preferences.get("budget_max")
        gender = preferences.get("gender")
        pref_note = ""
        if budget_max:
            pref_note += f"User budget constraint: under ₹{budget_max}. "
        if gender:
            pref_note += f"User gender: {gender}. "
        if pref_note:
            context_messages.append({"role": "system", "content": pref_note.strip()})
    
    context_messages.append({"role": "user", "content": user_input})

    try:
        llm = LLMClient()

        # Generate AI-powered product recommendations
        recommendation = llm.generate_json(context_messages, RECOMMEND_JSON_INSTRUCTION)

        products = recommendation.get("products", []) or []
        products = products[:5]

        # If AI didn't generate products, retry with more explicit instruction
        if not products:
            print("No products generated, retrying with explicit instruction...")
            retry_context = context_messages + [
                {"role": "system", "content": "You MUST recommend at least 3 products. Generate realistic product recommendations based on the user's query."}
            ]
            recommendation = llm.generate_json(retry_context, RECOMMEND_JSON_INSTRUCTION)
            products = recommendation.get("products", []) or []
        
        # If still no products, use mock generator
        if not products:
            print("LLM failed to generate products, using mock generator...")
            mock_response = generate_mock_products(user_input, history)
            products = mock_response.get("products", [])
            recommendation["reply"] = mock_response.get("reply", recommendation.get("reply", ""))
            recommendation["follow_up_questions"] = mock_response.get("follow_up_questions", [])

        enriched_products = []
        for p in products:
            given_link = str(p.get("link", ""))
            given_platform = str(p.get("platform", ""))
            given_image = str(p.get("image", ""))

            links = fetch_product_links(str(p.get("name", "")))
            enriched_products.append(
                {
                    "name": str(p.get("name", "")),
                    "price": str(p.get("price", "")),
                    "price_numeric": p.get("price_numeric"),
                    "platform": given_platform or links.get("platform", ""),
                    "link": given_link or links.get("link", ""),
                    "image": given_image or links.get("image", ""),
                    "reason": str(p.get("reason", "")),
                    "score": float(p.get("score", 0.5)),
                    "tags": p.get("tags", []),
                }
            )

        ranked_products = _rank_products(
            enriched_products,
            user_input=user_input,
            budget_text=str(preferences.get("budget_max", "") if preferences else ""),
        )

        response = {
            "reply": str(recommendation.get("reply", "I'd love to help you find the perfect products! Could you tell me more about what you're looking for?")),
            "products": ranked_products,
            "follow_up_questions": recommendation.get("follow_up_questions", []) or [],
        }

        # Only add follow-up questions if no products were found
        if not response["products"]:
            response["follow_up_questions"] = [
                "What's your budget range?",
                "What category are you interested in? (clothing, electronics, accessories, etc.)",
                "What will you mainly use it for?",
            ]

        response["products"] = response["products"][:5]

        set_cache(key, response)
        return response
    except Exception as e:
        print(f"Pipeline error: {e}")
        # Use mock generator for error cases
        try:
            mock_response = generate_mock_products(user_input, history)
            set_cache(key, mock_response)
            return mock_response
        except Exception as mock_error:
            print(f"Mock generator also failed: {mock_error}")
            # Final fallback with helpful message
            safe_response = {
                "reply": "I'm having trouble processing your request right now. Could you tell me more about what you're looking for? For example, what's your budget and what category of products interests you?",
                "products": [],
                "follow_up_questions": [
                    "What's your budget range?",
                    "What category are you interested in?",
                    "What will you mainly use it for?",
                ],
            }
            set_cache(key, safe_response)
            return safe_response
