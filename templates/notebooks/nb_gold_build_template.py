# Template: Gold build notebook  (nb_gold_dim_<entity> / nb_gold_fct_<process>)
# Copy into a Fabric notebook; each "# %%" block is one cell.
# Default lakehouse: lh_gold. Silver tables available via shortcuts.
# Contract: star schema, surrogate keys, unknown member (-1), documented grain.
# See standards/02-layer-contracts.md

# %% [parameters]
batch_id = "manual"

# %%
from datetime import datetime, timezone
from pyspark.sql import functions as F

started_at = datetime.now(timezone.utc)

# %% Dimension: dim_customer
# Grain: one row per customer_id (SCD1). For SCD2 use valid_from/valid_to from Silver.
# Surrogate key: stable hash of the business key, so keys don't change between rebuilds.
customer = spark.read.table("customer")

dim_customer = customer.select(
    F.xxhash64("customer_id").alias("customer_key"),
    "customer_id",
    "customer_name",
    "country_code",
)

unknown = spark.createDataFrame(
    [(-1, "UNKNOWN", "Unknown", None)],
    "customer_key long, customer_id string, customer_name string, country_code string",
)

dim_customer = (
    dim_customer.unionByName(unknown)
    .withColumn("_updated_at", F.current_timestamp())
    .withColumn("_batch_id", F.lit(batch_id))
)

dim_customer.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("dim_customer")

# %% Fact: fct_sales
# Grain: one row per sales order line.
order_line = spark.read.table("sales_order_line")
dim = spark.read.table("dim_customer").select("customer_id", "customer_key")

fct_sales = (
    order_line.join(dim, "customer_id", "left")
    .select(
        "order_id",
        "order_line_number",
        F.coalesce("customer_key", F.lit(-1).cast("long")).alias("customer_key"),
        F.date_format("order_date", "yyyyMMdd").cast("int").alias("order_date_key"),
        "order_qty",
        "net_amount",
    )
    .withColumn("_updated_at", F.current_timestamp())
    .withColumn("_batch_id", F.lit(batch_id))
)

# %% Blocking DQ: grain must be unique
dupes = fct_sales.groupBy("order_id", "order_line_number").count().filter("count > 1").count()
if dupes:
    raise ValueError(f"fct_sales grain violated: {dupes} duplicate order lines")

fct_sales.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("fct_sales")
# For large facts, switch to MERGE or replaceWhere on a date range instead of full overwrite.

# %% Run log
rows = fct_sales.count()
log = spark.createDataFrame([(
    batch_id, None, "nb_gold_fct_sales", "gold", "fct_sales",
    started_at, datetime.now(timezone.utc), "succeeded",
    rows, rows, 0, 0, 0, None,
)], "batch_id string, pipeline_name string, notebook_name string, layer string, target_table string, "
   "started_at timestamp, ended_at timestamp, status string, rows_read long, rows_inserted long, "
   "rows_updated long, rows_deleted long, rows_quarantined long, error_message string")
log.write.format("delta").mode("append").saveAsTable("ops_run_log")
