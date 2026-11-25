# ADR 0013 — Plain English names, no type codes

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
The first naming standard used type codes (`nb_`, `pl_`, `dp_`, `sm_`, `rpt_`) and abbreviations (`dim_`, `fct_`, `dq`). They are confusing to anyone new to the project. [Research](../docs/research/fabric-item-naming.md) found that Microsoft does not recommend an item naming convention, that Fabric shows each item's type and can filter by it, and that community practice is split between type prefixes and plain names.

## Options considered
1. **Type codes and abbreviations** — common in some community guides; sortable by prefix; needs a decoder.
2. **Plain English names** — readable by anyone; type comes from Fabric's icon and filter.

## Decision
Plain English names, as defined in [03 Naming](../standards/03-naming.md). Examples: `silver_clean_campaign` (notebook), `marketing_daily_run` (pipeline), `gold.marketing.ad_spend_daily` (fact table).

## Consequences
- Names use only letters, numbers and `_`, start with a letter, and never repeat within one item type in a workspace.
- Gold tables are named for what they hold; the table description states dimension or fact and the grain.
- Supersedes the item and table prefixes in earlier versions of 03 Naming.
