# 07 — DevOps & Environments

## Environments

| Env | Purpose | Who changes it | Data |
|---|---|---|---|
| `dev` | Build and test changes | Engineers, through Git | Sample or masked data |
| `test` | Integration test, UAT | Deployment pipeline only | Production-like (masked if PII) |
| `prod` | Live | Deployment pipeline only | Production |

## Source control

- Each **dev** workspace is connected to **GitHub** with **Fabric Git integration** ([ADR 0004](../adr/0004-github-for-source-control.md)).
- One repository per domain; each workspace maps to a folder (`/bronze`, `/silver`, `/gold`).
- This standards repo is separate and referenced from each domain repo's README.
- Fabric stores item definitions (notebooks, pipelines, semantic models). **Data is never committed.**

## Branching

- `main` = what is in `test`/`prod`. Protected: PR + 1 approval + checks.
- The dev workspace commits to a `dev` branch; open a PR from `dev` to `main` to release.
- Engineers build in the shared `<domain>-dev` workspace ([ADR 0005](../adr/0005-shared-dev-workspace.md)). Revisit when a second engineer joins.
- Reviewers use the [PR checklist](../templates/pr-checklist.md).

## Promotion

- Use **Fabric deployment pipelines** for dev → test → prod, one per domain named `dp_<domain>` ([ADR 0006](../adr/0006-fabric-deployment-pipelines.md)).
- Use **deployment rules** / parameterization so items point to the right lakehouse in each stage. No environment names hard-coded in notebooks.
- Deploy to prod only after test runs succeed end to end.
- Every prod deployment has a linked PR or release note.

## Testing

- Unit test transformation functions (pure PySpark functions) with small in-memory DataFrames. Keep business logic in functions, not inline cells, so it can be tested.
- Integration test: run the domain orchestration pipeline in `test` and check `logging.run_log` and `logging.dq_result`.
