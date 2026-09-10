#!/usr/bin/env sh
set -eu

BASE_URL="${BASE_URL:-http://localhost:8000}"
API_KEY="${GAMEOPS_API_KEY:-development-key}"

request() {
  curl --fail-with-body --silent --show-error "$@"
  printf '\n'
}

printf 'Checking API health...\n'
request "$BASE_URL/healthz"

for item in "rp-server-01:us-east:128" "arena-01:eu-west:64"; do
  name=$(printf '%s' "$item" | cut -d: -f1)
  region=$(printf '%s' "$item" | cut -d: -f2)
  capacity=$(printf '%s' "$item" | cut -d: -f3)
  printf 'Creating %s (a 409 means it already exists)...\n' "$name"
  curl --silent --show-error -X POST "$BASE_URL/api/v1/servers" \
    -H 'Content-Type: application/json' -H "X-API-Key: $API_KEY" \
    -d "{\"name\":\"$name\",\"region\":\"$region\",\"max_players\":$capacity}" || true
  printf '\n'
done

printf 'Current inventory:\n'
inventory=$(curl --fail-with-body --silent --show-error "$BASE_URL/api/v1/servers")
printf '%s\n' "$inventory"

server_id=$(printf '%s' "$inventory" | python -c 'import json,sys; rows=json.load(sys.stdin); print(next((r["id"] for r in rows if r["name"] == "rp-server-01"), ""))')
if [ -n "$server_id" ]; then
  printf 'Updating rp-server-01 to online with 12 players...\n'
  request -X PATCH "$BASE_URL/api/v1/servers/$server_id" \
    -H 'Content-Type: application/json' -H "X-API-Key: $API_KEY" \
    -d '{"status":"online","players":12}'
fi
