# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the **DocRouter Microsoft Power Automate custom connector** — an independent-publisher connector that exposes the DocRouter.ai REST API to Microsoft Power Automate workflows.

- **DocRouter source**: `../doc-router/` (FastAPI backend at `/fastapi`, docs at `../doc-router/docs/`)
- **Connector reference examples**: `../PowerPlatformConnectors/` (official Microsoft repository)
  - `independent-publisher-connectors/` — closest match to this project's connector type
  - `certified-connectors/` — higher-quality examples for auth patterns and operation design

## Repository Structure

```
power-automate-docrouter/
├── independent-published-connectors/
│   └── doc-router/
│       ├── apiDefinition.swagger.json   # OpenAPI 2.0 spec (primary artifact)
│       ├── apiProperties.json           # Power Automate connector metadata & auth
│       ├── create.sh                    # paconn create (first deploy)
│       └── update.sh                   # paconn update <connector-id>
├── requirements.txt                     # Python dep: paconn
├── README.md
└── CLAUDE.md
```

## Key Files

### `apiDefinition.swagger.json`
The core connector artifact. Must conform to **OpenAPI 2.0** (not 3.x). Key constraints:
- `"swagger": "2.0"` — Power Automate requires Swagger 2.0
- Uses `x-ms-parameterized-host` to support both cloud (`app.docrouter.ai`) and on-premises deployments
- Auth: API key via `X-Api-Key` header (`securityDefinitions.api_key`)
- All operations must have `operationId`, `x-ms-summary`, and `description`
- Parameters must include `x-ms-summary` for UI display labels
- Response schemas must be fully inlined (no `$ref` to external files)

### `apiProperties.json`
Connector metadata consumed by Power Automate portal:
- `connectionParameters.api_key` — securestring for the API key UI prompt
- `iconBrandColor` — `#2563EB` (DocRouter blue)
- `publisher` — `Analytiq Hub LLC`
- `stackOwner` — `DocRouter`

### `create.sh` / `update.sh`
Deploy scripts using the `paconn` CLI (installed via `pip install paconn`):
```bash
# First-time creation
./independent-published-connectors/doc-router/create.sh

# Update existing connector
./independent-published-connectors/doc-router/update.sh <connector-id>
```

## Development Workflow

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # installs paconn
```

### Validate the Swagger Locally
Use the Power Automate custom connector wizard (portal.azure.com or make.powerautomate.com) to import and validate `apiDefinition.swagger.json`. The portal shows validation errors inline.

Alternatively, validate OpenAPI 2.0 compliance with:
```bash
npx swagger-parser validate independent-published-connectors/doc-router/apiDefinition.swagger.json
```

### Syncing from DocRouter Source
The upstream source of truth for the API spec is:
- `../doc-router/docs/docrouter_power_automate_connector.yaml` — YAML version of the spec
- `../doc-router/packages/python/app/` — FastAPI route definitions

When DocRouter adds new endpoints, update `apiDefinition.swagger.json` to match. Convert the YAML spec to JSON if needed:
```bash
python -c "import sys, json, yaml; json.dump(yaml.safe_load(sys.stdin), sys.stdout, indent=2)" \
  < ../doc-router/docs/docrouter_power_automate_connector.yaml \
  > independent-published-connectors/doc-router/apiDefinition.swagger.json
```

## Connector Design Conventions

Follow patterns from `../PowerPlatformConnectors/independent-publisher-connectors/`:

- Every operation needs: `operationId` (PascalCase), `summary` (short label), `description` (longer help text), `x-ms-summary` on all parameters
- Use `x-ms-visibility: important` for primary parameters, `advanced` for optional ones
- Binary file uploads use `in: formData` with `type: string, format: binary`
- Paginated list responses include `nextLink` or cursor fields
- Webhook operations (if any) use `x-ms-trigger: single` or `batch`

## DocRouter API Context

The DocRouter FastAPI backend (`../doc-router`) exposes endpoints under `/fastapi`. Key resource groups:
- **Documents**: upload, list, get, delete, run extraction
- **Prompts**: CRUD for LLM extraction prompts (with versioning)
- **Schemas**: JSON Schema definitions for structured extraction
- **Organizations**: multi-tenant scoping (all paths include `organization_id`)
- **Webhooks**: event-based notifications on document state changes
- **Knowledge Bases**: RAG knowledge base management

Authentication uses `X-Api-Key` header. API keys are created under Settings → Developer in the DocRouter UI.
