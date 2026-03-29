#!/usr/bin/env bash
set -euo pipefail

# Local dev: build and run only water-app via Compose (shows up in `docker compose ps`).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
cd "$SCRIPT_DIR"

COMPOSE_FILES=(-f docker-compose.yaml -f docker-compose.dev.yaml)

echo "Building Water Analysis image and starting water-app on port 3000..."

docker rm -f water-app 2>/dev/null || true

docker compose "${COMPOSE_FILES[@]}" up -d --build water-app

echo "✅ Container started successfully!"
echo "🌐 Application available at: http://localhost:3000"
echo ""
echo "Compose sees this stack (app-only dev overlay):"
echo "  docker compose -f docker-compose.yaml -f docker-compose.dev.yaml ps"
echo ""
echo "Useful commands:"
echo "  View logs: docker compose -f docker-compose.yaml -f docker-compose.dev.yaml logs -f water-app"
echo "  Stop:      docker compose -f docker-compose.yaml -f docker-compose.dev.yaml stop water-app"
echo "  Remove:    docker compose -f docker-compose.yaml -f docker-compose.dev.yaml rm -sf water-app"
echo ""
echo "Production server (nginx + TLS + sites — not dev):"
echo "  ./scripts/prod-up.sh"
