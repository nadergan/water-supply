#!/usr/bin/env bash
# Show issuer and dates for the cert nginx loads (host path -> certbot volume).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PEM="$ROOT/certbot/conf/live/yasmin.ganayem.com/fullchain.pem"
if [[ ! -f "$PEM" ]]; then
  echo "No cert at $PEM — run ./scripts/tls-bootstrap.sh first."
  exit 1
fi
echo "File: $PEM"
openssl x509 -in "$PEM" -noout -subject -issuer -dates
echo ""
if openssl x509 -in "$PEM" -noout -issuer | grep -qi "Let's Encrypt"; then
  echo "Issuer looks like Let's Encrypt — browsers should trust this (after correct hostname on the cert)."
else
  echo "Not a Let's Encrypt cert (likely bootstrap self-signed). Run:"
  echo "  CERTBOT_EMAIL=you@domain.com ./scripts/certbot-issue.sh"
fi
