# Template: Silver clean notebook  (silver_clean_<entity>)
# Copy into a Fabric notebook; each "# %%" block is one cell.
# Default lakehouse: silver (schemas enabled). Reads bronze by its full name in the same workspace.
# Contract: typed, UTC, deduplicated on business key, MERGE, quarantine for blocking data quality failures.
# See standards/02-layer-contracts.md and standards/05-data-quality.md
#
# Steps: standardize names (as text) -> run data quality checks -> convert types -> deduplicate -> MERGE

# %% [parameters]
batch_id = "manual"
source_table = "bronze.ads.campaign"   # <lakehouse>.<schema>.<table>
target_table = "marketing.campaign"    # <schema>.<table> in silver
business_key = ["campaign_id"]
full_refresh = False
max_fail_ratio = 0.05                  # fail the run if more than 5% of rows are quarantined

# %% Load the shared checks (in Fabric, %run must be alone in its cell)
%run data_quality_checks

# %%
from datetime import datetime, timezone
from delta.tables import DeltaTable
from pyspark.sql import DataFrame, Window, functions as F

spark.conf.set("spark.sql.session.timeZone", "UTC")  # all timestamps are UTC (standard 02)
started_at = datetime.now(timezone.utc)

# %% Entity-specific logic: edit these three parts per entity. Keep them pure functions so they can be unit tested.
def standardize(df: DataFrame) -> DataFrame:
    """Rename Bronze columns to Silver names and tidy text. Values stay as text so checks can see bad input."""
    return df.select(
        F.trim("CampaignID").alias("campaign_id"),
        F.trim("CampaignName").alias("campaign_name"),
        F.lower(F.trim("Channel")).alias("channel"),
        F.trim("Budget").alias("budget"),
        F.trim("StartDate").alias("start_date"),
        F.trim("EndDate").alias("end_date"),
        F.trim("ModifiedDate").alias("source_modified_at"),
        F.col("_source_system"),
    ).replace("", None)


checks = [
    not_null("campaign_id"),
    castable("budget", "decimal(18,2)"),
    in_range("budget", minimum=0),
    castable("start_date", "date"),
    castable("end_date", "date"),
    castable("source_modified_at", "timestamp"),
    allowed_values("channel", ["paid_search", "paid_social", "display", "email", "affiliate"]),
    # No unique() check: duplicates on the business key are expected and removed by deduplication below.
]


def convert_types(df: DataFrame) -> DataFrame:
    """Convert checked text to proper types. Timestamps are UTC."""
    return (
        df.withColumn("budget", F.col("budget").cast("decimal(18,2)"))
          .withColumn("start_date", F.to_date("start_date"))
          .withColumn("end_date", F.to_date("end_date"))
          .withColumn("source_modified_at", F.to_timestamp("source_modified_at"))
    )

# %% Read Bronze: only this batch unless full refresh
bronze = spark.read.table(source_table)
if not full_refresh:
    bronze = bronze.filter(F.col("_batch_id") == batch_id)
rows_read = bronze.count()

# %% Check, convert, deduplicate
valid, quarantined = run_checks(standardize(bronze), checks, table_name=target_table, batch_id=batch_id)

df = convert_types(valid)

# Latest record per business key wins
latest_first = Window.partitionBy(*business_key).orderBy(F.col("source_modified_at").desc_nulls_last())
df = df.withColumn("_row_number", F.row_number().over(latest_first)).filter("_row_number = 1").drop("_row_number")

# %% Quarantine
rows_quarantined = quarantined.count()
if rows_quarantined:
    (quarantined.withColumn("_quarantined_at", F.current_timestamp())
        .withColumn("_batch_id", F.lit(batch_id))
        .write.format("delta").mode("append").option("mergeSchema", "true")
        .saveAsTable(f"{target_table}_quarantine"))

if rows_read and rows_quarantined / rows_read > max_fail_ratio:
    raise ValueError(f"{rows_quarantined}/{rows_read} rows quarantined; above threshold {max_fail_ratio}")

# %% Add Silver metadata and MERGE
business_columns = [c for c in df.columns if not c.startswith("_")]
df = (
    df.withColumn("_record_hash", F.sha2(F.concat_ws("||", *[F.col(c).cast("string") for c in business_columns]), 256))
      .withColumn("_created_at", F.current_timestamp())
      .withColumn("_updated_at", F.current_timestamp())
      .withColumn("_batch_id", F.lit(batch_id))
)

if not spark.catalog.tableExists(target_table):
    df.write.format("delta").saveAsTable(target_table)
    rows_inserted, rows_updated = df.count(), 0
else:
    target = DeltaTable.forName(spark, target_table)
    match_on = " AND ".join(f"target.{k} = source.{k}" for k in business_key)
    update_columns = {c: f"source.{c}" for c in df.columns if c != "_created_at"}
    (target.alias("target").merge(df.alias("source"), match_on)
        .whenMatchedUpdate(condition="target._record_hash <> source._record_hash", set=update_columns)
        .whenNotMatchedInsertAll()
        .execute())
    metrics = target.history(1).select("operationMetrics").first()[0]
    rows_inserted = int(metrics.get("numTargetRowsInserted", 0))
    rows_updated = int(metrics.get("numTargetRowsUpdated", 0))

# %% Run log
log = spark.createDataFrame([(
    batch_id, None, f"silver_clean_{target_table.split('.')[-1]}", "silver", target_table,
    started_at, datetime.now(timezone.utc), "succeeded",
    rows_read, rows_inserted, rows_updated, 0, rows_quarantined, None,
)], "batch_id string, pipeline_name string, notebook_name string, layer string, target_table string, "
   "started_at timestamp, ended_at timestamp, status string, rows_read long, rows_inserted long, "
   "rows_updated long, rows_deleted long, rows_quarantined long, error_message string")
log.write.format("delta").mode("append").saveAsTable("logging.run_log")
