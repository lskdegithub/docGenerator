#!/bin/bash
# Build Docker image for LaTeX project compilation
# Usage: ./scripts/docker_build_image.sh [image:tag]

set -e

IMAGE_NAME="${1:-latex-test-env:ubuntu22.04}"

echo "Building image: ${IMAGE_NAME}"
docker build -t "${IMAGE_NAME}" .
echo "Done."
