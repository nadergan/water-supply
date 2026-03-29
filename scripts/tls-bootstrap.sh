#!/usr/bin/env bash
# Self-signed placeholder so nginx can start before Let's Encrypt (replaced by certbot-issue-wildcard.sh or certbot-issue.sh).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
CERT_DIR="${CERT_LIVE_NAME:-ganayem-wildcard}"
LIVE="$ROOT/certbot/conf/live/$CERT_DIR"
mkdir -p "$ROOT/certbot/www" "$LIVE"
if [[ -f "$LIVE/privkey.pem" && -f "$LIVE/fullchain.pem" ]]; then
  echo "TLS material already present under certbot/conf/live/$CERT_DIR — skipping bootstrap."
  exit 0
fi
echo "Generating temporary self-signed cert under live/$CERT_DIR (browsers will warn until Let's Encrypt is issued)..."
# SANs: wildcard covers one label (*.ganayem.com); apex + common hosts for local testing
if openssl req -x509 -nodes -newkey rsa:2048 -days 2 \
  -keyout "$LIVE/privkey.pem" \
  -out "$LIVE/fullchain.pem" \
  -subj "/CN=*.ganayem.com" \
  -addext "subjectAltName=DNS:*.ganayem.com,DNS:ganayem.com,DNS:yasmin.ganayem.com,DNS:water.ganayem.com" 2>/dev/null; then
  :
else
  openssl req -x509 -nodes -newkey rsa:2048 -days 2 \
    -keyout "$LIVE/privkey.pem" \
    -out "$LIVE/fullchain.pem" \
    -subj "/CN=yasmin.ganayem.com"
fi
cp "$LIVE/fullchain.pem" "$LIVE/chain.pem"
echo "Done. Start or restart: docker compose up -d"
echo "Wildcard (DNS): CERTBOT_EMAIL=you@domain.com ./scripts/certbot-issue-wildcard.sh"
echo "Per-host HTTP-01: CERTBOT_EMAIL=you@domain.com ./scripts/certbot-issue.sh (and match nginx ssl paths to that cert)"
