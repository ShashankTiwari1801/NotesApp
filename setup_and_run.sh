#!/bin/bash
set -e

REPO_URL="https://github.com/ShashankTiwari1801/NotesApp.git"
TARGET_DIR="NotesApp"

echo "=== 1. Cloning / Updating Repository ==="
if [ -d "$TARGET_DIR" ]; then
    echo "Directory $TARGET_DIR already exists. Pulling latest changes..."
    cd "$TARGET_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$TARGET_DIR"
    cd "$TARGET_DIR"
fi

echo "=== 2. Creating Python Virtual Environment ==="
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

echo "=== 3. Activating Venv & Installing Dependencies ==="
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== 4. Starting Notes App Server ==="
echo "The server will run on http://0.0.0.0:9110"
python run.py
