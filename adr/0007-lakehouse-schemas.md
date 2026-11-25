# ADR 0007 — Lakehouse schemas, lakehouses named by layer

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
Tables in a lakehouse can sit in one flat list or be grouped into schemas. Lakehouse names also needed a convention.

## Options considered
1. **Schemas enabled** — group tables by source (Bronze) or subject (Silver/Gold).
2. **No schemas** — flat list; grouping by name prefix (`erp_customer`).

## Decision
- Create every lakehouse with schemas enabled.
- Bronze schemas are per source system (`bronze.erp.customer`); Silver and Gold schemas are per subject (`silver.sales.customer`, `gold.sales.fct_sales`).
- Operational tables live in an `ops` schema (`ops.run_log`, `ops.dq_result`).
- Lakehouses are named `bronze`, `silver`, `gold` with no `lh_` prefix.

## Consequences
- Schemas must be chosen when a lakehouse is created; an existing lakehouse without schemas can't be switched on later.
- Table references use `<lakehouse>.<schema>.<table>`.
