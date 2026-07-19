#!/usr/bin/env bash
set -euo pipefail

if docker compose version >/dev/null 2>&1; then
    COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE=(docker-compose)
else
    echo "Docker Compose is required" >&2
    exit 1
fi

cleanup() {
    "${COMPOSE[@]}" -f docker-compose.simulator.yml down --volumes --remove-orphans || true
}
trap cleanup EXIT

echo "Starting VR-ASI-1 simulator tests..."
"${COMPOSE[@]}" -f docker-compose.simulator.yml up --build -d

echo "Checking service health..."
MAX_RETRIES=24
RETRY_INTERVAL=5
SERVICE_URLS=(
    "http://localhost:8080/health"
    "http://localhost:4000"
    "http://localhost:8081"
    "http://localhost:8082"
)
for service_url in "${SERVICE_URLS[@]}"; do
    retries=0
    until curl --fail --silent --show-error "$service_url" >/dev/null; do
        retries=$((retries + 1))
        if [ "$retries" -ge "$MAX_RETRIES" ]; then
            echo "Service at $service_url did not become ready in time" >&2
            "${COMPOSE[@]}" -f docker-compose.simulator.yml ps >&2
            "${COMPOSE[@]}" -f docker-compose.simulator.yml logs --no-color --tail 100 >&2
            exit 1
        fi
        sleep "$RETRY_INTERVAL"
    done
done

echo "Running BVR scenario: agent hand-off..."
curl --fail --silent --show-error -X POST -H "Content-Type: application/json" \
    --data-binary @oden.json http://localhost:8080/plugins/register >/dev/null

echo "Simulator tests finished."
