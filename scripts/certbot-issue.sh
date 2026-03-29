#!/usr/bin/env bash
# HTTP-01 certificate for explicit hostnames (NOT *.ganayem.com — use certbot-issue-wildcard.sh + DNS-01).
# After issuance, either point nginx ssl_certificate to Certbot's live/<name>/ or keep per-host paths.
# Requires: hostname DNS -> this host; stack up (nginx serves /.well-known/acme-challenge/).
set -euo pipefail
: "${CERTBOT_EMAIL:?Set CERTBOT_EMAIL to your address for Let's Encrypt}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# Set INCLUDE_WWW=1 only if DNS has www.yasmin.ganayem.com -> this host (adds SAN to the cert).
DOMAINS=(-d yasmin.ganayem.com)
if [[ "${INCLUDE_WWW:-}" == "1" ]]; then
  DOMAINS+=(-d www.yasmin.ganayem.com)
fi

docker compose run --rm --entrypoint certbot certbot certonly \
  --webroot -w /var/www/certbot \
  --preferred-challenges http-01 \
  "${DOMAINS[@]}" \
  --email "$CERTBOT_EMAIL" \
  --agree-tos \
  --non-interactive
docker compose exec nginx nginx -s reload
