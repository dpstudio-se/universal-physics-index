#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE=(docker compose -f docker-compose.simulator.yml)
PORT_ANGELICA="${PORT_ANGELICA:-8080}"
PORT_PUTER="${PORT_PUTER:-4000}"

cleanup() {
    "${COMPOSE[@]}" down --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Checking the UPI calculation layer..."
PYTHONPATH=src python - <<'PY'
import json

from upi.physics import energy_from_frequency, index8_from_frequency, mass_from_frequency

frequency_hz = 8.0
print(json.dumps({
    "frequency_hz": frequency_hz,
    "energy_j": energy_from_frequency(frequency_hz),
    "mass_equivalent_kg": mass_from_frequency(frequency_hz),
    "n8_reference_index": index8_from_frequency(frequency_hz),
    "verification_type": "software_test",
    "claims_experimental_verification": False,
}))
PY

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
