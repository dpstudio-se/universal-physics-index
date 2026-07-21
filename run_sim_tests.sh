#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE=(docker compose -f docker-compose.simulator.yml)
PORT_ANGELICA="${PORT_ANGELICA:-8080}"
PORT_PUTER="${PORT_PUTER:-4000}"

cleanup() {
    "${COMPOSE[@]}" down --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Checking the standalone VR-ASI physics layer..."
PYTHONPATH=modules/vrasi-physics/src python - <<'PY'
import json
from dataclasses import asdict

from vrasi_physics import evaluate_frequency

print(json.dumps(asdict(evaluate_frequency(8.0)), sort_keys=True))
PY

echo "Checking the standalone 3-6-9/Gen4 swarm layer..."
PYTHONPATH=modules/vrasi-swarm/src python -m vrasi_swarm demo

echo "Starting VR-ASI-1 Simulator Tests..."
"${COMPOSE[@]}" up -d

echo "Checking service health..."
MAX_RETRIES=12
RETRY_INTERVAL=5

for service_url in "http://localhost:${PORT_ANGELICA}/health" "http://localhost:${PORT_PUTER}"; do
    retries=0
    until curl --fail --silent --show-error --max-time 3 "$service_url" > /dev/null 2>&1; do
        retries=$((retries + 1))
        if [ "$retries" -ge "$MAX_RETRIES" ]; then
            echo "Service at $service_url did not become ready in time"
            exit 1
        fi
        echo "Waiting for $service_url... (attempt $retries/$MAX_RETRIES)"
        sleep "$RETRY_INTERVAL"
    done
    echo "$service_url is ready"
done

echo "Running BVR Scenarios..."
# Scenario 1: Agent Hand-off
curl --fail --silent --show-error --max-time 5 \
    --request POST \
    --header "Content-Type: application/json" \
    --data-binary @oden.json \
    "http://localhost:${PORT_ANGELICA}/plugins/register"
echo "Scenario 1 complete."

echo "Tests finished."
