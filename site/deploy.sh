#!/bin/bash
# deploy.sh — run this on the VPS to rebuild the site after new content
# The Python engine calls this via publisher.py after each cycle

set -e

SITE_DIR="/var/www/theletter/site"
CONTENT_DIR="/var/www/theletter/content"

echo "[deploy] Starting build at $(date)"

cd "$SITE_DIR"

# Install deps if needed (first run only)
if [ ! -d "node_modules" ]; then
  echo "[deploy] Installing dependencies..."
  npm install
fi

# Build the Astro site
echo "[deploy] Building..."
npm run build

echo "[deploy] Done. Site live at $(date)"
