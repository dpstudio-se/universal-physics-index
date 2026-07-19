#!/bin/bash
echo "Starting VR-ASI-1 Simulator Tests..."
docker-compose -f docker-compose.simulator.yml up --build -d

echo "Checking service health..."
sleep 5
curl http://localhost:8080/health || echo "Angelica not ready"
curl http://localhost:4000 || echo "Puter Mock not ready"

echo "Running BVR Scenarios..."
# Scenario 1: Agent Hand-off
curl -X POST http://localhost:8080/plugins/register -d @oden.json
echo "Scenario 1 complete."

docker-compose -f docker-compose.simulator.yml down
echo "Tests finished."
