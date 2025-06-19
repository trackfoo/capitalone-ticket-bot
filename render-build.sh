#!/bin/bash
set -e

# Install Python packages
pip install -r requirements.txt

# Manually install Chromium into a known location
PLAYWRIGHT_BROWSERS_PATH=/tmp/pw-browsers python -m playwright install chromium

# Export so Playwright can find it during execution
echo "PLAYWRIGHT_BROWSERS_PATH=/tmp/pw-browsers" >> $HOME/.bashrc