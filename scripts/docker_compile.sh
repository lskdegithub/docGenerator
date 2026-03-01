#!/bin/bash
# Compile documents in Docker with project bind mount.
# Usage:
#   ./scripts/docker_compile.sh all
#   ./scripts/docker_compile.sh test_plan
#   ./scripts/docker_compile.sh test_detail
#   ./scripts/docker_compile.sh test_report
# Optional env:
#   IMAGE=latex-test-env:ubuntu22.04

set -e

TARGET="${1:-all}"
IMAGE="${IMAGE:-latex-test-env:ubuntu22.04}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker not found"
  exit 1
fi

case "${TARGET}" in
  all)
    RUN_CMD="./scripts/build_test_plan.sh && ./scripts/build_test_detail.sh && ./scripts/build_test_report.sh"
    ;;
  test_plan)
    RUN_CMD="./scripts/build_test_plan.sh"
    ;;
  test_detail)
    RUN_CMD="./scripts/build_test_detail.sh"
    ;;
  test_report)
    RUN_CMD="./scripts/build_test_report.sh"
    ;;
  *)
    echo "Usage: $0 [all|test_plan|test_detail|test_report]"
    exit 1
    ;;
esac

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

DOCKER_TTY_ARGS=(-i)
if [ -t 0 ] && [ -t 1 ]; then
  DOCKER_TTY_ARGS=(-it)
fi

docker run --rm "${DOCKER_TTY_ARGS[@]}" \
  --user "$(id -u):$(id -g)" \
  -v "${PROJECT_ROOT}:/workspace" \
  -w /workspace \
  "${IMAGE}" \
  bash -lc "${RUN_CMD}"
