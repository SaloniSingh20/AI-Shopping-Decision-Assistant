# AI-Powered Shopping Assistant (Streamlit + Gemini)

A complete, deployment-ready shopping assistant built with Python, Streamlit, and Google Gemini API.

## What This Project Demonstrates

- Prompt engineering with strict anti-hallucination guardrails
- Context-aware chatbot with follow-up support
- Hybrid AI + logic flow (Python filtering first, then LLM ranking)
- Explainable recommendations with best-match highlighting
- Streamlit Cloud deployment readiness

## Core Reliability Rules

- No hardcoded API keys
- Uses environment variable: GEMINI_API_KEY
- Recommends only from the provided catalog

## Project Files

- app.py: Main Streamlit application
- products.py: Product dataset (12 products)
- requirements.txt: Runtime dependencies
- check_setup.py: Optional local setup verifier
- .github/workflows/ci.yml: Optional CI checks

## Local Setup (Beginner-Friendly, Windows-Safe)

1. Open PowerShell in the project folder.
2. (Recommended) Create and activate a virtual environment:

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

3. Install dependencies:

   pip install -r requirements.txt

4. If pip command fails, use fallback:

   python -m pip install -r requirements.txt

5. Set your API key for the current terminal session:

   $env:GEMINI_API_KEY="your_api_key_here"

6. Run with the safer command (avoids PATH issues):

   python -m streamlit run app.py

## Verify Streamlit Installation

Run:

python -m streamlit --version

Then start app:

python -m streamlit run app.py

Expected terminal output includes:

Local URL: http://localhost:8501

## If You Get: "streamlit is not recognized"

Use one of these commands:

- pip install streamlit
- python -m pip install streamlit

Then run:

python -m streamlit run app.py

## Troubleshooting

1. pip install fails:

   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt

2. Missing module errors (example: ModuleNotFoundError):

   python -m pip install -r requirements.txt

3. API key warning in app:

   Ensure GEMINI_API_KEY is set in the same terminal where you run Streamlit.

4. Verify setup quickly:

   python check_setup.py

## Streamlit Cloud Deployment Steps

1. Push code to GitHub.
2. Go to Streamlit Cloud.
3. Click Create app / New app.
4. Connect your GitHub repository.
5. Add app secret:

   GEMINI_API_KEY = "your_api_key_here"

6. Deploy.

## Optional CI

This repo includes a GitHub Actions workflow that runs on push/PR:

- Python syntax checks
- Dependency install verification
- Basic setup script check

## Notes on Reliability

- The app filters catalog items before calling Gemini.
- The app validates LLM recommendations against allowed product names.
- If no exact match exists, it shows closest catalog products only.
