# 04 — Ingestion & Orchestration

## Choosing a tool

| Need | Use |
|---|---|
| Copy from a database, file share, SaaS app, or API into Bronze | **Data pipeline** with Copy activity |
| Data already in ADLS Gen2, S3, or another OneLake location | **Shortcut** (no copy), then a notebook to load into Bronze if we need history |
| Operational database that needs near-real-time replication | **Mirroring** (evaluate per source) |
| Any transformation Bronze → Silver → Gold | **Notebook** (PySpark or Spark SQL) |
| Small, analyst-owned source (e.g. a budget spreadsheet) | **Dataflow Gen2**, landing in Bronze |
| Scheduling and dependencies | **Data pipeline** orchestrating notebooks |

Transformations are not done in Copy activities or Dataflows beyond what's needed to land the data.

## Load patterns

| Pattern | When | How |
|---|---|---|
| Full load | Small reference tables (< ~1M rows) or sources without a reliable change column | Bronze: append whole extract with new `_batch_id`. Silver: MERGE on business key, then handle deletes (rows missing from the latest batch). |
| Incremental (watermark) | Source has a reliable `modified_at` or increasing ID | Store the high watermark in `ops_watermark`; extract `> last watermark`; update the watermark **only after** the Silver load succeeds. |
| Change data capture | Source provides CDC or change tracking | Land change records in Bronze; apply inserts/updates/deletes in Silver via MERGE. |

## Idempotency rules

- Every run gets a `_batch_id` (use the pipeline run ID).
- Silver and Gold writes use MERGE or overwrite-by-partition, never blind append.
- A notebook re-run with the same parameters must not create duplicates.
- Watermarks move forward only after downstream writes commit.

## Metadata-driven ingestion

Once a domain has more than ~5 source tables, ingestion is driven by a control table instead of one pipeline per table:

`ops_ingest_config`: `source_system`, `source_object`, `target_table`, `load_pattern`, `watermark_column`, `business_key`, `is_enabled`, `schedule_group`

A single parameterized pipeline (`pl_ingest_<source_system>`) loops over enabled rows with a ForEach activity.

## Orchestration

- One orchestration pipeline per domain: `pl_orchestrate_<domain>`. It calls, in order: ingest pipelines → Silver notebooks → Gold notebooks → semantic model refresh (if not Direct Lake).
- Independent entities in the same layer run in parallel; layers run in sequence.
- Notebooks take parameters (`batch_id`, `load_date`, `full_refresh`) from a parameter cell, never hard-coded values.
- Retries: 2 retries with 5-minute interval on Copy and notebook activities.
- Failures alert the owning team (Teams/email activity on the failure path, or Fabric Activator). **DECIDE** the alert channel.

## Logging

Every notebook writes one row per run to `ops_run_log`:

`batch_id`, `pipeline_name`, `notebook_name`, `layer`, `target_table`, `started_at`, `ended_at`, `status`, `rows_read`, `rows_inserted`, `rows_updated`, `rows_deleted`, `rows_quarantined`, `error_message`

The templates in [templates/notebooks/](../templates/notebooks/) include this.

## Spark settings

- Use a shared Spark **Environment** (`env_default`) for library versions; don't `%pip install` in production notebooks.
- Start with the starter pool; move to a custom pool only with evidence (run times, failures).
