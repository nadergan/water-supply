#!/bin/bash
set -euo pipefail

# Local dev: build and run only water-app via Compose (shows up in `docker compose ps`).
COMPOSE_FILES="-f docker-compose.yaml -f docker-compose.dev.yaml"

echo "Building Water Analysis image and starting water-app on port 3000..."

docker rm -f water-app 2>/dev/null || true

docker compose $COMPOSE_FILES up -d --build water-app

echo "✅ Container started successfully!"
echo "🌐 Application available at: http://localhost:3000"
echo ""
echo "Compose sees this stack (app-only dev overlay):"
echo "  docker compose $COMPOSE_FILES ps"
echo ""
echo "Useful commands:"
echo "  View logs: docker compose $COMPOSE_FILES logs -f water-app"
echo "  Stop:      docker compose $COMPOSE_FILES stop water-app"
echo "  Remove:    docker compose $COMPOSE_FILES rm -sf water-app"
echo ""
echo "Full stack (nginx + static sites + TLS):"
echo "  docker compose up -d"
