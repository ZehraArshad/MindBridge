#!/usr/bin/env bash
set -e

PYTHON_SCRIPT="main.py"

SCRIPT_DIR=$(dirname "$(realpath "$0")")
cd "$SCRIPT_DIR" || exit 1

echo "Running $PYTHON_SCRIPT..."
../../../.venv/Scripts/python.exe "$PYTHON_SCRIPT"
