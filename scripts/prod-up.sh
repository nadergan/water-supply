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
echo "🌐 HTTP :80 redirects to HTTPS. DNS: point *.ganayem.com (or yasmin/water) to this host."
echo ""
echo "Trusted TLS: wildcard needs DNS-01:"
echo "  CERTBOT_EMAIL=you@domain.com ./scripts/certbot-issue-wildcard.sh"
echo "Per-host HTTP-01 (no wildcard): ./scripts/certbot-issue.sh — then match nginx ssl paths to Certbot's live/ dir."
echo ""
echo "Inspect cert on disk: ./scripts/check-tls.sh"
