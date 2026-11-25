# ADR 0004 — GitHub for source control

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
Fabric Git integration supports Azure DevOps and GitHub. This standard is meant to be shared publicly with the wider data community.

## Options considered
1. **GitHub** — public repos, wide visibility, GitHub Actions for automation.
2. **Azure DevOps** — free for up to five users; tighter Microsoft integration; less visible publicly.

## Decision
GitHub. This standards repo is public. Domain repos (actual pipelines) are private unless they contain no sensitive logic or data references.

## Consequences
- Dev workspaces connect to GitHub via Fabric Git integration.
- Automation, if needed beyond deployment pipelines, uses GitHub Actions.
- Nothing company-specific (names, connection details, real table names) goes into this public repo.
