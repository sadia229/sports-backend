#!/usr/bin/env bash
# Start the AI Match Predictor backend cleanly.
# Frees port 8001 first so you never hit "Address already in use".
set -e

cd "$(dirname "$0")"

PORT=8001

# 1) Free the port if something is already listening on it.
if lsof -ti:"$PORT" >/dev/null 2>&1; then
  echo "Port $PORT busy — stopping the old server..."
  lsof -ti:"$PORT" | xargs kill -9 2>/dev/null || true
  sleep 1
fi

# 2) Activate the venv.
source .venv/bin/activate

# 3) Run. (.env is loaded automatically — no cp needed.)
echo "Starting server on http://127.0.0.1:$PORT  (Ctrl+C to stop)"
exec uvicorn app.main:app --reload --port "$PORT"
