# ADR 0003 — One workspace per environment, one lakehouse per layer

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
We need a layout for workspaces and lakehouses that keeps dev, test and prod separate and supports CI/CD.

## Options considered
1. **One workspace per environment, three lakehouses in each** — simple; works with deployment pipelines; layer access is controlled per lakehouse.
2. **One workspace per layer per environment** (9 workspaces) — strongest access isolation; more to manage.
3. **One lakehouse with bronze/silver/gold schemas** — simplest, but access can't be separated by layer.

## Decision
Option 1. Each Fabric **domain** (e.g. Sales) has three workspaces: `<domain>-dev`, `<domain>-test`, `<domain>-prod`. Each holds `bronze`, `silver`, `gold` plus notebooks and pipelines.

## Consequences
- Changes move dev → test → prod with a Fabric deployment pipeline; deployment rules repoint items to each stage's lakehouses.
- Only `<domain>-dev` is connected to Git.
- Workspace Viewers can see all three layers; analysts who must not see Bronze/Silver get item-level access to `gold` instead of a workspace role.
