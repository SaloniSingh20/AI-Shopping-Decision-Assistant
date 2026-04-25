"""
Mock product generator for when LLM API fails.
Generates contextual, realistic products based on user query.
"""

import re
import random
from typing import Any


def extract_budget(text: str) -> tuple[float, float]:
    """Extract budget range from text."""
    numbers = [float(x) for x in re.findall(r"\d+(?:,\d+)?", text.replace(",", ""))]
    if numbers:
        max_budget = max(numbers)
        min_budget = max_budget * 0.5
        return min_budget, max_budget
    return 500, 5000


def extract_category(text: str) -> str:
    """Extract product category from text."""
    text_lower = text.lower()
    
    categories = {
        "pants": ["pants", "trousers", "jeans", "chinos"],
        "shirts": ["shirt", "tshirt", "t-shirt", "tee"],
        "shoes": ["shoes", "sneakers", "footwear", "boots"],
        "earbuds": ["earbuds", "earphones", "headphones", "airpods"],
        "laptop": ["laptop", "notebook", "computer"],
        "phone": ["phone", "mobile", "smartphone"],
        "watch": ["watch", "smartwatch"],
        "bag": ["bag", "backpack", "handbag"],
    }
    
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    
    return "general"


def generate_mock_products(user_query: str, history: list[dict[str, str]]) -> dict[str, Any]:
    """Generate contextual mock products based on user query."""
    
    min_budget, max_budget = extract_budget(user_query)
    category = extract_category(user_query)
    
    # Product templates by category
    product_templates = {
        "pants": [
            {
                "name": "Peter England Slim Fit Formal Trouser",
                "platform": "Myntra",
                "link": "https://www.myntra.com/trousers/peter-england/peter-england-men-slim-fit-formal-trousers/1234567/buy",
                "image": "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/productimage/2021/1/1/1234567.jpg",
                "reason": "Slim fit with stretchable fabric, perfect for long office hours. Available in charcoal grey.",
                "tags": ["formal", "slim-fit", "office", "grey"],
            },
            {
                "name": "Allen Solly Regular Fit Trousers",
                "platform": "Amazon",
                "link": "https://www.amazon.in/Allen-Solly-Regular-Fit-Trousers/dp/B08XYZ1234",
                "image": "https://m.media-amazon.com/images/I/71abcdef123.jpg",
                "reason": "Classic regular fit in navy blue, wrinkle-resistant fabric ideal for daily office wear.",
                "tags": ["formal", "regular-fit", "office", "navy"],
            },
            {
                "name": "Van Heusen Tapered Fit Trousers",
                "platform": "Flipkart",
                "link": "https://www.flipkart.com/van-heusen-tapered-fit-trousers/p/itm67890xyz",
                "image": "https://rukminim2.flixcart.com/image/416/416/k1234567/trouser/abc123.jpeg",
                "reason": "Modern tapered fit with easy-care fabric, looks sharp and stays comfortable all day.",
                "tags": ["formal", "tapered-fit", "office", "black"],
            },
            {
                "name": "Levi's 511 Slim Fit Jeans",
                "platform": "Amazon",
                "link": "https://www.amazon.in/Levis-511-Slim-Fit-Jeans/dp/B07ABC5678",
                "image": "https://m.media-amazon.com/images/I/61xyz789def.jpg",
                "reason": "Classic slim fit jeans with stretch denim, perfect for casual everyday wear.",
                "tags": ["casual", "slim-fit", "denim", "blue"],
            },
        ],
        "earbuds": [
            {
                "name": "boAt Airdopes 141",
                "platform": "Amazon",
                "link": "https://www.amazon.in/boAt-Airdopes-141-Wireless-Earbuds/dp/B09ABC4567",
                "image": "https://m.media-amazon.com/images/I/61xyz789abc.jpg",
                "reason": "Popular budget pick with 42H playback, IPX4 water resistance, and balanced sound quality.",
                "tags": ["wireless", "earbuds", "budget", "long-battery"],
            },
            {
                "name": "Noise Buds VS104",
                "platform": "Flipkart",
                "link": "https://www.flipkart.com/noise-buds-vs104-wireless-earbuds/p/itm123xyz789",
                "image": "https://rukminim2.flixcart.com/image/416/416/k9876543/headphone/abc123.jpeg",
                "reason": "Strong battery backup with quad mic for clear calls, great for work-from-home setup.",
                "tags": ["wireless", "earbuds", "calling", "budget"],
            },
            {
                "name": "Realme Buds Air 3",
                "platform": "Amazon",
                "link": "https://www.amazon.in/Realme-Buds-Air-3-Wireless/dp/B09DEF7890",
                "image": "https://m.media-amazon.com/images/I/51pqr890stu.jpg",
                "reason": "Active noise cancellation at this price point, plus fast charging and comfortable fit for long use.",
                "tags": ["wireless", "earbuds", "anc", "budget"],
            },
            {
                "name": "OnePlus Buds Z2",
                "platform": "Amazon",
                "link": "https://www.amazon.in/OnePlus-Buds-Z2-Wireless-Earbuds/dp/B09GHI1234",
                "image": "https://m.media-amazon.com/images/I/41vwx567yza.jpg",
                "reason": "Premium sound quality with active noise cancellation, 38-hour battery life, and IP55 rating.",
                "tags": ["wireless", "earbuds", "anc", "premium"],
            },
        ],
        "laptop": [
            {
                "name": "HP 15s Ryzen 5 Laptop",
                "platform": "Amazon",
                "link": "https://www.amazon.in/HP-15s-Ryzen-5-Laptop/dp/B0ABC12345",
                "image": "https://m.media-amazon.com/images/I/71abc123def.jpg",
                "reason": "Powerful Ryzen 5 processor with 8GB RAM and 512GB SSD, perfect for programming and multitasking.",
                "tags": ["laptop", "ryzen", "programming", "8gb"],
            },
            {
                "name": "Lenovo IdeaPad Slim 3",
                "platform": "Flipkart",
                "link": "https://www.flipkart.com/lenovo-ideapad-slim-3-laptop/p/itm456xyz789",
                "image": "https://rukminim2.flixcart.com/image/416/416/k7654321/computer/abc456.jpeg",
                "reason": "Lightweight design with Intel i5 processor, ideal for students and professionals on the go.",
                "tags": ["laptop", "intel", "slim", "portable"],
            },
            {
                "name": "ASUS VivoBook 15",
                "platform": "Amazon",
                "link": "https://www.amazon.in/ASUS-VivoBook-15-Laptop/dp/B0DEF67890",
                "image": "https://m.media-amazon.com/images/I/81ghi789jkl.jpg",
                "reason": "Full HD display with backlit keyboard, great for coding and content creation work.",
                "tags": ["laptop", "fullhd", "backlit", "coding"],
            },
        ],
        "shirts": [
            {
                "name": "Peter England Casual Shirt",
                "platform": "Myntra",
                "link": "https://www.myntra.com/shirts/peter-england/peter-england-men-casual-shirt/2345678/buy",
                "image": "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/productimage/2021/2/2/2345678.jpg",
                "reason": "Comfortable cotton blend in classic blue, perfect for casual outings and weekend wear.",
                "tags": ["casual", "cotton", "blue", "weekend"],
            },
            {
                "name": "US Polo Assn. T-Shirt",
                "platform": "Amazon",
                "link": "https://www.amazon.in/US-Polo-Assn-T-Shirt/dp/B08MNO3456",
                "image": "https://m.media-amazon.com/images/I/61pqr234stu.jpg",
                "reason": "Premium cotton t-shirt with logo print, great for everyday casual wear.",
                "tags": ["casual", "tshirt", "cotton", "branded"],
            },
            {
                "name": "H&M Regular Fit Shirt",
                "platform": "Myntra",
                "link": "https://www.myntra.com/shirts/hm/hm-men-regular-fit-shirt/3456789/buy",
                "image": "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/productimage/2021/3/3/3456789.jpg",
                "reason": "Trendy design with comfortable fit, perfect for casual office days or social events.",
                "tags": ["casual", "regular-fit", "trendy", "versatile"],
            },
        ],
        "general": [
            {
                "name": "Fastrack Analog Watch",
                "platform": "Amazon",
                "link": "https://www.amazon.in/Fastrack-Analog-Watch/dp/B07STU5678",
                "image": "https://m.media-amazon.com/images/I/51vwx901yza.jpg",
                "reason": "Stylish analog watch with leather strap, perfect for both casual and formal occasions.",
                "tags": ["watch", "analog", "leather", "versatile"],
            },
            {
                "name": "Wildcraft Backpack",
                "platform": "Flipkart",
                "link": "https://www.flipkart.com/wildcraft-backpack/p/itm789abc012",
                "image": "https://rukminim2.flixcart.com/image/416/416/k3456789/bag/def789.jpeg",
                "reason": "Durable backpack with laptop compartment, ideal for daily commute and travel.",
                "tags": ["backpack", "laptop", "travel", "durable"],
            },
            {
                "name": "Puma Sports Shoes",
                "platform": "Myntra",
                "link": "https://www.myntra.com/sports-shoes/puma/puma-men-sports-shoes/4567890/buy",
                "image": "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/productimage/2021/4/4/4567890.jpg",
                "reason": "Comfortable cushioning with breathable mesh, perfect for running and gym workouts.",
                "tags": ["shoes", "sports", "running", "comfortable"],
            },
        ],
    }
    
    # Get products for the category
    templates = product_templates.get(category, product_templates["general"])
    
    # Filter and adjust prices based on budget
    products = []
    for template in templates[:4]:  # Take up to 4 products
        # Generate price within budget
        price_numeric = random.randint(int(min_budget), int(max_budget))
        price_numeric = (price_numeric // 100) * 100  # Round to nearest 100
        
        product = {
            **template,
            "price": f"₹{price_numeric:,}",
            "price_numeric": price_numeric,
            "score": random.uniform(0.85, 0.95),
        }
        products.append(product)
    
    # Sort by score
    products.sort(key=lambda x: x["score"], reverse=True)
    
    # Generate contextual reply
    category_name = category if category != "general" else "products"
    reply = f"Great! I found some excellent {category_name} within your budget of ₹{int(max_budget):,}. These are popular choices that match your needs."
    
    follow_up_questions = []
    if category == "pants":
        follow_up_questions = [
            "Do you prefer slim fit or regular fit?",
            "Any preferred color — navy, black, or grey?",
        ]
    elif category == "earbuds":
        follow_up_questions = [
            "Do you prioritize battery life or sound quality?",
            "Will you use them mainly for calls or music?",
        ]
    elif category == "laptop":
        follow_up_questions = [
            "What will you mainly use it for — coding, gaming, or general use?",
            "Do you prefer Windows or would you consider other options?",
        ]
    else:
        follow_up_questions = [
            "Would you like to see more options in this category?",
            "Any specific brand preferences?",
        ]
    
    return {
        "reply": reply,
        "products": products,
        "follow_up_questions": follow_up_questions,
    }
