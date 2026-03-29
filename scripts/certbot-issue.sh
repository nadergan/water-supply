#!/usr/bin/env bash
# First-time (or extra-domain) certificate via HTTP-01. Requires:
# - DNS yasmin.ganayem.com -> this host
# - Stack up: docker compose up -d (nginx must serve /.well-known/acme-challenge/)
set -euo pipefail
: "${CERTBOT_EMAIL:?Set CERTBOT_EMAIL to your address for Let's Encrypt}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
docker compose run --rm --entrypoint certbot certbot certonly \
  --webroot -w /var/www/certbot \
  --preferred-challenges http-01 \
  -d yasmin.ganayem.com \
  --email "$CERTBOT_EMAIL" \
  --agree-tos \
  --non-interactive
docker compose exec nginx nginx -s reload
