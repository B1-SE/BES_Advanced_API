#!/bin/bash
# Render build script
echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-dev.txt
echo "Build complete!"