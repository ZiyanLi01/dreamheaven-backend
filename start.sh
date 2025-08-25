#!/bin/bash

# Dream Haven Backend Startup Script

echo "Starting Dream Haven Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please copy env.example to .env and configure your Supabase credentials"
    echo "cp env.example .env"
    exit 1
fi

# Start the server
echo "Starting FastAPI server..."
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo "Press Ctrl+C to stop the server"
echo ""

python main.py 