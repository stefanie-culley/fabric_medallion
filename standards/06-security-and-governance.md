# 06 — Security & Governance

## Workspace roles

| Role | `<domain>-dev` | `<domain>-test` / `<domain>-prod` |
|---|---|---|
| Admin | Platform leads (2 people minimum) | Platform leads |
| Member | Domain data owner | Domain data owner |
| Contributor | Data & analytics engineers | — (deployment pipeline only) |
| Viewer | — | — |

Analysts and report builders get **item-level access to `gold`** (and its semantic models), not a workspace role, because a workspace role would also expose `bronze` and `silver`.

- Assign roles to **Entra ID security groups**, never to individual users.
- Production workspaces: only the deployment pipeline / service principal and platform leads have write access. Engineers change prod through Git + deployment, not by editing in prod.

## Data access below workspace level

- Gold consumers who should not see every table get access via item permissions, SQL endpoint permissions, or OneLake data access roles, not Viewer on the workspace.
- Row-level security for report users is defined in the semantic model.

## Personal and sensitive data

- Every table that contains PII is listed in the table documentation with the PII columns named.
- PII lands in Bronze only when needed. In Silver, mask, hash, or drop PII columns not required downstream.
- Gold contains PII only with an approved use case.
- Apply **Microsoft Purview sensitivity labels** using the starter mapping in [ADR 0011](../adr/0011-sensitivity-label-mapping.md): **Public** for sample data, **General** for Gold without personal data, **Confidential** for `bronze`, `silver` and any Gold table with personal data. Anything built from a labeled item carries at least the same label.
- Deletion requests (e.g. GDPR) are applied in all layers including Bronze, followed by `VACUUM` so deleted rows are physically removed.

## Secrets and connections

- No credentials, keys, or connection strings in notebooks, pipelines, or this repo.
- Use Fabric **connections** (managed in the gateway/connection settings) for pipelines.
- Notebooks read secrets from **Azure Key Vault** (`notebookutils.credentials.getSecret`).
- Prefer service principals or workspace identity over personal accounts for scheduled runs, so jobs don't break when people leave.

## Ownership and documentation

Every Silver and Gold table has, in the domain's `docs/` folder or the item description:
- Owner (team and named person)
- Description and grain
- Source tables
- Refresh schedule and SLA
- PII columns
- Known limitations

Endorse Gold lakehouses and semantic models as **Promoted** once documented and **Certified** once approved by the domain data owner.
