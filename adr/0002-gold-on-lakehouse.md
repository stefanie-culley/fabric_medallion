# ADR 0002 — Gold layer uses a Lakehouse

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
Gold could be stored in a Fabric Lakehouse or a Fabric Warehouse.

## Options considered
1. **Lakehouse** — same item type and tooling (Spark notebooks) as Bronze and Silver; Direct Lake semantic models; read-only SQL endpoint for analysts.
2. **Warehouse** — full T-SQL read/write; better fit for SQL-first teams.

## Decision
Gold uses a Lakehouse (`gold`).

## Consequences
- All layers are built with Spark notebooks; one skill set and one pattern.
- Analysts query Gold through the read-only SQL analytics endpoint; they can't write tables there.
- A Warehouse can be added later for a specific use case via a new ADR.
