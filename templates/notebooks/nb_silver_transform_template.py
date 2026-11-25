# Template: Silver transform notebook  (nb_silver_<entity>)
# Copy into a Fabric notebook; each "# %%" block is one cell.
# Default lakehouse: lh_silver. Bronze table available via shortcut (or attached lakehouse).
# Contract: typed, UTC, deduplicated on business key, MERGE, quarantine for blocking DQ failures.
# See standards/02-layer-contracts.md and standards/05-data-quality.md

# %% [parameters]
batch_id = "manual"
source_table = "erp_customer"       # Bronze table (shortcut name)
target_table = "customer"
business_key = ["customer_id"]
full_refresh = False
max_fail_ratio = 0.05               # fail the run if more than 5% of rows are quarantined

# %%
from datetime import datetime, timezone
from delta.tables import DeltaTable
from pyspark.sql import DataFrame, Window, functions as F

started_at = datetime.now(timezone.utc)

# %% Transformation logic — keep it in a pure function so it can be unit tested
def transform(df: DataFrame) -> DataFrame:
    """Map Bronze columns to the Silver entity. Edit per entity."""
    return df.select(
        F.trim(F.col("CustomerID")).alias("customer_id"),
        F.initcap(F.trim(F.col("Name"))).alias("customer_name"),
        F.upper(F.trim(F.col("Country"))).alias("country_code"),
        F.to_utc_timestamp(F.to_timestamp("ModifiedDate"), "UTC").alias("source_modified_at"),
        F.col("_source_system"),
    ).replace("", None)

def dq_split(df: DataFrame):
    """Return (valid, quarantined). Blocking rules only; warnings go to ops_dq_result."""
    rule = (
        F.when(F.col("customer_id").isNull(), F.lit("business_key_not_null"))
         .when(F.col("source_modified_at").isNull(), F.lit("modified_at_castable"))
    )
    flagged = df.withColumn("_dq_rule", rule)
    valid = flagged.filter(F.col("_dq_rule").isNull()).drop("_dq_rule")
    bad = flagged.filter(F.col("_dq_rule").isNotNull())
    return valid, bad

# %% Read Bronze: only this batch unless full refresh
bronze = spark.read.table(source_table)
if not full_refresh:
    bronze = bronze.filter(F.col("_batch_id") == batch_id)

rows_read = bronze.count()
df = transform(bronze)

# Deduplicate: latest record per business key wins
w = Window.partitionBy(*business_key).orderBy(F.col("source_modified_at").desc_nulls_last())
df = df.withColumn("_rn", F.row_number().over(w)).filter("_rn = 1").drop("_rn")

valid, bad = dq_split(df)

# %% Quarantine
rows_quarantined = bad.count()
if rows_quarantined:
    (bad.withColumn("_dq_message", F.lit(None).cast("string"))
        .withColumn("_quarantined_at", F.current_timestamp())
        .withColumn("_batch_id", F.lit(batch_id))
        .write.format("delta").mode("append").option("mergeSchema", "true")
        .saveAsTable(f"{target_table}_quarantine"))

if rows_read and rows_quarantined / rows_read > max_fail_ratio:
    raise ValueError(f"{rows_quarantined}/{rows_read} rows quarantined; above threshold {max_fail_ratio}")

# %% Add Silver metadata and MERGE
business_cols = [c for c in valid.columns if not c.startswith("_")]
valid = (
    valid.withColumn("_record_hash", F.sha2(F.concat_ws("||", *[F.col(c).cast("string") for c in business_cols]), 256))
         .withColumn("_created_at", F.current_timestamp())
         .withColumn("_updated_at", F.current_timestamp())
         .withColumn("_batch_id", F.lit(batch_id))
)

if not spark.catalog.tableExists(target_table):
    valid.write.format("delta").saveAsTable(target_table)
    rows_inserted, rows_updated = valid.count(), 0
else:
    tgt = DeltaTable.forName(spark, target_table)
    on = " AND ".join(f"t.{k} = s.{k}" for k in business_key)
    update_cols = {c: f"s.{c}" for c in valid.columns if c != "_created_at"}
    (tgt.alias("t").merge(valid.alias("s"), on)
        .whenMatchedUpdate(condition="t._record_hash <> s._record_hash", set=update_cols)
        .whenNotMatchedInsertAll()
        .execute())
    metrics = tgt.history(1).select("operationMetrics").first()[0]
    rows_inserted = int(metrics.get("numTargetRowsInserted", 0))
    rows_updated = int(metrics.get("numTargetRowsUpdated", 0))

# %% Run log
log = spark.createDataFrame([(
    batch_id, None, f"nb_silver_{target_table}", "silver", target_table,
    started_at, datetime.now(timezone.utc), "succeeded",
    rows_read, rows_inserted, rows_updated, 0, rows_quarantined, None,
)], "batch_id string, pipeline_name string, notebook_name string, layer string, target_table string, "
   "started_at timestamp, ended_at timestamp, status string, rows_read long, rows_inserted long, "
   "rows_updated long, rows_deleted long, rows_quarantined long, error_message string")
log.write.format("delta").mode("append").saveAsTable("ops_run_log")
