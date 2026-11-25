# Template: Bronze ingest notebook  (nb_bronze_<source_system>_<entity>)
# Copy into a Fabric notebook; each "# %%" block is one cell.
# Default lakehouse: bronze
# Contract: append-only, data as received, required metadata columns.
# See standards/02-layer-contracts.md

# %% [parameters]  -- mark this cell as the Parameters cell in Fabric
batch_id = "manual"                 # pipeline run ID, passed by pl_orchestrate_<domain>
load_date = "2026-01-01"            # ingest date (YYYY-MM-DD)
source_system = "ads"
source_entity = "campaign"
file_format = "csv"                 # csv | json | parquet
target_table = f"{source_system}.{source_entity}"   # <schema>.<table>

# %%
from datetime import datetime, timezone
from pyspark.sql import functions as F

started_at = datetime.now(timezone.utc)
raw_path = f"Files/{source_system}/{source_entity}/ingest_date={load_date}/"

# %% Read raw files exactly as received
reader = spark.read.format(file_format)
if file_format == "csv":
    reader = reader.option("header", "true").option("inferSchema", "false")  # keep as strings

df = reader.load(raw_path)

# Make column names legal for Delta without otherwise renaming them
for c in df.columns:
    safe = "".join("_" if ch in " ,;{}()\n\t=" else ch for ch in c)
    if safe != c:
        df = df.withColumnRenamed(c, safe)

# %% Add required metadata columns
df = (
    df.withColumn("_ingested_at", F.current_timestamp())
      .withColumn("_source_system", F.lit(source_system))
      .withColumn("_source_file", F.input_file_name())
      .withColumn("_batch_id", F.lit(batch_id))
)

# %% Idempotency: remove rows from a previous attempt of the same batch, then append.
# (Bronze is append-only across batches; this only cleans up a failed re-run of THIS batch.)
if spark.catalog.tableExists(target_table):
    spark.sql(f"DELETE FROM {target_table} WHERE _batch_id = '{batch_id}'")

rows_read = df.count()
if rows_read == 0:
    raise ValueError(f"No rows found in {raw_path}")  # remove if this source may be empty

(df.write.format("delta")
   .mode("append")
   .option("mergeSchema", "true")   # new source columns are allowed in Bronze; DQ flags them
   .saveAsTable(target_table))

# %% Run log  (logging.run_log in the default lakehouse)
log = spark.createDataFrame([(
    batch_id, None, f"nb_bronze_{source_system}_{source_entity}", "bronze", target_table,
    started_at, datetime.now(timezone.utc), "succeeded",
    rows_read, rows_read, 0, 0, 0, None,
)], "batch_id string, pipeline_name string, notebook_name string, layer string, target_table string, "
   "started_at timestamp, ended_at timestamp, status string, rows_read long, rows_inserted long, "
   "rows_updated long, rows_deleted long, rows_quarantined long, error_message string")
log.write.format("delta").mode("append").saveAsTable("logging.run_log")

notebookutils.notebook.exit(str(rows_read))
