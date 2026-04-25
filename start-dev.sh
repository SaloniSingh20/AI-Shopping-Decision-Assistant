#!/bin/bash

# Shop AI - Development Server Startup Script
# This script starts both backend (FastAPI) and frontend (Next.js)

echo "🚀 Starting Shop AI Development Servers..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Start Backend (FastAPI on port 8000)
echo -e "${BLUE}Starting Backend (FastAPI)...${NC}"
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start Frontend (Next.js on port 3000)
echo -e "${BLUE}Starting Frontend (Next.js)...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}✅ Both servers are starting!${NC}"
echo ""
echo "📍 Access your application at:"
echo -e "${GREEN}   Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}   Backend API: http://localhost:8000${NC}"
echo -e "${BLUE}   API Docs: http://localhost:8000/docs${NC}"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
