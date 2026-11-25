# PR Checklist — Fabric Medallion

Copy into the PR description and tick each item, or explain why it doesn't apply.

## Layer contract
- [ ] Each notebook reads only from the layer below (Gold may read Gold)
- [ ] Bronze: append-only, no business logic, metadata columns present
- [ ] Silver: types, UTC timestamps, dedup on business key, MERGE, metadata columns present
- [ ] Gold: star schema, documented grain, surrogate keys, unknown (`-1`) member

## Naming
- [ ] Items, tables, and columns follow [03 Naming](../standards/03-naming.md)

## Reliability
- [ ] Re-running with the same parameters gives the same result (idempotent)
- [ ] No hard-coded environment names, dates, or paths — parameters only
- [ ] Writes to `logging.run_log`
- [ ] Watermark updated only after a successful write

## Quality
- [ ] Data quality checks added for new tables (see [05 Data quality](../standards/05-data-quality.md))
- [ ] Ran end to end in a dev/feature workspace; run log attached or linked

## Security
- [ ] No secrets in code
- [ ] PII columns identified and handled
- [ ] Table documentation (owner, grain, sources, SLA) added or updated
