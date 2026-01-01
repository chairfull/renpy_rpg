#!/bin/bash
# Run script for AI RPG
# Compiles data and launches Ren'Py

# 1. Compile Data
echo "Compiling data..."
python3 game/python/compile_data.py

if [ $? -ne 0 ]; then
    echo "Data compilation failed!"
    exit 1
fi

# 2. Run Ren'Py
echo "Launching Ren'Py..."

# Try to find SDK path from VS Code settings to match extension behavior
SETTINGS_FILE=".vscode/settings.json"
SDK_PATH=""

if [ -f "$SETTINGS_FILE" ]; then
    # Python one-liner to extract sdkPath safely
    SDK_PATH=$(python3 -c "import json, sys; print(json.load(open('$SETTINGS_FILE')).get('renpyWarp.sdkPath', ''))" 2>/dev/null)
fi

if [ -n "$SDK_PATH" ] && [ -d "$SDK_PATH" ]; then
    echo "Found configured SDK at: $SDK_PATH"
    "$SDK_PATH/renpy.sh" .
elif command -v renpy.sh &> /dev/null; then
    echo "Using system renpy.sh"
    renpy.sh .
elif command -v renpy &> /dev/null; then
    echo "Using system renpy"
    renpy .
else
    echo "Ren'Py executable not found."
    echo "Please ensure 'renpy.sh' is in your PATH or 'renpyWarp.sdkPath' is set in .vscode/settings.json"
    exit 1
fi
