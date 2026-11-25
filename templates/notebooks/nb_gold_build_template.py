# Template: Gold build notebook  (nb_gold_dim_<entity> / nb_gold_fct_<process>)
# Copy into a Fabric notebook; each "# %%" block is one cell.
# Default lakehouse: gold (schemas enabled). Reads silver by its full name in the same workspace.
# Contract: star schema, surrogate keys, unknown member (-1), documented grain.
# See standards/02-layer-contracts.md

# %% [parameters]
batch_id = "manual"

# %%
from datetime import datetime, timezone
from pyspark.sql import functions as F

started_at = datetime.now(timezone.utc)

# %% Dimension: dim_campaign
# Grain: one row per campaign_id (SCD1). For SCD2 use valid_from/valid_to from Silver.
# Surrogate key: stable hash of the business key, so keys don't change between rebuilds.
campaign = spark.read.table("silver.marketing.campaign")

dim_campaign = campaign.select(
    F.xxhash64("campaign_id").alias("campaign_key"),
    "campaign_id",
    "campaign_name",
    "channel",
)

unknown = spark.createDataFrame(
    [(-1, "UNKNOWN", "Unknown", "unknown")],
    "campaign_key long, campaign_id string, campaign_name string, channel string",
)

dim_campaign = (
    dim_campaign.unionByName(unknown)
    .withColumn("_updated_at", F.current_timestamp())
    .withColumn("_batch_id", F.lit(batch_id))
)

dim_campaign.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("marketing.dim_campaign")

# %% Fact: fct_ad_spend
# Grain: one row per campaign per day.
ad_spend = spark.read.table("silver.marketing.ad_spend")
dim = spark.read.table("marketing.dim_campaign").select("campaign_id", "campaign_key")

fct_ad_spend = (
    ad_spend.join(dim, "campaign_id", "left")
    .select(
        F.coalesce("campaign_key", F.lit(-1).cast("long")).alias("campaign_key"),
        F.date_format("spend_date", "yyyyMMdd").cast("int").alias("spend_date_key"),
        "impression_count",
        "click_count",
        "spend_amount",
    )
    .withColumn("_updated_at", F.current_timestamp())
    .withColumn("_batch_id", F.lit(batch_id))
)

# %% Blocking DQ: grain must be unique
dupes = fct_ad_spend.groupBy("campaign_key", "spend_date_key").count().filter("count > 1").count()
if dupes:
    raise ValueError(f"fct_ad_spend grain violated: {dupes} duplicate campaign-days")

fct_ad_spend.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("marketing.fct_ad_spend")
# For large facts, switch to MERGE or replaceWhere on a date range instead of full overwrite.

# %% Run log
rows = fct_ad_spend.count()
log = spark.createDataFrame([(
    batch_id, None, "nb_gold_fct_ad_spend", "gold", "marketing.fct_ad_spend",
    started_at, datetime.now(timezone.utc), "succeeded",
    rows, rows, 0, 0, 0, None,
)], "batch_id string, pipeline_name string, notebook_name string, layer string, target_table string, "
   "started_at timestamp, ended_at timestamp, status string, rows_read long, rows_inserted long, "
   "rows_updated long, rows_deleted long, rows_quarantined long, error_message string")
log.write.format("delta").mode("append").saveAsTable("logging.run_log")
