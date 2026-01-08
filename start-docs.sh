#!/bin/bash
# Quick script to start the interactive documentation

echo ""
echo "================================================================================"
echo "  RBAC Algorithm - Interactive Documentation"
echo "================================================================================"
echo ""
echo "Starting documentation server..."
echo ""

cd docs

if [ ! -d "node_modules" ]; then
    echo "First time setup: Installing dependencies..."
    echo "This may take a few minutes..."
    echo ""
    npm install
    echo ""
    echo "Installation complete!"
    echo ""
fi

echo "Starting server..."
echo "The documentation will open automatically in your browser."
echo ""
echo "Access at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

npm start
