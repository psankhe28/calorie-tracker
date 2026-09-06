#!/usr/bin/env bash
# Runs backend (FastAPI) + frontend (Vite) locally, without Docker.
# Requires SUPABASE_URL / SUPABASE_SERVICE_KEY in .env, with backend/schema.sql already
# applied in that Supabase project's SQL Editor.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

BACKEND_PORT="${BACKEND_PORT:-8001}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

echo "==> Backend: preparing (venv, deps)"
cd "$ROOT_DIR/backend"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q -r requirements.txt

echo "==> Backend: starting on port $BACKEND_PORT"
.venv/bin/uvicorn app.main:app --reload --port "$BACKEND_PORT" &
BACKEND_PID=$!

echo "==> Frontend: preparing (npm install)"
cd "$ROOT_DIR/frontend"
if [ ! -d node_modules ]; then
  npm install
fi

echo "==> Frontend: starting on port $FRONTEND_PORT"
VITE_API_BASE_URL="http://localhost:$BACKEND_PORT" npm run dev -- --port "$FRONTEND_PORT" &
FRONTEND_PID=$!

cd "$ROOT_DIR"

cleanup() {
  echo ""
  echo "==> Shutting down..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

echo ""
echo "Backend:  http://localhost:$BACKEND_PORT  (docs: /docs)"
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "Press Ctrl+C to stop both."

wait
