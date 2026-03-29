#!/usr/bin/env bash
set -euo pipefail

# Download the custom connector from Power Platform into a local folder (gitignored).
# Requires: pip install paconn && paconn login
#
# Usage:
#   ./download.sh
#   ./download.sh <connector-id> <environment-guid>
#
# Or set in repo-root .env (optional — paconn prompts for anything omitted):
#   ACCOUNT_CONNECTOR_ID
#   POWER_PLATFORM_ENVIRONMENT_ID
#
# Optional:
#   DOWNLOAD_ROOT — absolute or relative path for downloads (default: ./download next to this script)
#   DOWNLOAD_OVERWRITE=1 — pass --overwrite to paconn

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -f "$REPO_ROOT/.env" ]]; then
  # shellcheck source=/dev/null
  set -o allexport; source "$REPO_ROOT/.env"; set +o allexport
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONNECTOR_ID="${1:-${ACCOUNT_CONNECTOR_ID:-}}"
ENV_ID="${2:-${POWER_PLATFORM_ENVIRONMENT_ID:-${ENVIRONMENT_ID:-}}}"

DOWNLOAD_ROOT="${DOWNLOAD_ROOT:-$SCRIPT_DIR/download}"
mkdir -p "$DOWNLOAD_ROOT"

# Match create.sh / update.sh: omit --env (and --cid) when unset so paconn prompts interactively.
DOWNLOAD_ARGS=(download --dest "$DOWNLOAD_ROOT")
[[ -n "$CONNECTOR_ID" ]] && DOWNLOAD_ARGS+=(--cid "$CONNECTOR_ID")
[[ -n "$ENV_ID" ]] && DOWNLOAD_ARGS+=(--env "$ENV_ID")
if [[ "${DOWNLOAD_OVERWRITE:-}" == "1" || "${DOWNLOAD_OVERWRITE:-}" == "true" ]]; then
  DOWNLOAD_ARGS+=(--overwrite)
fi

paconn "${DOWNLOAD_ARGS[@]}"
