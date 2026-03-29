# DocRouter Account connector

Microsoft Power Automate custom connector for DocRouter **account-scoped** HTTP APIs (`/v0/account/...`): users, organizations, account API tokens, AWS integration, and LLM provider configuration.

Deploy with `create.sh` / `update.sh` (no C# script — paths are fixed in OpenAPI). Use an **account-level API token** (`acc_...`), not an organization token (`org_...`).

See the repository root `README.md` for `paconn` setup and a summary of operations.

Regenerate `apiDefinition.swagger.json` after API changes:

```bash
python3 docrouter/docrouter-account/generate_swagger.py
```

After changing the OpenAPI file, run `update.sh` so the Power Automate **Test** tab uses the new response schema (otherwise you may see stale type validation on e.g. `created_at`).
