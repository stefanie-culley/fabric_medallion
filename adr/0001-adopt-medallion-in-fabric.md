# ADR 0001 — Adopt medallion architecture in Microsoft Fabric

- **Status:** Proposed
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
We need a consistent way to ingest, clean, and serve data in Microsoft Fabric so that pipelines built by different people look the same, can be reviewed against shared rules, and can be rebuilt from raw data when logic changes.

## Options considered
1. **Medallion (Bronze/Silver/Gold) on Fabric lakehouses** — Microsoft's recommended pattern for Fabric; clear separation of raw, cleansed, and business-ready data; Delta tables work across Spark, SQL endpoint, and Direct Lake.
2. **Single-layer warehouse with ELT in T-SQL** — simpler for SQL-only teams, but no preserved raw layer, and harder to reprocess.
3. **No standard** — fastest to start, inconsistent over time.

## Decision
Adopt option 1, as described in the standards in this repository.

## Consequences
- Data is stored more than once (Bronze, Silver, Gold). Accepted for the ability to reprocess and audit.
- Engineers need PySpark skills for Silver and Gold notebooks.
- Open decisions marked **DECIDE** in the standards need follow-up ADRs.
