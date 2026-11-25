# 02 — Layer Contracts

Each layer has a contract: what it **must** do, what it **must not** do, and the columns every table carries. A PR that breaks a contract is not merged.

## Bronze — "as received"

**Must**
- Store data exactly as delivered by the source: same columns, same values. Type conversion is limited to what's needed to write Delta (e.g. landing everything as string is allowed).
- Keep raw files under `Files/` in the Bronze lakehouse, by source and ingest date:
  `Files/<source_system>/<entity>/ingest_date=YYYY-MM-DD/<original_file_name>`
- Load the raw data into a Delta table under `Tables/` with the metadata columns below.
- Be **append-only**. Never update or delete rows, except under the retention policy or a legal deletion request.

**Must not**
- Apply business rules, filters, joins, or deduplication.
- Rename source columns, except to make them legal Delta column names (see [03 Naming](03-naming.md)).

**Required metadata columns**

| Column | Type | Meaning |
|---|---|---|
| `_ingested_at` | timestamp (UTC) | When this row was written to Bronze |
| `_source_system` | string | Source system code, e.g. `ads`, `crm`, `web` |
| `_source_file` | string | File path or API endpoint the row came from (null for DB extracts) |
| `_batch_id` | string | ID of the pipeline run that loaded the row |

**Retention:** Raw files in `Files/` are kept for **30 days**; Bronze Delta tables are kept indefinitely unless a source-specific policy says otherwise. Permanent sample data lives in the repo under `samples/` ([ADR 0009](../adr/0009-raw-file-retention-and-samples.md)).

## Silver — "clean and conformed"

**Must**
- Contain one table per business entity (campaign, lead, web session), not per source file.
- Apply correct data types, trim whitespace, standardize nulls and empty strings, and convert all timestamps to **UTC**.
- Sources without an offset are converted using the source's time zone from the ingestion config (`source_time_zone`). If the zone is unknown, keep `timestamp_ntz` and flag it; never guess.
- Where local time matters, keep the source's offset or time zone in a column next to the UTC timestamp: `<name>_offset` (e.g. `-05:00`) or `<name>_time_zone` (e.g. `America/New_York`) ([ADR 0014](../adr/0014-utc-timestamps-with-offset.md)).
- Deduplicate on the business key; the latest record by source timestamp wins.
- Rename columns to the team standard (`snake_case`, see [03 Naming](03-naming.md)).
- Use **MERGE** (upsert) on the business key for incremental loads.
- Use **SCD Type 2** for entities whose history matters (flag this in the table's documentation).
- Send rows that fail **blocking** quality checks to a quarantine table, not into the Silver table (see [05 Data quality](05-data-quality.md)).

**Must not**
- Contain aggregations or report-specific logic.
- Read from any source other than Bronze (and other Silver tables for conforming reference data).

**Required metadata columns**

| Column | Type | Meaning |
|---|---|---|
| `_record_hash` | string | Hash of business columns; used to detect changes |
| `_created_at` | timestamp (UTC) | When the row was first inserted into Silver |
| `_updated_at` | timestamp (UTC) | When the row was last changed in Silver |
| `_source_system` | string | Carried over from Bronze |
| `_batch_id` | string | Run that last touched the row |

SCD2 tables also have `valid_from`, `valid_to` (null = current) and `is_current`.

## Gold — "business ready"

**Must**
- Be modelled as **star schemas**: fact tables (events, named `<event>_<grain>`, e.g. `ad_spend_daily`) at a clearly documented grain, joined to dimension tables (things, e.g. `campaign`) by surrogate keys.
- Use integer or hash **surrogate keys** (`<entity>_key`) in dimensions; facts reference dimensions by these keys only.
- Include an unknown member row (key `-1`) in every dimension so facts never have null foreign keys.
- Apply business definitions (e.g. "qualified lead", "cost per acquisition") **once**, here, and document them.
- Be the only layer exposed to semantic models, reports, and external consumers.

**Must not**
- Read from Bronze.
- Contain PII unless the use case is approved and the table is secured accordingly (see [06 Security](06-security-and-governance.md)).

**Required metadata columns**

| Column | Type | Meaning |
|---|---|---|
| `_updated_at` | timestamp (UTC) | When the row was last written |
| `_batch_id` | string | Run that last touched the row |

## Table maintenance (all layers)

- Run `OPTIMIZE` on tables with frequent small writes at least weekly (or use Fabric table maintenance from the lakehouse).
- Run `VACUUM` with a retention of at least 7 days so time travel and concurrent readers keep working.
- Keep V-Order enabled (Fabric default) on Silver and Gold tables read by Power BI.
- Partition only tables over ~1 TB, and only by a low-cardinality column such as a date. Over-partitioning small tables hurts performance.
