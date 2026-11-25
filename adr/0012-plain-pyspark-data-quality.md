# ADR 0012 — Data quality checks as plain PySpark functions

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
Data quality checks ([05 Data quality](../standards/05-data-quality.md)) can be written by hand or with a library.

## Options considered
1. **Plain PySpark functions** in a shared `nb_util_dq` notebook — no dependencies; easy to read and teach.
2. **A library** (Great Expectations, Soda, `pydeequ`) — richer features and reports; extra setup in a Fabric Spark Environment.

## Decision
Plain PySpark functions in `nb_util_dq`, loaded into transform notebooks with `%run nb_util_dq`.

## Consequences
- No extra libraries in the Spark Environment.
- Each check returns failing rows plus a result row for `logging.dq_result`, so every check is handled the same way.
- Revisit if the rule count or reporting needs outgrow hand-written checks.
