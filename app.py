import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

import google.generativeai as genai
import streamlit as st

from products import products


PRODUCT_SYSTEM_PROMPT = """
You are an expert AI shopping decision assistant, not just a recommender.

Your job is to help users MAKE the best decision, not just list options.

STRICT RULES:
- Only use products from the provided dataset. Never hallucinate.
- If no exact match exists, suggest the closest alternatives and explain why.
- Always prioritize relevance, clarity, and usefulness.

THINKING PROCESS (internal, do not show steps):
1. Understand user intent (goal, budget, use-case)
2. Identify constraints (price, category, preferences)
3. Match products based on tags, category, and price
4. Rank options based on best fit
5. Evaluate trade-offs

OUTPUT REQUIREMENTS:
For every recommendation:
- Clearly explain WHY it matches the user’s need
- State BEST use-case
- Mention TRADE-OFFS (important)
- Give a FINAL actionable suggestion (what user should do)

STYLE:
- Be concise but insightful
- Avoid generic phrases
- Be confident and helpful

DECISION GUIDANCE:
Always guide the user like:
“If your priority is X → choose A”
“If your priority is Y → choose B”

FALLBACK:
If the query is unclear:
- Ask ONE smart clarifying question

GOAL:
Act like a smart shopping advisor that helps users confidently decide.
"""

GENERAL_SYSTEM_PROMPT = """
You are a helpful, practical AI assistant.

You can answer general questions like ChatGPT and provide useful guidance.
If relevant, include concise actionable next steps.
Do not invent products from the user's catalog unless they are explicitly provided.
When the user asks outside the catalog domain, answer normally with general knowledge.
Keep responses clear, concise, and helpful.
"""

CHAT_STORE_FILE = "chats_store.json"
KNOWN_CATEGORIES = sorted({p["category"].lower() for p in products})
KNOWN_TAGS = sorted({tag.lower() for p in products for tag in p["tags"]})
PRODUCT_BY_NAME = {p["name"]: p for p in products}


st.set_page_config(page_title="AI Shopping Decision Assistant", page_icon="🛍️", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
        font-family: 'Manrope', sans-serif;
    }

    :root {
        --bg: #1f2023;
        --bg-accent-1: rgba(124, 133, 255, 0.10);
        --bg-accent-2: rgba(86, 176, 255, 0.08);
        --surface: #2a2b30;
        --surface-soft: #25262b;
        --surface-sidebar: #17181b;
        --text-main: #eceef4;
        --text-soft: #a2a7b5;
        --line-soft: #393b42;
        --line-strong: #43454e;
        --radius-xl: 24px;
        --radius-lg: 20px;
        --radius-md: 16px;
        --shadow-soft: 0 10px 26px rgba(0, 0, 0, 0.25);
        --shadow-card: 0 8px 20px rgba(0, 0, 0, 0.24);
        --shadow-float: 0 12px 30px rgba(0, 0, 0, 0.32);
    }

    .stApp {
        background:
            radial-gradient(circle at 6% 10%, var(--bg-accent-1) 0%, rgba(255, 202, 186, 0) 36%),
            radial-gradient(circle at 95% 14%, var(--bg-accent-2) 0%, rgba(186, 205, 255, 0) 34%),
            linear-gradient(180deg, #1f2023 0%, #1d1e22 100%);
        color: var(--text-main);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #17181b 0%, #141519 100%);
        border-right: 1px solid #2a2c33;
    }

    [data-testid="stSidebar"] > div {
        padding-top: 1.1rem;
        padding-left: 0.65rem;
        padding-right: 0.65rem;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        border-bottom: 0;
    }

    [data-testid="stSidebar"] .stTextInput > div > div {
        border-radius: var(--radius-md);
        border: 1px solid var(--line-strong);
        background: #212228;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
    }

    [data-testid="stSidebar"] .stTextInput input {
        color: var(--text-main) !important;
        caret-color: var(--text-main) !important;
    }

    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: #9096a6 !important;
        opacity: 1;
    }

    [data-testid="stSidebar"] button {
        border-radius: 16px !important;
        border: 1px solid var(--line-strong) !important;
        background: linear-gradient(180deg, #23242a 0%, #1c1d23 100%) !important;
        color: var(--text-main) !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.28);
        transition: all 0.18s ease;
        padding-top: 0.38rem !important;
        padding-bottom: 0.38rem !important;
    }

    [data-testid="stSidebar"] button:hover {
        background: linear-gradient(180deg, #2b2d34 0%, #22242b 100%) !important;
        border-color: #575b67 !important;
        transform: translateY(-1px) scale(1.01);
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 6.6rem;
        max-width: 1020px;
    }

    .hero {
        background: linear-gradient(135deg, #2a2b31 0%, #25262c 60%, #23242a 100%);
        border: 1px solid var(--line-soft);
        border-radius: var(--radius-xl);
        padding: 1.65rem 1.8rem;
        margin-bottom: 1.6rem;
        box-shadow: var(--shadow-soft);
        text-align: center;
    }

    .hero h1 {
        margin: 0;
        color: var(--text-main);
        font-size: 2.15rem;
        letter-spacing: -0.02em;
        font-weight: 800;
        line-height: 1.18;
    }

    .hero p {
        margin: 0.55rem 0 0;
        color: var(--text-soft);
        font-size: 1.04rem;
        font-weight: 500;
    }

    .subtle-note {
        margin: 0.15rem 0 1.25rem;
        border: 1px solid var(--line-soft);
        background: linear-gradient(180deg, #26272d 0%, #23242a 100%);
        border-radius: var(--radius-md);
        padding: 0.86rem 1rem;
        color: var(--text-soft);
        font-size: 0.95rem;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.22);
    }

    .card {
        border: 1px solid var(--line-soft);
        border-radius: 22px;
        padding: 1.24rem 1.2rem 1.08rem;
        margin-bottom: 1.2rem;
        background: var(--surface);
        box-shadow: var(--shadow-card);
    }

    .best {
        border: 2px solid #646ce0;
        background: linear-gradient(180deg, #2d2f38 0%, #262830 100%);
        box-shadow: 0 12px 28px rgba(92, 104, 242, 0.20);
    }

    .small {
        color: var(--text-soft);
        font-size: 0.93rem;
        line-height: 1.42;
    }

    .stButton > button {
        border-radius: 999px !important;
        border: 1px solid var(--line-strong) !important;
        background: linear-gradient(180deg, #2a2c33 0%, #202228 100%) !important;
        color: var(--text-main) !important;
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.25);
        transition: all 0.2s ease;
        font-weight: 600;
        padding: 0.5rem 0.96rem !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) scale(1.01);
        border-color: #646973 !important;
        background: linear-gradient(180deg, #323540 0%, #272a33 100%) !important;
    }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, #8ea5ff 0%, #6a7df0 100%) !important;
    }

    [data-testid="stChatInput"] {
        background:
            linear-gradient(#2a2c33, #2a2c33) padding-box,
            linear-gradient(90deg, #6f85ff, #8ea5ff) border-box;
        border: 2px solid transparent;
        border-radius: 22px;
        box-shadow: var(--shadow-float);
        backdrop-filter: blur(8px);
        padding: 0.24rem;
        margin-top: 1.2rem;
        position: sticky;
        bottom: 0.78rem;
        z-index: 20;
    }

    [data-testid="stChatInput"] textarea {
        border-radius: 16px !important;
        padding-top: 0.4rem !important;
        padding-bottom: 0.4rem !important;
        color: var(--text-main) !important;
        background: #2a2c33 !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #98a0b2 !important;
        opacity: 1;
    }

    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 0.42rem 0.34rem;
        margin-bottom: 0.48rem;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] div {
        color: var(--text-main);
    }

    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
        margin-bottom: 0.34rem;
    }

    [data-testid="stExpander"] {
        border-radius: 18px;
        border: 1px solid var(--line-soft);
        background: linear-gradient(180deg, #2a2c33 0%, #23252b 100%);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.24);
        margin-bottom: 1.45rem;
    }

    [data-testid="stBottomBlockContainer"] {
        background: linear-gradient(180deg, rgba(31, 32, 35, 0.0) 0%, rgba(31, 32, 35, 0.82) 34%, rgba(31, 32, 35, 0.96) 100%);
        padding-top: 0.5rem;
    }

    [data-testid="stAppHeader"] {
        background: transparent;
        border: none;
    }

    .chat-active-pill {
        margin: 0.38rem 0 0.9rem;
        padding: 0.58rem 0.84rem;
        border-radius: 999px;
        border: 1px solid #4a4d58;
        background: linear-gradient(135deg, #2b2d34 0%, #22242a 100%);
        color: #cad0df;
        font-size: 0.84rem;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.24);
    }

    .section-gap {
        margin-top: 0.4rem;
        margin-bottom: 1.28rem;
    }

    .cmp-card {
        border: 1px solid var(--line-soft);
        border-radius: 18px;
        background: linear-gradient(180deg, #2a2c33 0%, #23252b 100%);
        box-shadow: var(--shadow-card);
        padding: 0.9rem 1rem;
        margin: 0.6rem 0;
    }

    .cmp-title {
        margin: 0 0 0.45rem;
        color: #d7dcee;
        font-weight: 700;
        font-size: 0.96rem;
    }

    .cmp-point {
        margin: 0.18rem 0;
        color: #b8becf;
        font-size: 0.93rem;
    }

    .mode-badge {
        display: inline-block;
        margin: 0.2rem 0 0.45rem;
        padding: 0.22rem 0.62rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        border: 1px solid #4a4d58;
        background: linear-gradient(135deg, #2b2d34 0%, #23262d 100%);
        color: #cfd5e6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_chats_from_disk() -> List[Dict[str, Any]]:
    if not os.path.exists(CHAT_STORE_FILE):
        return []
    try:
        with open(CHAT_STORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def save_chats_to_disk(chats: List[Dict[str, Any]]) -> None:
    try:
        with open(CHAT_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(chats, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def create_chat(title: str = "New chat") -> Dict[str, Any]:
    ts = now_iso()
    return {
        "id": str(uuid4()),
        "title": title,
        "pinned": False,
        "created_at": ts,
        "updated_at": ts,
        "messages": [],
        "conversation_state": {
            "current_intent": "chat",
            "stage": "initial",
            "collected_data": {
                "budget": None,
                "category": None,
                "use_case": None,
                "base_query": "",
            },
        },
    }


def resolve_api_key() -> Optional[str]:
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        return None


def choose_supported_model_name() -> Optional[str]:
    preferred = [
        "models/gemini-1.5-flash",
        "models/gemini-1.5-flash-latest",
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
        "models/gemini-flash-latest",
    ]
    try:
        available = [
            m.name
            for m in genai.list_models()
            if "generateContent" in getattr(m, "supported_generation_methods", [])
        ]
        for model_name in preferred:
            if model_name in available:
                return model_name
        return available[0] if available else None
    except Exception as e:
        print(f"[WARN][Gemini] Could not list models: {type(e).__name__}: {e}")
        # Last-resort static fallback if list_models is unavailable.
        return "models/gemini-2.5-flash"


def configure_model() -> Any:
    api_key = resolve_api_key()
    print(f"[DEBUG][Gemini] GEMINI_API_KEY present: {bool(api_key)}")
    if not api_key:
        return None
    try:
        # Keep both aliases set so underlying SDK lookup always succeeds.
        os.environ["GEMINI_API_KEY"] = api_key
        os.environ["GOOGLE_API_KEY"] = api_key
        genai.configure(api_key=api_key)
        model_name = choose_supported_model_name()
        if not model_name:
            print("[ERROR][Gemini] No supported generateContent model found for this key")
            return None
        print(f"[DEBUG][Gemini] Using model: {model_name}")
        st.session_state.active_model_name = model_name
        return genai.GenerativeModel(model_name)
    except Exception as e:
        print(f"[ERROR][Gemini] Failed to configure model: {type(e).__name__}: {e}")
        return None


def safe_generate_response(model: Any, prompt: str, generation_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    key_present = bool(resolve_api_key())
    print(f"[DEBUG][Gemini] key_present={key_present}")
    print(f"[DEBUG][Gemini] prompt_preview={prompt[:240].replace(chr(10), ' ')}")

    if not key_present:
        return {"ok": False, "text": None, "error": "API key missing"}

    if model is None:
        return {"ok": False, "text": None, "error": "Model not initialized"}

    try:
        response = model.generate_content(prompt, generation_config=generation_config or {"temperature": 0.3})
        text = response.text if hasattr(response, "text") else None
        if text and text.strip():
            print(f"[DEBUG][Gemini] response_preview={text[:240].replace(chr(10), ' ')}")
            st.session_state.last_api_error = None
            return {"ok": True, "text": text, "error": None}

        print("[WARN][Gemini] Empty response on first attempt, retrying once")
        retry_response = model.generate_content(prompt, generation_config=generation_config or {"temperature": 0.3})
        retry_text = retry_response.text if hasattr(retry_response, "text") else None
        if retry_text and retry_text.strip():
            print(f"[DEBUG][Gemini] retry_response_preview={retry_text[:240].replace(chr(10), ' ')}")
            st.session_state.last_api_error = None
            return {"ok": True, "text": retry_text, "error": None}

        error = "Empty response after retry"
        st.session_state.last_api_error = error
        print(f"[ERROR][Gemini] {error}")
        return {"ok": False, "text": None, "error": error}
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        st.session_state.last_api_error = error
        print(f"[ERROR][Gemini] {error}")
        return {"ok": False, "text": None, "error": error}


def local_chat_fallback(query: str) -> str:
    constraints = extract_constraints(query)
    filtered = filter_products(products, constraints)
    pool = filtered if filtered else closest_products(products, constraints, limit=3)
    if not pool:
        return "AI service temporarily unavailable. I currently cannot find suitable products in the catalog."

    names = ", ".join([f"{p['name']} (₹{p['price']})" for p in pool[:3]])
    return (
        "AI service temporarily unavailable. Showing best available results from the catalog: "
        f"{names}. You can refine by budget, use-case, or style."
    )


def ensure_state() -> None:
    if "chats" not in st.session_state:
        chats = load_chats_from_disk()
        if not chats:
            chats = [create_chat()]
            save_chats_to_disk(chats)
        st.session_state.chats = chats

    if "active_chat_id" not in st.session_state:
        st.session_state.active_chat_id = st.session_state.chats[0]["id"]

    if "saved_items" not in st.session_state:
        st.session_state.saved_items = []

    if "queued_user_query" not in st.session_state:
        st.session_state.queued_user_query = None

    if "last_recommendation_names" not in st.session_state:
        st.session_state.last_recommendation_names = []

    if "current_intent" not in st.session_state:
        st.session_state.current_intent = "chat"

    if "conversation_stage" not in st.session_state:
        st.session_state.conversation_stage = "initial"

    if "collected_data" not in st.session_state:
        st.session_state.collected_data = {"budget": None, "category": None, "use_case": None, "base_query": ""}

    if "last_api_error" not in st.session_state:
        st.session_state.last_api_error = None

    if "flow_state" not in st.session_state:
        st.session_state.flow_state = {
            "intent": "unknown",
            "stage": "initial",
            "product_type": None,
            "budget": None,
        }


def sync_flow_state(chat: Dict[str, Any]) -> None:
    state = chat.get("conversation_state", {})
    collected = state.get("collected_data", {})
    st.session_state.flow_state = {
        "intent": "product_query" if state.get("current_intent") == "recommendation" else state.get("current_intent", "unknown"),
        "stage": state.get("stage", "initial"),
        "product_type": collected.get("product_type") or collected.get("category") or extract_product_type(collected.get("base_query", "") or ""),
        "budget": collected.get("budget"),
    }


def find_chat(chat_id: str) -> Optional[Dict[str, Any]]:
    for chat in st.session_state.chats:
        if chat["id"] == chat_id:
            return chat
    return None


def persist_state() -> None:
    save_chats_to_disk(st.session_state.chats)


def touch_chat(chat: Dict[str, Any]) -> None:
    chat["updated_at"] = now_iso()


def auto_title_chat(chat: Dict[str, Any], user_text: str) -> None:
    if chat["title"] != "New chat":
        return
    title = user_text.strip().replace("\n", " ")
    title = title[:45] + ("..." if len(title) > 45 else "")
    chat["title"] = title if title else "Shopping help"


def add_message(
    chat: Dict[str, Any],
    role: str,
    msg_type: str,
    text: str = "",
    data: Any = None,
    mode: str = "",
) -> None:
    chat["messages"].append(
        {
            "role": role,
            "type": msg_type,
            "text": text,
            "data": data,
            "mode": mode,
            "created_at": now_iso(),
        }
    )
    touch_chat(chat)
    persist_state()


def detect_intent(query: str) -> str:
    q = query.lower().strip()
    if any(k in q for k in ["compare", "vs", "versus", "difference between"]):
        return "comparison"
    if any(k in q for k in ["suggest", "recommend", "find", "under", "budget", "best", "cheaper", "premium"]):
        return "recommendation"
    if re.search(r"(?:under|below|within|less than)\s*(?:₹|rs\.?|inr)?\s*(\d+)", q):
        return "recommendation"
    return "chat"


def classify_query(query: str, model: Any = None, chat: Optional[Dict[str, Any]] = None) -> str:
    q = query.lower().strip()

    if chat:
        state = chat.get("conversation_state", {})
        if state.get("stage") != "initial":
            print(f"[DEBUG][Router] Skipping classification because flow is in progress: stage={state.get('stage')}")
            return "product_query"

    if any(k in q for k in ["compare", "vs", "versus", "difference between"]):
        return "comparison"

    category_hits = sum(1 for c in KNOWN_CATEGORIES if c in q)
    tag_hits = sum(1 for t in KNOWN_TAGS if t in q)
    product_hits = sum(1 for p in products if p["name"].lower() in q)

    shopping_terms = [
        "buy", "recommend", "suggest", "under", "budget", "best", "product", "catalog",
        "stationery", "planner", "journal", "notebook", "pen", "gift",
    ]
    general_terms = [
        "what is", "how to", "why", "explain", "tips", "brands", "career", "code", "health",
        "travel", "news", "recipe", "math", "history",
    ]

    has_shopping_signal = any(k in q for k in shopping_terms)
    has_general_signal = any(k in q for k in general_terms)

    if product_hits > 0 or category_hits > 0 or tag_hits > 0:
        return "product_query"

    if has_shopping_signal and not has_general_signal:
        return "product_query"

    if has_general_signal and not has_shopping_signal:
        return "general_query"

    if model is not None:
        classifier_prompt = f"""
Classify the following user query into exactly one label:
- product_query
- general_query
- comparison
- unknown

Return only the label.

Query: {query}
""".strip()
        result = safe_generate_response(model, classifier_prompt, generation_config={"temperature": 0})
        if result.get("ok") and result.get("text"):
            label = result.get("text", "").strip().lower()
            if label in ["product_query", "general_query", "comparison", "unknown"]:
                return label

    return "unknown"


def reset_product_conversation_state(chat: Dict[str, Any]) -> None:
    chat["conversation_state"] = {
        "current_intent": "chat",
        "stage": "initial",
        "collected_data": {
            "budget": None,
            "category": None,
            "use_case": None,
            "base_query": "",
        },
    }
    touch_chat(chat)
    persist_state()


def extract_budget(text: str) -> Optional[int]:
    q = text.lower().strip()
    strict = re.search(r"(?:under|below|within|less than|budget)\s*(?:₹|rs\.?|inr)?\s*(\d{2,6})", q)
    if strict:
        return int(strict.group(1))

    # Accept plain numeric follow-ups while collecting budget.
    loose = re.search(r"\b(\d{2,6})\b", q)
    if loose:
        return int(loose.group(1))
    return None


def extract_use_case(text: str) -> Optional[str]:
    q = text.lower().strip()
    mapping = {
        "journaling": "journal",
        "journal": "journal",
        "planning": "planner",
        "planner": "planner",
        "gifting": "gifting",
        "gift": "gifting",
        "study": "study",
        "office": "office",
        "creative": "creative",
        "work": "office",
    }
    for key, normalized in mapping.items():
        if key in q:
            return normalized
    return None


def extract_category(text: str) -> Optional[str]:
    q = text.lower().strip()
    for category in KNOWN_CATEGORIES:
        if category in q:
            return category
    if any(k in q for k in ["notebook", "journal", "planner", "stationery"]):
        return "stationery"
    return None


def extract_product_type(text: str) -> Optional[str]:
    q = text.lower().strip()
    product_terms = [
        "pen", "notebook", "journal", "planner", "bookmark", "sticky notes", "washi", "organizer",
        "pouch", "calendar", "cards", "stationery", "desk",
    ]
    for term in product_terms:
        if term in q:
            return term
    return None


def looks_like_product_need(text: str) -> bool:
    q = text.lower()
    product_words = ["notebook", "journal", "planner", "gift", "stationery", "pen", "desk"]
    intent_words = ["want", "need", "looking for", "help me choose", "buy"]
    return any(w in q for w in product_words) and any(iw in q for iw in intent_words)


def is_ready_for_recommendation(collected_data: Dict[str, Any]) -> bool:
    has_budget = bool(collected_data.get("budget"))
    has_specific_target = bool(collected_data.get("use_case") or collected_data.get("product_type") or collected_data.get("category"))
    return has_budget and has_specific_target


def build_refined_query(collected_data: Dict[str, Any], latest_query: str) -> str:
    base = collected_data.get("base_query") or latest_query
    parts = [base]
    if collected_data.get("budget"):
        parts.append(f"under ₹{collected_data['budget']}")
    if collected_data.get("use_case"):
        parts.append(f"for {collected_data['use_case']}")
    if collected_data.get("category"):
        parts.append(f"in {collected_data['category']}")
    return " ".join(parts)


def update_conversation_state(chat: Dict[str, Any], user_query: str) -> Dict[str, Any]:
    state = chat.get("conversation_state")
    if not state:
        chat["conversation_state"] = {
            "current_intent": "chat",
            "stage": "initial",
            "collected_data": {"budget": None, "category": None, "use_case": None, "product_type": None, "base_query": ""},
        }
        state = chat["conversation_state"]

    detected_intent = detect_intent(user_query)
    collected = state["collected_data"]

    parsed_budget = extract_budget(user_query)
    parsed_use_case = extract_use_case(user_query)
    parsed_category = extract_category(user_query)
    parsed_product_type = extract_product_type(user_query)

    if parsed_budget is not None:
        collected["budget"] = parsed_budget
    if parsed_use_case is not None:
        collected["use_case"] = parsed_use_case
    if parsed_category is not None:
        collected["category"] = parsed_category
    if parsed_product_type is not None:
        collected["product_type"] = parsed_product_type

    if state["stage"] == "initial" and not collected.get("base_query"):
        collected["base_query"] = user_query

    # Follow-up path: continue collecting data instead of starting a new intent branch.
    if state["current_intent"] == "recommendation" and state["stage"] in ["collecting_budget", "collecting_use_case"]:
        print(f"[DEBUG][Flow] intent={state['current_intent']} stage={state['stage']} collected={collected}")
        if state["stage"] == "collecting_budget" and collected.get("budget") is None:
            return {"status": "ask", "text": "What is your budget in rupees? (example: under 500)"}

        if state["stage"] == "collecting_budget" and collected.get("budget") is not None:
            # If we already have a specific product/category target, recommendation can proceed.
            if collected.get("product_type") or collected.get("category"):
                state["stage"] = "ready_for_recommendation"
                effective_query = build_refined_query(collected, user_query)
                print(f"[DEBUG][Flow] intent={state['current_intent']} stage={state['stage']} collected={collected}")
                return {"status": "ready", "intent": "recommendation", "effective_query": effective_query}
            state["stage"] = "collecting_use_case"

        if state["stage"] == "collecting_use_case" and collected.get("use_case") is None:
            return {"status": "ask", "text": "Got it. What is your use-case: journal, planner, or gifting?"}

        if is_ready_for_recommendation(collected):
            state["stage"] = "ready_for_recommendation"
            effective_query = build_refined_query(collected, user_query)
            print(f"[DEBUG][Flow] intent={state['current_intent']} stage={state['stage']} collected={collected}")
            return {"status": "ready", "intent": "recommendation", "effective_query": effective_query}

        print(f"[DEBUG][Flow] intent={state['current_intent']} stage={state['stage']} collected={collected}")
        return {"status": "ask", "text": "I didn't understand, can you clarify your budget or use-case?"}

    if detected_intent == "comparison":
        state["current_intent"] = "comparison"
        state["stage"] = "initial"
        print(f"[DEBUG][Flow] intent={state['current_intent']} stage={state['stage']} collected={collected}")
        return {"status": "ready", "intent": "comparison", "effective_query": user_query}

    if detected_intent == "recommendation" or looks_like_product_need(user_query):
        state["current_intent"] = "recommendation"
        if not collected.get("base_query"):
            collected["base_query"] = user_query

        if collected.get("budget") is None:
            state["stage"] = "collecting_budget"
            print(f"[DEBUG][Flow] intent={state['current_intent']} stage={state['stage']} collected={collected}")
            return {"status": "ask", "text": "Great, I can help with that. What is your budget?"}

        if collected.get("use_case") is None:
            if collected.get("product_type") or collected.get("category"):
                state["stage"] = "ready_for_recommendation"
                effective_query = build_refined_query(collected, user_query)
                print(f"[DEBUG][Flow] intent={state['current_intent']} stage={state['stage']} collected={collected}")
                return {"status": "ready", "intent": "recommendation", "effective_query": effective_query}
            state["stage"] = "collecting_use_case"
            print(f"[DEBUG][Flow] intent={state['current_intent']} stage={state['stage']} collected={collected}")
            return {"status": "ask", "text": "Nice. Is this for journaling, planning, or gifting?"}

        state["stage"] = "ready_for_recommendation"
        effective_query = build_refined_query(collected, user_query)
        print(f"[DEBUG][Flow] intent={state['current_intent']} stage={state['stage']} collected={collected}")
        return {"status": "ready", "intent": "recommendation", "effective_query": effective_query}

    state["current_intent"] = "chat"
    state["stage"] = "initial"
    print(f"[DEBUG][Flow] intent={state['current_intent']} stage={state['stage']} collected={collected}")
    return {"status": "ready", "intent": "chat", "effective_query": user_query}


def extract_constraints(query: str) -> Dict[str, Any]:
    q = query.lower()
    constraints: Dict[str, Any] = {"max_price": None, "category": None, "tags": [], "premium": False}

    price_match = re.search(r"(?:under|below|within|less than)\s*(?:₹|rs\.?|inr)?\s*(\d+)", q)
    if price_match:
        constraints["max_price"] = int(price_match.group(1))

    for category in KNOWN_CATEGORIES:
        if category in q:
            constraints["category"] = category
            break

    tags = [tag for tag in KNOWN_TAGS if tag in q]
    if "aesthetic" in q and "aesthetic" not in tags:
        tags.append("aesthetic")
    if "minimal" in q and "minimal" not in tags:
        tags.append("minimal")

    constraints["premium"] = any(x in q for x in ["premium", "higher-end", "luxury"]) 
    constraints["tags"] = sorted(set(tags))
    return constraints


def filter_products(catalog: List[Dict[str, Any]], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
    pool = []
    for item in catalog:
        if constraints.get("max_price") is not None and item["price"] > constraints["max_price"]:
            continue
        if constraints.get("category") and item["category"].lower() != constraints["category"]:
            continue
        required_tags = constraints.get("tags", [])
        item_tags = [t.lower() for t in item["tags"]]
        if required_tags and not all(tag in item_tags for tag in required_tags):
            continue
        pool.append(item)

    if constraints.get("premium") and pool:
        return sorted(pool, key=lambda x: x["price"], reverse=True)

    return pool


def closest_products(catalog: List[Dict[str, Any]], constraints: Dict[str, Any], limit: int = 4) -> List[Dict[str, Any]]:
    ranked = []
    target_price = constraints.get("max_price")
    for item in catalog:
        score = 0.0
        if constraints.get("category") and item["category"].lower() == constraints["category"]:
            score += 2.0
        tags = [t.lower() for t in item["tags"]]
        score += sum(1.0 for t in constraints.get("tags", []) if t in tags)
        if target_price is not None:
            score += max(0.0, 2.0 - abs(item["price"] - target_price) / 300.0)
        ranked.append((score, item))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in ranked[:limit]]


def safe_json_parse(raw: str) -> Dict[str, Any]:
    txt = raw.strip()
    if txt.startswith("```"):
        txt = re.sub(r"^```(?:json)?", "", txt).strip()
        txt = re.sub(r"```$", "", txt).strip()
    try:
        return json.loads(txt)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", txt)
        if match:
            return json.loads(match.group(0))
        raise


def generate_candidates(model: Any, prompt: str, runs: int = 3) -> List[Dict[str, Any]]:
    temps = [0.2, 0.4, 0.6]
    out: List[Dict[str, Any]] = []
    for i in range(runs):
        result = safe_generate_response(model, prompt, generation_config={"temperature": temps[i % len(temps)]})
        if not result.get("ok"):
            continue
        try:
            out.append(safe_json_parse(result.get("text", "")))
        except Exception as e:
            print(f"[WARN][Gemini] Failed to parse JSON candidate: {type(e).__name__}: {e}")
            continue
    return out


def get_actionable_recommendation(model: Any, user_query: str, history: List[Dict[str, str]], filtered: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    payload = json.dumps(filtered, indent=2)
    hist = json.dumps(history[-10:], indent=2)

    prompt = f"""
{PRODUCT_SYSTEM_PROMPT}

Return JSON only. No markdown. No extra text.
Use ONLY products provided in the list.
Keep chain-of-thought hidden.

Conversation history:
{hist}

User query:
{user_query}

Products:
{payload}

Required schema:
{{
  "recommendations": [
    {{
      "name": "",
      "price": "",
      "reason": "",
      "match_score": "",
      "why_good_for_you": "",
      "best_use_case": "",
      "tradeoffs": "",
      "next_action": "",
      "score_explanation": ""
    }}
  ]
}}
""".strip()

    candidates = generate_candidates(model, prompt, runs=3)
    if not candidates:
        return []

    allowed = {p["name"].lower(): p for p in filtered}

    def score_candidate(c: Dict[str, Any]) -> float:
        recs = c.get("recommendations", [])
        if not isinstance(recs, list):
            return -1.0
        score = 0.0
        for rec in recs:
            name = str(rec.get("name", "")).strip().lower()
            if name in allowed:
                score += 2.0
            raw = str(rec.get("match_score", "")).replace("%", "").strip()
            try:
                score += float(raw) / 100.0
            except Exception:
                pass
        return score

    chosen = sorted(candidates, key=score_candidate, reverse=True)[0]
    cleaned: List[Dict[str, Any]] = []
    for rec in chosen.get("recommendations", []):
        nm = str(rec.get("name", "")).strip()
        base = allowed.get(nm.lower())
        if not base:
            continue
        cleaned.append(
            {
                "name": base["name"],
                "price": base["price"],
                "reason": rec.get("reason", "Strong alignment with your request."),
                "match_score": rec.get("match_score", "80"),
                "why_good_for_you": rec.get("why_good_for_you", "Matches your core preferences and budget intent."),
                "best_use_case": rec.get("best_use_case", "General daily use."),
                "tradeoffs": rec.get("tradeoffs", "May not fit every edge case."),
                "next_action": rec.get("next_action", "Shortlist this option and compare it with one alternative."),
                "score_explanation": rec.get("score_explanation", "Score based on budget fit, tags, and use-case relevance."),
            }
        )

    return cleaned


def generate_followup_actions(recommendations: List[Dict[str, Any]]) -> List[str]:
    actions = [
        "Compare top 2",
        "Show cheaper options",
        "Show premium alternatives",
        "Explain differences",
    ]
    if len(recommendations) < 2:
        return ["Show cheaper options", "Show premium alternatives"]
    return actions


def extract_comparison_targets(query: str, catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    q = query.lower()
    found = [p for p in catalog if p["name"].lower() in q]
    if len(found) >= 2:
        return found[:2]

    tokens = re.sub(r"\bcompare\b|\bwith\b|\bvs\b|\bversus\b", "|", q)
    chunks = [x.strip() for x in tokens.split("|") if x.strip()]
    for chunk in chunks:
        for p in catalog:
            if any(w in p["name"].lower() for w in chunk.split()):
                if p not in found:
                    found.append(p)
                break
        if len(found) >= 2:
            break
    return found[:2]


def compare_products_with_ai(model: Any, query: str, history: List[Dict[str, str]], a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    hist = json.dumps(history[-10:], indent=2)
    payload = json.dumps([a, b], indent=2)
    prompt = f"""
{PRODUCT_SYSTEM_PROMPT}

Return valid JSON only.
Do not mention products beyond the two provided.
Keep chain-of-thought hidden.

Conversation history:
{hist}

User query:
{query}

Products:
{payload}

Required schema:
{{
  "pros_product1": [],
  "pros_product2": [],
  "cons_product1": [],
  "cons_product2": [],
  "final_verdict": "",
  "best_use_case": "",
  "explain_differences": ""
}}
""".strip()

    candidates = generate_candidates(model, prompt, runs=3)
    if not candidates:
        return {}

    required = ["pros_product1", "pros_product2", "cons_product1", "cons_product2", "final_verdict", "best_use_case"]
    return sorted(candidates, key=lambda c: sum(1 for k in required if k in c), reverse=True)[0]


def chat_with_context(model: Any, query: str, history: List[Dict[str, str]]) -> str:
    hist = json.dumps(history[-12:], indent=2)
    catalog = json.dumps(products, indent=2)
    prompt = f"""
{GENERAL_SYSTEM_PROMPT}

Answer as a practical decision assistant, not just a recommender.
Only reference products from provided catalog.
If no exact answer exists, ask one clarifying question.

Conversation history:
{hist}

Catalog:
{catalog}

User:
{query}
""".strip()
    result = safe_generate_response(model, prompt, generation_config={"temperature": 0.35})
    if result.get("ok") and result.get("text"):
        return str(result.get("text"))
    return local_chat_fallback(query)


def render_saved_items() -> None:
    with st.expander("Saved Items ❤️", expanded=False):
        if not st.session_state.saved_items:
            st.caption("No saved products yet.")
            return
        for i, name in enumerate(st.session_state.saved_items):
            p = PRODUCT_BY_NAME.get(name)
            if not p:
                continue
            c1, c2 = st.columns([5, 1])
            with c1:
                st.write(f"{p['name']} - ₹{p['price']} ({p['category']})")
            with c2:
                if st.button("Remove", key=f"remove_saved_{i}_{name}"):
                    st.session_state.saved_items = [x for x in st.session_state.saved_items if x != name]
                    st.rerun()


def score_float(v: Any) -> float:
    try:
        return float(str(v).replace("%", "").strip())
    except Exception:
        return 0.0


def render_points(points: Any) -> str:
    if not isinstance(points, list) or not points:
        return "<div class='cmp-point'>- Not available</div>"
    return "".join([f"<div class='cmp-point'>- {str(p)}</div>" for p in points])


def queue_followup(label: str, recommendations: List[Dict[str, Any]]) -> None:
    if label == "Compare top 2" and len(recommendations) >= 2:
        st.session_state.queued_user_query = f"Compare {recommendations[0]['name']} and {recommendations[1]['name']}"
    elif label == "Show cheaper options":
        prices = sorted([r["price"] for r in recommendations])
        target = prices[0] if prices else 400
        st.session_state.queued_user_query = f"Suggest cheaper options under ₹{max(100, target - 100)}"
    elif label == "Show premium alternatives":
        prices = sorted([r["price"] for r in recommendations])
        target = prices[-1] if prices else 600
        st.session_state.queued_user_query = f"Show premium alternatives above ₹{target}"
    elif label == "Explain differences":
        if len(recommendations) >= 2:
            st.session_state.queued_user_query = f"Explain differences between {recommendations[0]['name']} and {recommendations[1]['name']}"
        else:
            st.session_state.queued_user_query = "Explain differences in features and use-cases"
    st.rerun()


def render_recommendation_message(chat_id: str, msg_index: int, msg: Dict[str, Any]) -> None:
    recs = msg.get("data", {}).get("recommendations", [])
    if msg.get("text"):
        st.write(msg["text"])

    if not recs:
        st.info("No recommendations to display.")
        return

    sorted_recs = sorted(recs, key=lambda r: score_float(r.get("match_score", "0")), reverse=True)
    st.session_state.last_recommendation_names = [r["name"] for r in sorted_recs]

    for i, rec in enumerate(sorted_recs):
        best = i == 0
        best_label = "🏆 BEST MATCH" if best else ""
        css_class = "card best" if best else "card"

        st.markdown(
            f"""
            <div class=\"{css_class}\">
                <h4 style=\"margin:0;color:#5f4437;\">{rec['name']} {best_label}</h4>
                <div class=\"small\">Price: ₹{rec['price']} | Match: {rec.get('match_score', '0')}%</div>
                <p><strong>✅ Why this is good for you:</strong> {rec.get('why_good_for_you', rec.get('reason', ''))}</p>
                <p><strong>🎯 Best for use-case:</strong> {rec.get('best_use_case', 'General daily use')}</p>
                <p><strong>⚖️ Trade-offs:</strong> {rec.get('tradeoffs', 'May not be ideal for all preferences')}</p>
                <p><strong>🛒 What you should do next:</strong> {rec.get('next_action', 'Shortlist and compare with one alternative')}</p>
                <p class=\"small\"><strong>Score reasoning:</strong> {rec.get('score_explanation', 'Based on budget fit, category fit, and tag alignment.')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        score = int(max(0, min(100, score_float(rec.get("match_score", "0")))))
        st.progress(score / 100.0, text=f"Match Score: {score}%")

        alt = None
        for cand in sorted_recs:
            if cand["name"] != rec["name"]:
                alt = cand["name"]
                break

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Save ❤️", key=f"save_{chat_id}_{msg_index}_{i}_{rec['name']}"):
                if rec["name"] not in st.session_state.saved_items:
                    st.session_state.saved_items.append(rec["name"])
                st.success(f"Saved: {rec['name']}")
        with c2:
            if st.button("Compare with another", key=f"cmp_{chat_id}_{msg_index}_{i}_{rec['name']}"):
                if alt:
                    st.session_state.queued_user_query = f"Compare {rec['name']} and {alt}"
                else:
                    st.session_state.queued_user_query = f"Compare {rec['name']} with another product"
                st.rerun()

    followups = msg.get("data", {}).get("followups", [])
    if followups:
        st.markdown("**Try next:**")
        cols = st.columns(2)
        for i, action in enumerate(followups):
            with cols[i % 2]:
                if st.button(action, key=f"fu_{chat_id}_{msg_index}_{i}_{action}"):
                    queue_followup(action, sorted_recs)


def render_sidebar() -> None:
    st.sidebar.title("Chats")

    if st.sidebar.button("+ New chat", use_container_width=True):
        chat = create_chat()
        st.session_state.chats.insert(0, chat)
        st.session_state.active_chat_id = chat["id"]
        persist_state()
        st.rerun()

    search = st.sidebar.text_input("Search chats", key="sidebar_chat_search", placeholder="Type to filter chats")

    active = find_chat(st.session_state.active_chat_id)
    if active:
        st.sidebar.markdown(
            f"<div class='chat-active-pill'>Active chat: {active['title']}</div>",
            unsafe_allow_html=True,
        )

    chats = st.session_state.chats
    filtered = [c for c in chats if search.lower() in c["title"].lower()] if search else chats[:]
    filtered.sort(key=lambda x: (not x.get("pinned", False), x.get("updated_at", "")), reverse=False)

    for chat in filtered:
        is_active = chat["id"] == st.session_state.active_chat_id
        title = ("📌 " if chat.get("pinned") else "") + chat["title"]

        c1, c2, c3 = st.sidebar.columns([6, 1, 1])
        with c1:
            if st.button(("▶ " if is_active else "") + title, key=f"open_{chat['id']}", use_container_width=True):
                st.session_state.active_chat_id = chat["id"]
                st.rerun()
        with c2:
            if st.button("📌" if not chat.get("pinned") else "📍", key=f"pin_{chat['id']}"):
                chat["pinned"] = not chat.get("pinned", False)
                touch_chat(chat)
                persist_state()
                st.rerun()
        with c3:
            if st.button("🗑", key=f"del_{chat['id']}"):
                st.session_state.chats = [c for c in st.session_state.chats if c["id"] != chat["id"]]
                if not st.session_state.chats:
                    st.session_state.chats = [create_chat()]
                if st.session_state.active_chat_id == chat["id"]:
                    st.session_state.active_chat_id = st.session_state.chats[0]["id"]
                persist_state()
                st.rerun()


def handle_product_query(chat: Dict[str, Any], model: Any, user_query: str, forced_intent: Optional[str] = None) -> None:
    flow_result = update_conversation_state(chat, user_query)
    touch_chat(chat)
    persist_state()
    sync_flow_state(chat)

    if flow_result.get("status") == "ask":
        add_message(chat, "assistant", "text", text=flow_result.get("text", "I didn't understand, can you clarify?"), mode="product")
        return

    intent = forced_intent or flow_result.get("intent", "recommendation")
    effective_query = flow_result.get("effective_query", user_query)

    state = chat.get("conversation_state", {})
    st.session_state.current_intent = state.get("current_intent", "chat")
    st.session_state.conversation_stage = state.get("stage", "initial")
    st.session_state.collected_data = state.get(
        "collected_data",
        {"budget": None, "category": None, "use_case": None, "base_query": ""},
    )

    history = [{"role": m["role"], "content": m.get("text", m.get("type", ""))} for m in chat["messages"]]

    if model is None:
        constraints = extract_constraints(effective_query)
        fallback = closest_products(products, constraints, limit=3)
        recs = [
            {
                "name": p["name"],
                "price": p["price"],
                "reason": "Closest available match from the catalog.",
                "match_score": "70",
                "why_good_for_you": "Closest available fit while AI service is unavailable.",
                "best_use_case": "Quick shortlist until AI service is back.",
                "tradeoffs": "Personalization is limited without AI ranking.",
                "next_action": "Refine budget/use-case and retry when AI is available.",
                "score_explanation": "Based on rule-based category, tag, and price proximity.",
            }
            for p in fallback
        ]
        add_message(
            chat,
            "assistant",
            "recommendation",
            text="AI service temporarily unavailable. Showing best available results.",
            data={"recommendations": recs, "followups": generate_followup_actions(recs)},
            mode="product",
        )
        return

    if intent == "comparison":
        targets = extract_comparison_targets(effective_query, products)
        if len(targets) < 2 and len(st.session_state.last_recommendation_names) >= 2:
            a = PRODUCT_BY_NAME.get(st.session_state.last_recommendation_names[0])
            b = PRODUCT_BY_NAME.get(st.session_state.last_recommendation_names[1])
            if a and b:
                targets = [a, b]

        if len(targets) < 2:
            add_message(
                chat,
                "assistant",
                "text",
                text="Please mention two product names to compare, for example: Compare Soft Linen Journal and Sakura Weekly Planner.",
                mode="product",
            )
            return

        cmp_data = compare_products_with_ai(model, effective_query, history, targets[0], targets[1])
        if not cmp_data:
            cmp_data = {
                "pros_product1": ["Good fit for core usage."],
                "pros_product2": ["Strong alternative profile."],
                "cons_product1": ["May not fit all preferences."],
                "cons_product2": ["May be less budget-friendly."],
                "final_verdict": "Pick based on your top priority: budget, look, or features.",
                "best_use_case": "Best choice depends on whether you value practicality or aesthetics first.",
                "explain_differences": "One option is better for style, the other for utility.",
            }
        add_message(
            chat,
            "assistant",
            "comparison",
            text=f"Comparison: {targets[0]['name']} vs {targets[1]['name']}",
            data=cmp_data,
            mode="product",
        )
        return

    constraints = extract_constraints(effective_query)
    filtered = filter_products(products, constraints)

    no_exact = False
    pool = filtered
    clarifying_question = ""
    if not filtered:
        no_exact = True
        pool = closest_products(products, constraints, limit=4)
        clarifying_question = "I could not find an exact match. Do you want to relax budget, category, or style preferences?"

    recs = get_actionable_recommendation(model, effective_query, history, pool)
    if not recs:
        fallback = closest_products(products, constraints, limit=3)
        recs = [
            {
                "name": p["name"],
                "price": p["price"],
                "reason": "Closest available match from the catalog.",
                "match_score": "72",
                "why_good_for_you": "Closest fit based on your current constraints.",
                "best_use_case": "Use when you want a nearby option without changing many preferences.",
                "tradeoffs": "May miss one or more specific constraints.",
                "next_action": "Consider adjusting budget or one tag to improve precision.",
                "score_explanation": "Calculated from category, tag overlap, and price proximity.",
            }
            for p in fallback
        ]
        st.session_state.last_api_error = st.session_state.get("last_api_error") or "AI response unavailable"

    followups = generate_followup_actions(recs)
    note = "Here are actionable picks for your decision."
    if no_exact:
        note = "No exact match found. I am showing closest alternatives. " + clarifying_question
    if st.session_state.get("last_api_error"):
        note = "AI service temporarily unavailable. Showing best available results."

    add_message(
        chat,
        "assistant",
        "recommendation",
        text=note,
        data={"recommendations": recs, "followups": followups},
        mode="product",
    )

    if chat.get("conversation_state"):
        chat["conversation_state"]["stage"] = "initial"
        touch_chat(chat)
        persist_state()


def handle_general_query(chat: Dict[str, Any], model: Any, user_query: str) -> None:
    reset_product_conversation_state(chat)
    sync_flow_state(chat)
    history = [{"role": m["role"], "content": m.get("text", m.get("type", ""))} for m in chat["messages"]]

    apparel_terms = ["pants", "trouser", "jeans", "shirt", "tshirt", "clothes", "hoodie", "jacket", "shoes"]
    asked_outside_catalog = any(t in user_query.lower() for t in apparel_terms)

    if model is None:
        answer = (
            "AI service temporarily unavailable. Here is a quick general approach: define your budget, "
            "compare 2-3 options by quality/reviews/return policy, and choose based on your top priority."
        )
    else:
        answer = chat_with_context(model, user_query, history)
    if not answer or not answer.strip():
        answer = "I didn't understand, can you clarify?"

    if asked_outside_catalog:
        catalog_categories = ", ".join(KNOWN_CATEGORIES)
        answer = (
            "I do not have clothing products in your catalog right now. "
            + answer
            + f" If you want catalog-backed recommendations, I can help with these categories: {catalog_categories}."
        )

    add_message(chat, "assistant", "text", text=answer, mode="general")


def route_query(chat: Dict[str, Any], model: Any, user_query: str) -> None:
    state = chat.get("conversation_state", {})
    stage = state.get("stage", "initial")
    current_intent = state.get("current_intent", "chat")

    # Lock product mode while collecting multi-step inputs.
    if current_intent == "recommendation" and stage in ["collecting_budget", "collecting_use_case"]:
        print(f"[DEBUG][Router] mode lock active stage={stage}; skipping classifier for query={user_query}")
        handle_product_query(chat, model, user_query)
        return

    classification = classify_query(user_query, model=model, chat=chat)
    print(f"[DEBUG][Router] classification={classification} query={user_query}")

    if classification == "comparison":
        handle_product_query(chat, model, user_query, forced_intent="comparison")
        return

    if classification == "product_query":
        handle_product_query(chat, model, user_query)
        return

    if classification == "general_query":
        handle_general_query(chat, model, user_query)
        return

    # Unknown: ask one clarifying question while still being useful.
    add_message(
        chat,
        "assistant",
        "text",
        text="I can help in two modes: product catalog assistant or general AI advice. Do you want product recommendations from your catalog, or general guidance?",
        mode="general",
    )


def process_user_query(chat: Dict[str, Any], model: Any, user_query: str) -> None:
    add_message(chat, "user", "text", text=user_query)
    auto_title_chat(chat, user_query)
    persist_state()
    sync_flow_state(chat)
    route_query(chat, model, user_query)


ensure_state()
render_sidebar()

with st.spinner("Starting assistant..."):
    model = configure_model()

st.markdown(
    """
    <div class="hero">
        <h1>AI Shopping Decision Assistant</h1>
        <p>Get actionable recommendations, trade-offs, and next steps to decide faster.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtle-note section-gap">
        Try: <strong>"I want a notebook"</strong>, <strong>"Suggest aesthetic stationery under ₹500"</strong>, or
        <strong>"Compare Soft Linen Journal and Sakura Weekly Planner"</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

if model is None:
    st.warning(
        "Gemini API key not detected. Set GEMINI_API_KEY (or GOOGLE_API_KEY) in the same terminal before running Streamlit, "
        "or add GEMINI_API_KEY in Streamlit secrets."
    )

render_saved_items()

active_chat = find_chat(st.session_state.active_chat_id)
if not active_chat:
    st.session_state.active_chat_id = st.session_state.chats[0]["id"]
    active_chat = find_chat(st.session_state.active_chat_id)

for i, msg in enumerate(active_chat["messages"]):
    with st.chat_message(msg["role"]):
        if msg.get("role") == "assistant" and msg.get("mode"):
            mode_text = "🛍️ Product Mode" if msg.get("mode") == "product" else "💬 General Mode"
            st.markdown(f"<div class='mode-badge'>{mode_text}</div>", unsafe_allow_html=True)
        if msg["type"] == "recommendation":
            render_recommendation_message(active_chat["id"], i, msg)
        elif msg["type"] == "comparison":
            st.markdown("### Comparison")
            st.write(msg.get("text", ""))
            data = msg.get("data", {})
            st.markdown(
                f"""
                <div class="cmp-card">
                    <div class="cmp-title">Pros (Product 1)</div>
                    {render_points(data.get('pros_product1', []))}
                </div>
                <div class="cmp-card">
                    <div class="cmp-title">Pros (Product 2)</div>
                    {render_points(data.get('pros_product2', []))}
                </div>
                <div class="cmp-card">
                    <div class="cmp-title">Cons (Product 1)</div>
                    {render_points(data.get('cons_product1', []))}
                </div>
                <div class="cmp-card">
                    <div class="cmp-title">Cons (Product 2)</div>
                    {render_points(data.get('cons_product2', []))}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("Final Verdict:", data.get("final_verdict", ""))
            st.write("Best Use Case:", data.get("best_use_case", ""))
            if data.get("explain_differences"):
                st.write("Explain Differences:", data.get("explain_differences"))
        else:
            st.write(msg.get("text", ""))

queued = st.session_state.queued_user_query
if queued:
    st.info(f"Running suggested action: {queued}")

user_input = st.chat_input("Ask for recommendations, comparisons, or decision help...")

submitted_query = None
if user_input is not None and user_input.strip():
    submitted_query = user_input.strip()
elif queued:
    submitted_query = queued

if submitted_query:
    st.session_state.queued_user_query = None
    with st.chat_message("user"):
        st.write(submitted_query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            process_user_query(active_chat, model, submitted_query)
    st.rerun()

if user_input is not None and not user_input.strip():
    st.info("Please enter a message to continue.")
