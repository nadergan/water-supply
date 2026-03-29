#!/usr/bin/env bash
# Creates certbot dirs and a short-lived self-signed cert so nginx can start
# before the first Let's Encrypt issuance. Replaced when you run certbot-issue.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LIVE="$ROOT/certbot/conf/live/yasmin.ganayem.com"
mkdir -p "$ROOT/certbot/www" "$LIVE"
if [[ -f "$LIVE/privkey.pem" && -f "$LIVE/fullchain.pem" ]]; then
  echo "TLS material already present under certbot/conf/live/yasmin.ganayem.com — skipping bootstrap."
  exit 0
fi
echo "Generating temporary self-signed certificate (replace with Let's Encrypt via scripts/certbot-issue.sh)..."
openssl req -x509 -nodes -newkey rsa:2048 -days 2 \
  -keyout "$LIVE/privkey.pem" \
  -out "$LIVE/fullchain.pem" \
  -subj "/CN=yasmin.ganayem.com"
cp "$LIVE/fullchain.pem" "$LIVE/chain.pem"
