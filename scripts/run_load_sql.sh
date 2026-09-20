#!/usr/bin/env bash
# Locust against the API on PostgreSQL with the xl profile (NFR-301, NFR-302).
# Needs the compose database up and migrated; it clears and reseeds that database.
set -euo pipefail
PORT="${1:-8123}"; PIDFILE="$(mktemp)"
trap 'kill "$(cat "$PIDFILE")" 2>/dev/null || true; rm -f "$PIDFILE"' EXIT
export SEED_PASSWORD="${SEED_PASSWORD:-Seeded-Password-123}"
uv run --frozen python -m app.seed --profile xl --reset --yes >/dev/null
export APP_ENV=test STORAGE_BACKEND=sql LOG_LEVEL=warning SEED_PROFILE=none RATE_LIMIT_ATTEMPTS=100000
uv run --frozen uvicorn app.main:create_app --factory --port "$PORT" --log-level warning &
echo $! > "$PIDFILE"
for _ in $(seq 1 60); do curl -fs "http://127.0.0.1:$PORT/readyz" >/dev/null && break; sleep 0.5; done
LOAD_PASSWORD="$SEED_PASSWORD" uv run --frozen locust -f tests/load/locustfile.py \
  --headless -u 20 -r 10 -t 30s --host "http://127.0.0.1:$PORT" --csv /tmp/devdash-load-sql --only-summary
