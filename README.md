# power-automate-docrouter

Microsoft Power Automate tooling for [DocRouter.ai](https://docrouter.ai): the **DocRouter Organization RC1** custom connector (organization-scoped HTTP API). A separate **DocRouter Account** connector may be added later.

## Sandbox sample flow

The **sandbox** is a minimal Power Automate flow that proves end-to-end file ingestion: read a file from **SharePoint** (or any source that exposes a name + Base64 content) and send it to DocRouter with **Upload Document**. It is not a separate product—just a reference pattern you can copy.

Typical sequence:

1. **Manually trigger a flow** — run on demand while you test.
2. **Get file metadata using path** — resolves the file in a SharePoint library (name, path, identifiers).
3. **Get file content** — loads the file bytes for the next step.
4. **Upload Document** (DocRouter Organization RC1) — maps **File name** → `document_name` and **File content** → `content`, then runs OCR/LLM processing on the DocRouter side.

![Sample sandbox flow: manual trigger, SharePoint file steps, DocRouter Upload Document](docs/images/sandbox-flow.png)

The same connector exposes the full org API (documents, tags, prompts, schemas, knowledge bases, OCR/LLM helpers, webhooks, and more). The action picker shows everything available under **DocRouter Organization RC1**:

![DocRouter Organization RC1 actions in Power Automate](docs/images/connector-actions.png)

## Installing the connector

You need the [Power Platform CLI connector tools](https://learn.microsoft.com/en-us/connectors/custom-connectors/) (`paconn`), a Python 3 environment, and rights to create custom connectors in your Power Platform **environment**.

### 1. Clone and Python environment

```bash
cd power-automate-docrouter
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

This installs `paconn`.

### 2. Sign in to Power Platform

From the repo root:

```bash
./login.sh
```

Or: `paconn login` after activating the venv. Complete the browser/device login for the tenant where the connector should live.

### 3. Create the connector (first time)

```bash
./independent-published-connectors/doc-router/create.sh
```

`paconn` registers the connector using:

- `independent-published-connectors/doc-router/apiDefinition.swagger.json`
- `independent-published-connectors/doc-router/apiProperties.json`
- `independent-published-connectors/doc-router/icon.png`
- `independent-published-connectors/doc-router/script.csx` (injects organization id into `/v0/orgs/...` paths)

Note the **connector id** in the output or in the Power Automate portal (**Data** → **Custom connectors**). You need it for updates.

### 4. Update an existing connector

Set the connector id, then run `update.sh`:

```bash
export CONNECTOR_ID='shared_your-connector-id-here'
# or add CONNECTOR_ID=... to a repo-root `.env` file
./independent-published-connectors/doc-router/update.sh
```

You can also pass the id as the first argument:

```bash
./independent-published-connectors/doc-router/update.sh 'shared_your-connector-id-here'
```

Optional: use `independent-published-connectors/doc-router/settings.json` with `paconn update --settings ...` if you rely on saved paths (see Microsoft’s `paconn` documentation).

### 5. Use the connector in a flow

In Power Automate, add an action from **DocRouter Organization RC1** and create a **connection** when prompted:

| Field | Purpose |
|--------|--------|
| **Base URL** | Optional. Default production API is used if blank (`https://app.docrouter.ai/fastapi`). |
| **Organization ID** | Your org segment from the DocRouter app URL (`.../orgs/{organization_id}/...`) or **Settings → Organization**. |
| **Organization Token** | API key from DocRouter **Settings → Developer** (sent as `X-Api-Key`). |

After the connection succeeds, you can build flows such as the sandbox above or call **Get Document**, **List Documents**, tags, prompts, and the rest of the operations shown in the action list screenshot.

### Alternative: import in the portal

You can also create or refresh a custom connector manually in [Power Automate](https://make.powerautomate.com) or the Power Platform portal by importing the same OpenAPI (`apiDefinition.swagger.json`), properties (`apiProperties.json`), icon, and C# script—`paconn` is the supported path for keeping this repo and the tenant in sync.

## Repository layout

- `independent-published-connectors/doc-router/` — connector artifacts (`apiDefinition.swagger.json`, `apiProperties.json`, `script.csx`, `create.sh`, `update.sh`, `validate.sh`, `download.sh`).
- `CLAUDE.md` — detailed conventions for maintaining the connector and syncing with the DocRouter API.
