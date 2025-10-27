#!/bin/bash

# Script to clone OpenAlgo repositories for reference
# This is optional and only needed if you want to explore OpenAlgo source code

set -e

echo "================================================"
echo "  OpenAlgo Repository Cloner"
echo "================================================"
echo ""

# Create reference directory
REFERENCE_DIR="openalgo-reference"

if [ -d "$REFERENCE_DIR" ]; then
    echo "⚠️  Reference directory already exists: $REFERENCE_DIR"
    read -p "Do you want to remove and re-clone? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing directory..."
        rm -rf "$REFERENCE_DIR"
    else
        echo "❌ Aborted."
        exit 0
    fi
fi

echo "📁 Creating reference directory..."
mkdir -p "$REFERENCE_DIR"
cd "$REFERENCE_DIR"

# Clone OpenAlgo main repository
echo ""
echo "📥 Cloning OpenAlgo main repository..."
if git clone https://github.com/marketcalls/openalgo.git; then
    echo "✅ OpenAlgo main repository cloned successfully"
else
    echo "❌ Failed to clone OpenAlgo main repository"
    exit 1
fi

# Clone OpenAlgo Python library
echo ""
echo "📥 Cloning OpenAlgo Python library..."
if git clone https://github.com/marketcalls/openalgo-python-library.git; then
    echo "✅ OpenAlgo Python library cloned successfully"
else
    echo "❌ Failed to clone OpenAlgo Python library"
    exit 1
fi

cd ..

echo ""
echo "================================================"
echo "✅ OpenAlgo repositories cloned successfully!"
echo "================================================"
echo ""
echo "📂 Location: ./$REFERENCE_DIR/"
echo ""
echo "📖 Next steps:"
echo "   1. Review OpenAlgo documentation in ./$REFERENCE_DIR/openalgo/"
echo "   2. Set up OpenAlgo server if needed"
echo "   3. Get your API key from the OpenAlgo server"
echo "   4. Update the .env file with your API key"
echo ""
echo "🔗 OpenAlgo Documentation: https://github.com/marketcalls/openalgo"
echo ""
