# ADR 0005 — Shared dev workspace

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
Engineers can build in one shared dev workspace or in personal feature workspaces, each connected to its own Git branch.

## Options considered
1. **Shared `<domain>-dev`** — one workspace to set up; fits a solo engineer or a trial.
2. **Personal feature workspaces** — no overwriting each other's work; more setup per person.

## Decision
One shared `<domain>-dev` workspace, connected to a `dev` branch through Fabric Git integration. Changes reach `main` by pull request from `dev`.

## Consequences
- Simple setup, works within a single Fabric trial.
- With more than one engineer, edits can collide. Revisit this ADR when a second engineer starts building.
