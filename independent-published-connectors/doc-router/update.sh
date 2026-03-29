#!/usr/bin/env bash
set -euo pipefail

CONNECTOR_ID="${1:-}"

if [[ -z "$CONNECTOR_ID" ]]; then
  echo "Usage: $0 <connector-id>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

paconn update \
  --api-def "$SCRIPT_DIR/apiDefinition.swagger.json" \
  --api-prop "$SCRIPT_DIR/apiProperties.json" \
  --connector-id "$CONNECTOR_ID"
