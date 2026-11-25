# 05 — Data Quality

## Severity

| Severity | Effect |
|---|---|
| **Blocking** | Failing rows go to `<entity>_quarantine` and are not loaded. If more than the threshold fails (default 5% of the batch), the run fails. |
| **Warning** | Rows are loaded; the failure is logged to `logging.dq_result` and reviewed. |

## Minimum checks by layer

**Bronze** (run after landing)
- Row count > 0, unless the source is allowed to be empty (flag in config).
- Expected columns present (schema drift detection). New columns: warning. Missing columns: blocking.
- Freshness: the newest source timestamp is within the expected window.

**Silver** (run before the MERGE)
- Business key not null — blocking.
- Business key unique within the batch after dedup — blocking.
- Data types cast successfully (failed casts produce nulls; compare to source) — blocking.
- Domain values in an allowed list (status codes, country codes) — warning.
- Referential checks to other Silver entities — warning.

**Gold** (run after the build)
- Every fact foreign key resolves to a dimension row (including `-1` unknown) — blocking.
- Fact grain is unique — blocking.
- Reconciliation: key totals (e.g. sum of `spend_amount` per day) match Silver within tolerance — blocking for spend and budget metrics, warning otherwise.

## Quarantine tables

`<entity>_quarantine` has the same columns as the Silver input plus:
`_dq_rule`, `_dq_message`, `_quarantined_at`, `_batch_id`.

Quarantined rows are reviewed by the owning engineer. Fixed rows are reprocessed by re-running the Silver notebook for that batch. They are never edited in place.

## Results table

`logging.dq_result`: `batch_id`, `table_name`, `rule_name`, `severity`, `rows_checked`, `rows_failed`, `passed`, `checked_at`.

## Tooling

Checks are written as PySpark functions in the shared `nb_util_dq` notebook. **DECIDE** whether to adopt a library (e.g. Great Expectations, Soda, or `pydeequ`) once we have more than ~20 rules.
