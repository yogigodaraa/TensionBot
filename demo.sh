#!/bin/bash

# Mooring Data System Demo Script
# This script demonstrates the complete mooring data generation and visualization system

echo "🌊 Mooring Data Visualization System Demo"
echo "========================================"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to start process in background
start_background() {
    echo "Starting $1..."
    $2 &
    local pid=$!
    echo "Started $1 with PID $pid"
    return $pid
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists "python3"; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists "node"; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists "npm"; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ All prerequisites found"
echo ""

# Setup backend
echo "🔧 Setting up Python backend..."
cd backend

# Install in development mode
if command_exists "uv"; then
    echo "Using UV for Python package management..."
    uv venv
    source .venv/bin/activate
    uv pip install -e .
else
    echo "Using pip for Python package management..."
    pip install -e .
fi

cd ..

# Setup dashboard
echo "🔧 Setting up Node.js dashboard..."
cd dashboard
npm install
cd ..

echo ""
echo "✅ Setup complete!"
echo ""

# Start services
echo "🚀 Starting services..."

# Start dashboard
echo "Starting dashboard server..."
cd dashboard
npm start &
DASHBOARD_PID=$!
cd ..

# Wait for dashboard to start
sleep 3

# Start data receiver (alternative endpoint)
echo "Starting data receiver..."
cd backend
mooring-data-receiver --port 8001 &
RECEIVER_PID=$!
cd ..

# Wait for receiver to start
sleep 2

echo ""
echo "📊 Services are now running:"
echo "   Dashboard:     http://localhost:3000"
echo "   Data Receiver: http://localhost:8001"
echo ""

# Generate sample data
echo "🎯 Generating sample data..."
echo "This will send data to the dashboard for 30 seconds..."

cd backend

# Send data to dashboard
timeout 30s mooring-data-generator http://localhost:3000/api/mooring-data --interval 2 &
GENERATOR_PID=$!

echo ""
echo "📈 Data generation started!"
echo "🌐 Open your browser to http://localhost:3000 to view the dashboard"
echo ""
echo "Demo will run for 30 seconds..."
echo "Press Ctrl+C to stop early"

# Wait for generator to finish or user interrupt
wait $GENERATOR_PID 2>/dev/null

echo ""
echo "🏁 Demo complete!"
echo ""
echo "📊 System is still running. You can:"
echo "   1. View the dashboard: http://localhost:3000"
echo "   2. Send more data: mooring-data-generator http://localhost:3000/api/mooring-data"
echo "   3. Test with receiver: mooring-data-generator http://localhost:8001"
echo "   4. Generate OpenAPI spec: mooring-data-generator --openapi"
echo "   5. Save to file: mooring-data-generator --file sample_data.json"
echo ""
echo "To stop all services, run: pkill -f 'node\|mooring-data-receiver'"
echo ""
echo "Happy hacking! 🚀"