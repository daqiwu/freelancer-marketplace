#!/usr/bin/env bash
# Start FastAPI backend with Poetry

echo "🚀 Starting Freelancer Marketplace Backend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Change to backend directory
cd "$(dirname "$0")"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed!"
    echo "   Install it with: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo "✅ Poetry found"
echo "📦 Installing dependencies..."

# Install dependencies
poetry install --no-interaction

echo "🔧 Starting FastAPI server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run uvicorn
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
