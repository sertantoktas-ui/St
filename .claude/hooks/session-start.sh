#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "Installing Python dependencies..."
pip install -r "$CLAUDE_PROJECT_DIR/requirements.txt" --quiet --root-user-action=ignore
echo "Dependencies installed successfully."
