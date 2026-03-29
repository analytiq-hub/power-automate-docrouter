#!/usr/bin/env bash
set -euo pipefail

# Load ACCOUNT_CONNECTOR_ID from .env if present
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -f "$REPO_ROOT/.env" ]]; then
  # shellcheck source=/dev/null
  set -o allexport; source "$REPO_ROOT/.env"; set +o allexport
fi

CONNECTOR_ID="${1:-${ACCOUNT_CONNECTOR_ID:-}}"

if [[ -z "$CONNECTOR_ID" ]]; then
  echo "Usage: $0 <connector-id>" >&2
  echo "  or set ACCOUNT_CONNECTOR_ID in .env" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

paconn update \
  --api-def "$SCRIPT_DIR/apiDefinition.swagger.json" \
  --api-prop "$SCRIPT_DIR/apiProperties.json" \
  --icon "$SCRIPT_DIR/icon.png" \
  --cid "$CONNECTOR_ID"
