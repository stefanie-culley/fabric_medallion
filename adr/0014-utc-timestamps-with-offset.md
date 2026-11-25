# ADR 0014 — UTC timestamps, with an offset column where local time matters

- **Status:** Accepted
- **Date:** 2026-11-25
- **Deciders:** Data team

## Context
SQL Server has `datetimeoffset`, which stores a time together with its UTC offset. Spark and Delta (Fabric lakehouses) have no equivalent: `timestamp` stores an instant in UTC and drops the offset; `timestamp_ntz` has no time zone at all. Some analysis needs the source's local time (e.g. "what hour of their day did people convert?").

## Options considered
1. **UTC only** — simple; local time is lost after Bronze.
2. **UTC plus a separate offset or time zone column** where local time matters.

## Decision
- All timestamps in Silver and Gold are `timestamp` in UTC.
- Where local time matters, Silver adds a column next to the UTC timestamp:
  - `<name>_offset` (string, e.g. `-05:00`) when the source gives an offset
  - `<name>_time_zone` (string, IANA name, e.g. `America/New_York`) when the source gives a time zone
- Bronze keeps the original text as received, so the offset is never lost.
- Gold derives local values (e.g. `local_hour`) from the UTC timestamp and the offset or time zone.

## Consequences
- Joins and sorting always use the UTC column.
- Prefer `_time_zone` over `_offset` when the source provides it: it handles daylight saving time correctly for derived dates.
