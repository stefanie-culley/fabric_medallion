# ADR 0010 — Generate synthetic marketing analytics sample data

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
The repo needs permanent sample data ([ADR 0009](0009-raw-file-retention-and-samples.md)) for a marketing analytics use case: campaigns, channels, ad spend, web sessions, leads and conversions. [Research](../docs/research/public-sales-marketing-datasets.md) found few public marketing datasets with a license that allows redistribution in a public repo.

## Options considered
1. **Generate our own synthetic data** — no license risk; shaped to exercise Bronze/Silver/Gold.
2. **Public dataset** — real-world shape, but licenses unclear or single-table only (e.g. UCI Bank Marketing).

## Decision
A Fabric notebook, [`generate_sample_data`](../templates/notebooks/generate_sample_data.py), generates synthetic marketing data into the `bronze` lakehouse's Files area. A copy of its output is kept in `samples/` so the data can be browsed without Fabric. Five CSV files across three source systems:

| File | Contents |
|---|---|
| `samples/ads/campaign/` | Campaigns with channel, budget, start and end dates |
| `samples/ads/ad_spend/` | Daily impressions, clicks and spend per campaign |
| `samples/web/session/` | Website visits with traffic source and campaign |
| `samples/crm/lead/` | Sign-ups, each linked to a web session |
| `samples/crm/conversion/` | Leads that became customers, with revenue |

**Volume ("small"):** 12 campaigns over 6 months (2026-05-01 to 2026-10-31), about 20,000 web sessions, 1,500 leads and 300 conversions.

## Consequences
- The notebook uses a fixed random seed so output is the same every run.
- Generating in Fabric (not a local script) means Spark handles time zones, and the demo runs entirely in Fabric. Regenerating requires a Fabric workspace.
- Sources record local time, not UTC (see [samples/README.md](../samples/README.md#time-zones)).
- No real people: IDs only, and any emails use the reserved `example.com` domain.
- Files stay small (under ~1 MB each).
- The data can deliberately include messy rows (duplicates, nulls, bad dates) so Silver data quality rules have something to catch.
