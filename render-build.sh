#!/bin/bash
set -e

# Install dependencies
pip install -r requirements.txt

# Set custom install path and install Chromium
PLAYWRIGHT_BROWSERS_PATH=/tmp/pw-browsers python -m playwright install chromium