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

### Sources without an offset
Most sources record local clock time with no offset (e.g. `2026-05-01 09:15:00`).
- Find the source's time zone from the system's settings or documentation. It is usually one zone per source.
- Record it per source as an IANA name (`source_time_zone`, e.g. `America/New_York`) in the ingestion config, not hard-coded in notebooks.
- Silver converts to UTC with that zone (`to_utc_timestamp`) and, where local time matters, stores the zone in `<name>_time_zone`.
- If nobody knows the zone, **don't guess**: keep the value as `timestamp_ntz` (no time zone) and flag it in the table documentation.

## Consequences
- Joins and sorting always use the UTC column.
- Prefer `_time_zone` over `_offset` when the source provides it: it handles daylight saving time correctly for derived dates.
