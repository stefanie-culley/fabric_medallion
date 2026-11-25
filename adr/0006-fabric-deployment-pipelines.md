# ADR 0006 — Fabric deployment pipelines for promotion

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
Changes must move from `<domain>-dev` to `<domain>-test` to `<domain>-prod`.

## Options considered
1. **Fabric deployment pipelines** — built in; Deploy button or API; deployment rules repoint items to each stage's lakehouses.
2. **`fabric-cicd` + GitHub Actions** — fully automated from Git; we write and maintain the automation.

## Decision
Fabric deployment pipelines. One pipeline per domain (`dp_<domain>`) with stages dev → test → prod.

## Consequences
- No CI/CD code to maintain.
- Deploys are manual (a person clicks Deploy), so every prod deploy needs a linked PR or release note.
- Revisit if deploys become frequent enough to want full automation.
