#!/usr/bin/env bash
# Run from cron (e.g. weekly): renews if due and reloads nginx.
# Wildcard certs need DNS-01 on renew — configure a dns-* plugin in /etc/letsencrypt/renewal/*.conf or renewal may fail.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
docker compose run --rm --entrypoint certbot certbot renew \
  --webroot -w /var/www/certbot \
  --preferred-challenges http-01 \
  --quiet
docker compose exec nginx nginx -s reload
