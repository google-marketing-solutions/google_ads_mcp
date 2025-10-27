#!/bin/bash

# YouTube Shorts Intelligence Platform - Setup Script

set -e  # Exit on error

echo "=========================================="
echo "YouTube Shorts Intelligence Platform"
echo "Setup & Installation"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi
echo "✓ Python $python_version found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"
echo ""

# Create outputs directory
echo "Creating output directory..."
mkdir -p outputs
echo "✓ Output directory created"
echo ""

# Copy environment template
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your API credentials"
else
    echo "✓ .env file already exists"
fi
echo ""

# Optional: Install Playwright browsers for web scraping
read -p "Install Playwright browsers for web scraping? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Playwright browsers..."
    playwright install chromium > /dev/null 2>&1
    echo "✓ Playwright browsers installed"
    echo ""
fi

# Display completion message
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Edit .env file with your API credentials:"
echo "   - YOUTUBE_API_KEY"
echo "   - ANTHROPIC_API_KEY"
echo "   - DATABRICKS_WORKSPACE_URL (optional)"
echo "   - DATABRICKS_ACCESS_TOKEN (optional)"
echo ""
echo "2. Run the standalone demo (no API keys required):"
echo "   python standalone_demo.py"
echo ""
echo "3. Or run the production pipeline (requires API keys):"
echo "   python demo_runner.py"
echo ""
echo "4. Review the documentation:"
echo "   - README.md - Technical documentation"
echo "   - ARCHITECTURE.md - Deployment guide"
echo "   - EXECUTIVE_SUMMARY.md - Business value summary"
echo ""
echo "=========================================="
