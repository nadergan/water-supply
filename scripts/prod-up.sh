#!/usr/bin/env bash
# Production: nginx + static sites + water-app + certbot renew (no host port on :3000).
# Run from your server in the repo root, or from anywhere (script cds to repo root).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
cd "$ROOT"

echo "Ensuring TLS material exists (bootstrap self-signed only if missing)..."
./scripts/tls-bootstrap.sh

echo "Starting full stack..."
docker compose up -d

echo ""
echo "✅ Stack is up. Check: docker compose ps"
echo "🌐 HTTP :80 redirects to HTTPS; app is at https://yasmin.ganayem.com/ (set DNS to this host)."
echo ""
echo "If the browser still shows an invalid certificate, issue Let's Encrypt:"
echo "  CERTBOT_EMAIL=you@domain.com ./scripts/certbot-issue.sh"
echo "  # with www in DNS: INCLUDE_WWW=1 CERTBOT_EMAIL=you@domain.com ./scripts/certbot-issue.sh"
echo ""
echo "Inspect cert on disk: ./scripts/check-tls.sh"
