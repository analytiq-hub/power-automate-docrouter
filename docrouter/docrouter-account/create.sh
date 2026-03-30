#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

paconn create \
  --api-def "$SCRIPT_DIR/apiDefinition.swagger.json" \
  --api-prop "$SCRIPT_DIR/apiProperties.json" \
  --icon "$SCRIPT_DIR/icon.png" \
  --overwrite-settings

if [[ -f "$SCRIPT_DIR/settings.json" ]]; then
  CID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["connectorId"])' "$SCRIPT_DIR/settings.json")"
  echo ""
  echo "Connector ID: $CID"
  echo "Set in repo-root .env: ACCOUNT_CONNECTOR_ID='$CID'"
fi
