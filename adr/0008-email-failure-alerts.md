# ADR 0008 — Pipeline failure alerts by email

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
Pipeline failures must reach someone who can act on them.

## Options considered
1. **Email** — Office 365 Outlook activity on the pipeline's failure path; no extra setup.
2. **Microsoft Teams channel** — better visibility for a team; needs a channel and connection.

## Decision
Email. Every `pl_orchestrate_<domain>` pipeline has an Office 365 Outlook activity on its failure path, sent to the domain's alert address.

## Consequences
- The alert email includes pipeline name, run ID (`batch_id`), failed activity, and error message.
- Use a shared/team address, not a personal one, once more than one person supports the domain.
- Revisit (Teams) when a team shares support.
