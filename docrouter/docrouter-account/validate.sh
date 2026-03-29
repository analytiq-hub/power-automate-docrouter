#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

paconn validate \
  --api-def "$SCRIPT_DIR/apiDefinition.swagger.json" \
  --verbose
