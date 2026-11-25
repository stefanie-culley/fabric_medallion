# ADR 0009 — 30-day raw file retention; sample data kept in the repo

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
Pipelines land raw source files in `bronze/Files/`. We need a retention period for those files, and a permanent set of sample data for demos, testing and onboarding.

## Options considered
1. **30 days** — cheapest; short window to reprocess from raw files.
2. **90 days** — longer reprocessing window; more storage.
3. **Forever** — full replay from original files; storage keeps growing.

## Decision
- Raw files landed by pipelines in `bronze/Files/` are deleted after **30 days**. Bronze Delta tables are kept, so data can still be rebuilt from Bronze.
- A small set of **sample files** lives in the repo under `samples/`, organized like `bronze/Files/` (`samples/<source_system>/<entity>/`). They are uploaded to `bronze/Files/` for demos and tests and never expire.

## Consequences
- Reprocessing from raw files is only possible for the last 30 days; older reloads use the Bronze tables.
- Sample files must be fake or public data, contain no PII, and stay small (under ~1 MB each).
