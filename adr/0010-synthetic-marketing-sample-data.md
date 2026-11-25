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
A Python script in the repo generates synthetic marketing data into `samples/`.

## Consequences
- The script uses a fixed random seed so output is the same every run.
- No real people: IDs only, and any emails use the reserved `example.com` domain.
- Files stay small (under ~1 MB each).
- The data can deliberately include messy rows (duplicates, nulls, bad dates) so Silver data quality rules have something to catch.
