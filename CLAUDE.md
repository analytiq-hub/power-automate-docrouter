# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains Microsoft Power Automate custom connectors for DocRouter.ai. Connector sources live under **`docrouter/`**: **`docrouter-org/`** is the **DocRouter Organization RC1** connector (organization-scoped APIs, `/v0/orgs/...`, C# script injects org id). **`docrouter-account/`** is the **DocRouter Account** connector (account-scoped APIs, `/v0/account/...`, no script; **account-level** API token `acc_...` via `X-Api-Key`).

- **DocRouter source**: `../doc-router/` (FastAPI backend at `/fastapi`, docs at `../doc-router/docs/`)
- **Connector reference examples**: `../PowerPlatformConnectors/` (official Microsoft repository)
  - `independent-publisher-connectors/` — closest match to this project's connector type
  - `certified-connectors/` — higher-quality examples for auth patterns and operation design

## Repository Structure

```
power-automate-docrouter/
├── docrouter/
│   ├── docrouter-org/                 # Organization-scoped connector (RC1)
│   │   ├── apiDefinition.swagger.json   # OpenAPI 2.0 spec (primary artifact)
│   │   ├── apiProperties.json           # Power Automate connector metadata & auth
│   │   ├── script.csx                   # Injects connection org id into URL paths (all operations)
│   │   ├── create.sh / update.sh        # paconn create / update (pass --script)
│   │   ├── validate.sh                  # paconn validate (swagger)
│   │   ├── download.sh                  # paconn download → ./download/ (gitignored)
│   │   └── settings.json                # optional paconn --settings (local; gitignored)
│   └── docrouter-account/             # Account-scoped connector (/v0/account/)
│       ├── apiDefinition.swagger.json   # OpenAPI 2.0 (regenerate via generate_swagger.py)
│       ├── apiProperties.json           # base_url + Account API token (no org id)
│       ├── generate_swagger.py          # helper to rebuild the OpenAPI from route inventory
│       ├── create.sh / update.sh        # paconn create / update (no --script)
│       ├── validate.sh
│       ├── download.sh
│       └── settings.json                # optional paconn --settings (local; gitignored)
├── external-connectors/               # scripts to try connectors from ../PowerPlatformConnectors
├── login.sh                           # paconn login
├── logout.sh                          # paconn logout
├── requirements.txt                   # Python dep: paconn
├── README.md
└── CLAUDE.md
```

## Key Files

### Organization (`docrouter/docrouter-org/`) vs Account (`docrouter/docrouter-account/`)

- **Org**: `connectionParameters` include **`docrouter_organization_id`** and **`api_key`** (org token `org_...`); **`policyTemplateInstances`** pass a header for the script; **`script.csx`** rewrites `/v0/orgs/...` and handles upload/metadata quirks.
- **Account**: **`api_key`** only (plus optional **`base_url`**); **no** org id, **no** policy, **no** script — paths in OpenAPI are the real `/v0/account/...` routes. Backend auth resolves account vs org tokens by path (`get_api_context` in `../doc-router/.../auth.py`).

### `apiDefinition.swagger.json`
The core connector artifact. Must conform to **OpenAPI 2.0** (not 3.x). Key constraints:
- `"swagger": "2.0"` — Power Automate requires Swagger 2.0
- Uses fixed `host` / `basePath` in the spec; connection **`base_url`** in `apiProperties.json` is for the connector connection UI (on‑prem / custom host is typically wired via connector host settings or policies in the portal—not `x-ms-parameterized-host` in the current checked-in spec)
- Auth: API key via `X-Api-Key` header (`securityDefinitions.api_key`)
- All operations must have `operationId`, `x-ms-summary`, and `description`
- Parameters must include `x-ms-summary` for UI display labels
- Response schemas must be fully inlined (no `$ref` to external files)

### `apiProperties.json`
Connector metadata consumed by Power Automate portal (org connector shown; account omits org id and policies):
- `connectionParameters.api_key` — securestring; org UI label **Organization Token**; account UI label **Account API token** (`acc_...`)
- `connectionParameters.docrouter_organization_id` — **organization** connector only; once per connection (see `script.csx`)
- `connectionParameters.base_url` — optional; default `https://app.docrouter.ai/fastapi` when left blank
- `policyTemplateInstances` / `scriptOperations` — **organization** connector only (`scriptOperations`: `[]` runs the script for all operations)
- `iconBrandColor` — `#FFFFFF` (white tile; if the logo looks faint or garbled in the portal, increase icon/background contrast or adjust the asset)
- `publisher` — `Analytiq Hub LLC`
- `stackOwner` — `DocRouter`

### `script.csx` (organization connector only)
- Implements `ScriptBase`: reads connection header `docrouter_organization_id`, rewrites `/v0/orgs/{segment}/` in `RequestUri`, coerces upload/update **metadata** JSON strings to objects, wraps **Upload Document** (single body) to the API batch shape `{ documents: [...] }` with `name` from `document_name`, unwraps the upload response to one document object, strips connection headers, then `SendAsync`.
- Deploy with `paconn create` / `paconn update` using `--script` (see `docrouter/docrouter-org/create.sh` / `update.sh`).

### `create.sh` / `update.sh`
Deploy scripts using the `paconn` CLI (installed via `pip install paconn`):
```bash
# Organization connector (first-time)
./docrouter/docrouter-org/create.sh

# Account connector (first-time; no --script)
./docrouter/docrouter-account/create.sh

# Update existing connector
./docrouter/docrouter-org/update.sh <connector-id>
./docrouter/docrouter-account/update.sh <connector-id>
```

`update.sh` and `download.sh` for each connector read **`ORG_CONNECTOR_ID`** or **`ACCOUNT_CONNECTOR_ID`** from the repo-root `.env` when the connector id is not passed as the first argument (see `.env.example`).

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
npx swagger-parser validate docrouter/docrouter-org/apiDefinition.swagger.json
npx swagger-parser validate docrouter/docrouter-account/apiDefinition.swagger.json
```

### Syncing from DocRouter Source
The upstream source of truth for the **organization** API spec is:
- `../doc-router/docs/docrouter_power_automate_connector.yaml` — YAML version of the spec
- `../doc-router/packages/python/app/` — FastAPI route definitions

When DocRouter adds new endpoints, update `docrouter/docrouter-org/apiDefinition.swagger.json` to match. Convert the YAML spec to JSON if needed:
```bash
python -c "import sys, json, yaml; json.dump(yaml.safe_load(sys.stdin), sys.stdout, indent=2)" \
  < ../doc-router/docs/docrouter_power_automate_connector.yaml \
  > docrouter/docrouter-org/apiDefinition.swagger.json
```

For the **account** connector, routes live under `/v0/account/` in `../doc-router/packages/python/app/routes/` (e.g. `orgs.py`, `users.py`, `token.py`, `aws.py`, `llm.py`). After backend changes, edit `docrouter/docrouter-account/generate_swagger.py` and run:
```bash
python3 docrouter/docrouter-account/generate_swagger.py
```

## Power Automate OpenAPI types vs `../doc-router`

The custom connector **Test** step compares HTTP **response** bodies to the OpenAPI **response** schemas. Mismatches show as **Expected** (from the spec) vs **Actual** (how Power Automate classifies the JSON). Fix the **account** connector by editing `docrouter/docrouter-account/generate_swagger.py`, regenerating `apiDefinition.swagger.json`, and redeploying (`update.sh`). Do **not** guess types only from JSON samples—trace them in the backend.

### Method: inspect `../doc-router` first

1. **Find the route** in `../doc-router/packages/python/app/routes/` (account APIs: e.g. `orgs.py`, `users.py`, `llm.py`, `token.py`, `aws.py`).
2. **See how the response is built**: `response_model=SomePydanticModel` vs returning dicts; follow handlers into any helper that builds nested objects.
3. **Per field, note the source**:
   - **Raw MongoDB** (`user.get("email_verified")`, `organization.get("default_prompt_enabled")`, etc.): legacy or migrated documents may not match ideal JSON types at the wire.
   - **Computed in Python** (`bool(user.get("password"))`, arithmetic, Pydantic models with strict types): usually stable JSON booleans/numbers.
   - **Datetime**: often `datetime` serialized to ISO strings; timezone suffix may be missing depending on serializer.
   - **Nested models** (e.g. LLM lists in `llm.py`): match the Pydantic fields and numeric types (int vs float) to what FastAPI emits.
4. **Map that to OpenAPI** definitions in `generate_swagger.py`, regenerate, validate (`paconn validate`, portal **Test**).

### Booleans

| Situation in `../doc-router` | Typical PA symptom | OpenAPI adjustment |
|------------------------------|--------------------|--------------------|
| Field read straight from Mongo **without** coercion into a Pydantic `bool` | `Expected: boolean`, `Actual: string` (or strict boolean mismatch) | Prefer **`additionalProperties: true`** on the parent and **omit** the field from `properties`, **or** declare **`type: string`**, **or** fix the backend to coerce to `bool` before response. |
| Field **always** computed (e.g. `has_password=bool(...)`) | Usually none | Keep **`type: "boolean"`** in the spec. |

Use **`additionalProperties: true`** sparingly: it relaxes validation for undeclared keys but can hide future typing mistakes; prefer normalizing data in `../doc-router` when practical.

### Integers and `int32`

| Symptom | Cause | OpenAPI adjustment |
|---------|--------|-------------------|
| `Expected: "integer undefined"`, `Actual: "integer int32"` on token counts, dimensions, etc. | Power Automate classifies JSON integer numbers as **`integer` + `format: int32`**; a bare Swagger `integer` has no format (“undefined”). | Add **`"format": "int32"`** next to **`"type": "integer"`** for those properties (see `LLMChatModel` / `LLMEmbeddingModel` in `generate_swagger.py`). |

If the **reverse** mismatch appears (`Expected: int32`, `Actual: undefined`), remove `format` from that property or align with what **Test** reports.

### Date and time strings

| Symptom | Cause | OpenAPI adjustment |
|---------|--------|-------------------|
| `Expected: string date-time`, `Actual: string undefined` on timestamps | ISO strings **without** `Z` / offset, or PA not treating the value as `date-time`. | Use plain **`type: string`** without **`format: date-time`**, or **omit** the field from strict `properties` and rely on **`additionalProperties`** on the parent object (`Organization` timestamps). |

### Numbers (float)

Use **`type: number`** with **`format: float`** for cost fields when FastAPI returns floats. If **Test** reports a float/format mismatch, align the definition with the real JSON (and with `../doc-router` Pydantic models in `llm.py`).

## Connector Design Conventions

Follow patterns from `../PowerPlatformConnectors/independent-publisher-connectors/`:

- Every operation needs: `operationId` (PascalCase), `summary` (short label), `description` (longer help text), `x-ms-summary` on all parameters
- Use `x-ms-visibility: important` for primary parameters, `advanced` for optional ones
- Binary file uploads use `in: formData` with `type: string, format: binary`
- Paginated list responses include `nextLink` or cursor fields
- Webhook operations (if any) use `x-ms-trigger: single` or `batch`

### Organization path segment (no OpenAPI path parameter)

Paths use a fixed literal segment **`/v0/orgs/from-connection/`** instead of `{organization_id}`. That keeps **Test** and flow actions from showing an `organization_id` field. **`script.csx`** replaces `from-connection` with the real org id from **`docrouter_organization_id`** (via policy header) on every request. **Do not** name a connection parameter `organization_id`—it collided with the old path placeholder and produced `orgs/undefined/...`.

Optional portal-only **`policyTemplateInstances`** (e.g. set header from `@connectionParameters(...)`) are not represented in `paconn` deploys the same way in all environments—see Microsoft’s `PowerPlatformConnectors` samples (e.g. Zoho Invoice Basic) if you add policies manually.

### Dynamic Dropdowns with `x-ms-dynamic-values` / `x-ms-dynamic-list`

For parameters that reference DocRouter resources (tags, prompts, schemas), use **`x-ms-dynamic-values`** (single select) or **`x-ms-dynamic-list`** (arrays such as `tag_ids` on upload) with **`ListTags`**, **`ListPrompts`**, etc. Pass the org using **`connectionParameters.docrouter_organization_id`** when the operation does not expose `organization_id` as a visible parameter:

```json
"parameters": {
  "organization_id": {
    "parameterReference": "connectionParameters.docrouter_organization_id"
  }
}
```

**Tags on upload / update:** `tag_ids` is an array of tag id strings. You can add **`x-ms-dynamic-list`** on items with **`ListTags`** (see Clockify / Zapier NLA) so the designer shows tag names and stores ids.

**Metadata:** In OpenAPI, `metadata` is **`type: string`** (JSON object text) so Power Automate can save flows with expressions and composed JSON from any source. **`script.csx`** parses that string into a JSON **object** before the request reaches DocRouter (FastAPI still receives `Dict[str, str]`). Webhook **response** schemas keep `metadata` as `object` because the API returns structured JSON.

## DocRouter API Context

The DocRouter FastAPI backend (`../doc-router`) exposes endpoints under `/fastapi`. Key resource groups:
- **Documents**: upload, list, get, delete, run extraction
- **Prompts**: CRUD for LLM extraction prompts (with versioning)
- **Schemas**: JSON Schema definitions for structured extraction
- **Organizations**: multi-tenant scoping (all paths include `organization_id`)
- **Webhooks**: event-based notifications on document state changes
- **Knowledge Bases**: RAG knowledge base management

Authentication uses `X-Api-Key` header. API keys are created under Settings → Developer in the DocRouter UI.
