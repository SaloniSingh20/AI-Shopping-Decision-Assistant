from urllib.parse import quote_plus

import requests

from app.config import get_settings


def fetch_product_links(product_name: str) -> dict[str, str]:
    settings = get_settings()

    if settings.serpapi_api_key:
        try:
            params = {
                "engine": "google_shopping",
                "q": product_name,
                "api_key": settings.serpapi_api_key,
                "num": 5,
            }
            response = requests.get("https://serpapi.com/search.json", params=params, timeout=12)
            response.raise_for_status()
            data = response.json()
            shopping_results = data.get("shopping_results", [])
            if shopping_results:
                top = shopping_results[0]
                return {
                    "platform": top.get("source", "Online"),
                    "link": top.get("product_link") or top.get("link", ""),
                    "image": top.get("thumbnail", ""),
                }
        except Exception:
            # Fall back to deterministic search links when the API fails.
            pass

    encoded = quote_plus(product_name)
    return {
        "platform": "Amazon",
        "link": f"https://www.amazon.in/s?k={encoded}",
        "image": "",
    }
