# AI-Powered Shopping Decision Assistant (Streamlit + Gemini)

**Live Demo:**
https://ai-shopping-decision-assistant-6fqgywnqfk3hid585jvrmr.streamlit.app/

A complete, deployment-ready **AI shopping assistant** built with Python, Streamlit, and Google Gemini API.

This system goes beyond a basic chatbot by combining **LLM reasoning with a structured product dataset** to deliver accurate, explainable, and non-hallucinated recommendations.

---

## What This Project Demonstrates

* Prompt engineering with strict anti-hallucination guardrails
* Context-aware chatbot with follow-up support
* Hybrid AI system (Python filtering + LLM reasoning)
* Explainable recommendations with best-match highlighting
* Decision-focused responses (not just suggestions)
* Streamlit Cloud deployment readiness

---

## Key Innovation: Hybrid AI + Dataset System

This assistant intelligently combines:

### Product Mode (Strict / Dataset-Grounded)

* Uses a curated **stationery dataset**
* Filters products using Python logic first
* Then uses Gemini for ranking and explanation
* Ensures:

  * ❌ No hallucinated products
  * ✅ Only real catalog items
  * ✅ Structured and explainable output

---

### 💬 General Mode (ChatGPT-like)

* Activated when query is outside dataset scope
* Uses Gemini’s general knowledge
* Provides:

  * Advice
  * Suggestions
  * Clarifications

---

### Smart Routing

| Query                        | Mode         |
| ---------------------------- | ------------ |
| “Notebook under ₹500”        | Product Mode |
| “Best clothing brands”       | General Mode |
| “Compare planner vs journal” | Product Mode |

---

## 🚫 Hallucination Handling (CRITICAL FEATURE)

A major issue with LLMs is hallucination (fake or incorrect outputs).

### ✅ This system prevents hallucination by:

* Restricting product recommendations to a **fixed stationery dataset**
* Separating:

  * Product reasoning (dataset-based)
  * General reasoning (LLM-based)

---

### Example

**User:** “I want pants”
**System:**

* ❌ Does NOT generate fake products
* ✅ Responds:

  * “I don’t have pants in my catalog”
  * * Provides fallback guidance using general AI

---

## Dataset Scope

This assistant is intentionally specialized in:

**Stationery products**

* Notebooks
* Journals
* Planners
* Desk accessories

This improves:

* Accuracy
* Relevance
* Reliability

---

## Core Reliability Rules

* No hardcoded API keys
* Uses environment variable: `GEMINI_API_KEY`
* Recommends only from the provided catalog
* Validates LLM outputs before displaying
* Falls back safely if API fails

---

## Project Files

* `app.py` → Main Streamlit application
* `streamlit_app.py` → Streamlit Cloud entrypoint
* `products.py` → Product dataset
* `requirements.txt` → Dependencies
* `check_setup.py` → Optional setup verifier
* `.github/workflows/ci.yml` → CI checks

---

## ⚙️ Local Setup (Beginner-Friendly)

1. Open PowerShell in project folder

2. Create virtual environment:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Set API key:

```
$env:GEMINI_API_KEY="your_api_key_here"
```

5. Run app:

```
python -m streamlit run streamlit_app.py
```

---

## Verify Installation

```
python -m streamlit --version
python -m streamlit run streamlit_app.py
```

Expected:

```
Local URL: http://localhost:8501
```

---

## Common Issues

### Streamlit not recognized:

```
python -m pip install streamlit
```

---

### Dependencies error:

```
python -m pip install -r requirements.txt
```

---

### API key missing:

* Ensure `GEMINI_API_KEY` is set
* Or add in Streamlit Cloud Secrets

---

## Streamlit Cloud Deployment

1. Push code to GitHub
2. Go to Streamlit Cloud
3. Create new app
4. Select repo
5. Set main file:

```
streamlit_app.py
```

6. Add secret:

```
GEMINI_API_KEY = "your_api_key_here"
```

7. Deploy

---
<img width="1919" height="1014" alt="image" src="https://github.com/user-attachments/assets/db33bc56-e5c6-40fc-ab18-6d95c9978de5" />
<img width="1912" height="1002" alt="image" src="https://github.com/user-attachments/assets/bc07c43c-613e-4121-a118-44ae2606e6a7" />


## Architecture

```
User Input
   ↓
Intent Classification
   ↓
-------------------------
| Product Mode          |
| (Stationery Dataset)  |
-------------------------
         OR
-------------------------
| General Mode          |
| (LLM Knowledge)       |
-------------------------
   ↓
Final Response
```

---

## Learning Outcomes

* Prompt engineering for LLM systems
* Avoiding hallucination in AI applications
* Hybrid AI architecture design
* Context-aware chatbot development
* Building real-world AI products

---

## Conclusion

This project demonstrates how to build a **reliable, real-world AI assistant** that balances:

* Accuracy (no hallucination)
* Intelligence (LLM reasoning)
* Usability (clean UI + chat system)
