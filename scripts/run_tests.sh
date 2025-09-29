#!/bin/bash
set -e

echo "Running unit tests..."
docker compose -f ../rootly-deployment/docker-compose.yml run --build --rm user-plant-management-backend pytest tests/unit/ -v

echo "Running integration tests..."
docker compose -f ../rootly-deployment/docker-compose.yml run --build --rm user-plant-management-backend pytest tests/integration/ -v

echo "All tests completed successfully!"
