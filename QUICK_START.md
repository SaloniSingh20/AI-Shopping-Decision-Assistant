# 🚀 Quick Start Guide - Shop AI

## Running the Application Locally

### Option 1: Automated Startup (Recommended)

#### For Windows:
```bash
start-dev.bat
```

#### For Linux/Mac:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

This will automatically start both servers and open them in separate terminal windows.

---

### Option 2: Manual Startup

#### Step 1: Start the Backend (FastAPI)

Open a terminal and run:

```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

#### Step 2: Start the Frontend (Next.js)

Open a **new terminal** (keep the backend running) and run:

```bash
cd frontend
npm run dev
```

You should see:
```
  ▲ Next.js 16.2.0
  - Local:        http://localhost:3000
  - Ready in 2.3s
```

---

## 🌐 Access URLs

Once both servers are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main Shop AI chat interface |
| **Backend API** | http://localhost:8000 | FastAPI backend server |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs (Swagger UI) |
| **Health Check** | http://localhost:8000/health | Backend health status |

---

## ✅ Verify Everything is Working

### 1. Check Backend Health
Open your browser and go to: http://localhost:8000/health

You should see:
```json
{"status": "ok"}
```

### 2. Check API Documentation
Go to: http://localhost:8000/docs

You'll see the interactive Swagger UI with all API endpoints.

### 3. Test the Chat Interface
Go to: http://localhost:3000

Try these test queries:
- "I want pants under 2000 rupees"
- "Show me wireless earbuds under 1500"
- "I need a laptop for programming"

---

## 🔧 Configuration

### Backend Configuration (`.env` file)

The backend is configured in `backend/.env`:

```env
# LLM provider: huggingface
LLM_PROVIDER=huggingface

# HuggingFace Inference API config
HF_API_KEY=your_token_here
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Optional SerpAPI key (for better product links)
SERPAPI_API_KEY=

# Caching
CACHE_TTL_SECONDS=600
CACHE_MAXSIZE=512
```

### Frontend Configuration

The frontend connects to the backend at: `http://127.0.0.1:8000/chat`

This is configured in `frontend/app/page.tsx` (line 12).

---

## 🛠️ Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Frontend won't start

**Error**: `command not found: npm`

**Solution**: Install Node.js from https://nodejs.org/

**Error**: `Cannot find module 'next'`

**Solution**: Install dependencies:
```bash
cd frontend
npm install
```

### Port already in use

**Error**: `Address already in use: 8000` or `Port 3000 is already in use`

**Solution**: 
- Kill the process using that port
- Or change the port:
  - Backend: `uvicorn app.main:app --port 8001`
  - Frontend: `npm run dev -- -p 3001`

### CORS errors in browser console

**Error**: `Access to fetch at 'http://127.0.0.1:8000/chat' from origin 'http://localhost:3000' has been blocked by CORS`

**Solution**: The backend already has CORS enabled for all origins. Make sure the backend is running.

### AI responses are slow

This is normal for the first request as the HuggingFace model loads. Subsequent requests will be faster due to caching.

---

## 📦 Dependencies

### Backend Requirements
- Python 3.8+
- FastAPI
- Uvicorn
- HuggingFace API key (already configured)

### Frontend Requirements
- Node.js 18+
- npm or yarn
- Next.js 16.2.0

---

## 🎯 Testing the AI Improvements

After starting both servers, test these queries to see the new AI-powered responses:

1. **Specific product with budget**:
   - "I want pants under 2000 rupees for office"
   - Should get conversational response with relevant products

2. **Vague query**:
   - "show me laptops"
   - Should ask clarifying questions about budget and use case

3. **Electronics**:
   - "wireless earbuds under 1500"
   - Should get enthusiastic response with relevant earbuds

4. **Clothing**:
   - "casual t-shirts for men"
   - Should ask about budget and preferences

---

## 🔄 Restarting After Code Changes

### Backend Changes
The backend runs with `--reload` flag, so it automatically restarts when you modify Python files.

### Frontend Changes
Next.js has hot reload enabled by default. Just save your files and the browser will update.

### Environment Variable Changes
If you modify `.env` files, you need to manually restart the servers:
- Press `Ctrl+C` in each terminal
- Run the startup commands again

---

## 📝 Development Workflow

1. **Start both servers** using the startup script
2. **Open browser** to http://localhost:3000
3. **Make changes** to code
4. **Test immediately** - changes auto-reload
5. **Check logs** in the terminal windows for errors

---

## 🎉 You're Ready!

Your Shop AI application should now be running at:

### 🌟 **http://localhost:3000** 🌟

Try asking for product recommendations and see the AI-powered responses in action!
