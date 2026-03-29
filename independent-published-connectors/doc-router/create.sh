#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

paconn create \
  --api-def "$SCRIPT_DIR/apiDefinition.swagger.json" \
  --api-prop "$SCRIPT_DIR/apiProperties.json" \
  --icon "$SCRIPT_DIR/icon.png" \
  --script "$SCRIPT_DIR/script.csx"
