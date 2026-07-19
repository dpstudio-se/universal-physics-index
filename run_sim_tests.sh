#!/bin/bash
set -e
set -o pipefail

echo "Starting VR-ASI-1 Simulator Tests..."
docker-compose -f docker-compose.simulator.yml up --build -d

echo "Checking service health..."
MAX_RETRIES=12
RETRY_INTERVAL=5

for service_url in "http://localhost:8080/health" "http://localhost:4000"; do
    retries=0
    until curl -sf "$service_url" > /dev/null 2>&1; do
        retries=$((retries + 1))
        if [ "$retries" -ge "$MAX_RETRIES" ]; then
            echo "Service at $service_url did not become ready in time"
            docker-compose -f docker-compose.simulator.yml down
            exit 1
        fi
        echo "Waiting for $service_url... (attempt $retries/$MAX_RETRIES)"
        sleep "$RETRY_INTERVAL"
    done
    echo "$service_url is ready"
done

echo "Running BVR Scenarios..."
# Scenario 1: Agent Hand-off
curl -sf -X POST http://localhost:8080/plugins/register -d @oden.json
echo "Scenario 1 complete."

docker-compose -f docker-compose.simulator.yml down
echo "Tests finished."
