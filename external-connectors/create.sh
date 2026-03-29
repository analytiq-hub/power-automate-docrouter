#!/usr/bin/env bash
set -euo pipefail

# Usage: ./create.sh [connector-dir]
# connector-dir defaults to EXTERNAL_CONNECTOR_DIR from .env

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$REPO_ROOT/.env" ]]; then
  # shellcheck source=/dev/null
  set -o allexport; source "$REPO_ROOT/.env"; set +o allexport
fi

CONNECTOR_DIR="${1:-${EXTERNAL_CONNECTOR_DIR:-}}"
[[ "$CONNECTOR_DIR" != /* ]] && CONNECTOR_DIR="$REPO_ROOT/$CONNECTOR_DIR"

if [[ -z "$CONNECTOR_DIR" ]]; then
  echo "Usage: $0 <connector-dir>" >&2
  echo "  or set EXTERNAL_CONNECTOR_DIR in .env" >&2
  exit 1
fi

if [[ ! -f "$CONNECTOR_DIR/apiDefinition.swagger.json" ]]; then
  echo "Error: $CONNECTOR_DIR/apiDefinition.swagger.json not found" >&2
  exit 1
fi

if [[ ! -f "$CONNECTOR_DIR/apiProperties.json" ]]; then
  echo "Error: $CONNECTOR_DIR/apiProperties.json not found" >&2
  exit 1
fi

extra_args=()
[[ -f "$CONNECTOR_DIR/icon.png"   ]] && extra_args+=(--icon   "$CONNECTOR_DIR/icon.png")
[[ -f "$CONNECTOR_DIR/script.csx" ]] && extra_args+=(--script "$CONNECTOR_DIR/script.csx")

paconn create \
  --api-def "$CONNECTOR_DIR/apiDefinition.swagger.json" \
  --api-prop "$CONNECTOR_DIR/apiProperties.json" \
  "${extra_args[@]}"
