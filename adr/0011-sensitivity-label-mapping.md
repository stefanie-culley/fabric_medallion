# ADR 0011 — Starter sensitivity label mapping

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
Fabric items can carry Microsoft Purview sensitivity labels. Organizations define their own labels, but teams adopting this standard need a sensible default to start from.

## Options considered
1. **Guidance only** — "apply your organization's labels"; nothing concrete.
2. **Starter mapping** — a default per layer and data type, replaced by the organization's own labels when they exist.

## Decision
Use this starter mapping, based on the common four-level scheme. Rename to your organization's labels where they differ.

| Label | Applies to |
|---|---|
| **Public** | Sample and synthetic data; outputs approved for external release |
| **General** | Gold tables, semantic models and reports with no personal data |
| **Confidential** | `bronze` and `silver` lakehouses (raw data may hold personal data); any Gold table with personal data |
| **Highly Confidential** | Special-category data (health, government IDs, financial account numbers). Not allowed on the platform without an approved use case |

## Consequences
- Label the lakehouse by its most sensitive table.
- Anything built from a labeled item (semantic model, report, export) carries at least the same label.
- Replace this mapping with the organization's own as soon as one exists.
