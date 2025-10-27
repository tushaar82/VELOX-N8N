#!/bin/bash

# Setup script for VELOX Real-Time Technical Analysis System
# This script sets up the development environment

set -e

echo "================================================"
echo "  VELOX Setup Script"
echo "================================================"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ Python 3.10 or higher is required. Found: $PYTHON_VERSION"
    echo "   Please install Python 3.10+ and try again."
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "🐍 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf venv
        python3 -m venv venv
        echo "✅ Virtual environment recreated"
    else
        echo "⏭️  Skipping virtual environment creation"
    fi
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

echo ""

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Install Playwright browsers
echo ""
echo "🌐 Installing Playwright browsers (Chromium)..."
playwright install chromium

echo ""
echo "📝 Setting up environment file..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists"
    read -p "Do you want to overwrite it with .env.example? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ .env file created from template"
    else
        echo "⏭️  Keeping existing .env file"
    fi
else
    cp .env.example .env
    echo "✅ .env file created from template"
fi

echo ""
echo "================================================"
echo "✅ Setup completed successfully!"
echo "================================================"
echo ""
echo "📋 Next steps:"
echo ""
echo "   1. Edit the .env file and add your OpenAlgo API key:"
echo "      nano .env"
echo ""
echo "   2. Make sure OpenAlgo server is running"
echo ""
echo "   3. Run the development server:"
echo "      ./scripts/run_dev.sh"
echo ""
echo "   4. Visit the API documentation:"
echo "      http://localhost:8000/docs"
echo ""
echo "💡 Tips:"
echo "   - To activate the virtual environment manually:"
echo "     source venv/bin/activate"
echo ""
echo "   - To run tests:"
echo "     pytest tests/ -v --cov=app"
echo ""
echo "   - To clone OpenAlgo reference (optional):"
echo "     ./scripts/clone_openalgo.sh"
echo ""
