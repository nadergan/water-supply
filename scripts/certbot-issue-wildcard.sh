#!/usr/bin/env bash
# Let's Encrypt wildcard: *.ganayem.com + apex ganayem.com (recommended SAN set).
# Requires DNS-01 only — add TXT records when Certbot prompts (or configure a dns-* Certbot plugin).
# HTTP/webroot cannot obtain *.ganayem.com.
set -euo pipefail
: "${CERTBOT_EMAIL:?Set CERTBOT_EMAIL}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
cd "$ROOT"

CERT_NAME="${CERT_NAME:-ganayem-wildcard}"

echo "Certificate name: $CERT_NAME"
echo "Domains: *.ganayem.com, ganayem.com"
echo "When Certbot shows TXT name/value, add them at your DNS host, wait for propagation, then press Enter."
echo ""

docker compose run --rm -it --entrypoint certbot certbot certonly \
  --manual \
  --preferred-challenges dns \
  --cert-name "$CERT_NAME" \
  -d '*.ganayem.com' \
  -d 'ganayem.com' \
  --email "$CERTBOT_EMAIL" \
  --agree-tos

docker compose exec nginx nginx -s reload
echo "Nginx should load: /etc/letsencrypt/live/$CERT_NAME/{fullchain,privkey,chain}.pem"
