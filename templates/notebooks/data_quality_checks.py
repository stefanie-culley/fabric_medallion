# Shared notebook: data_quality_checks
# Reusable data quality checks for Silver notebooks. See standards/05-data-quality.md and ADR 0012.
# Copy into a Fabric notebook named `data_quality_checks`; each "# %%" block is one cell.
#
# Use it from another notebook:
#
#     %run data_quality_checks
#
#     checks = [
#         not_null("campaign_id"),
#         unique(["campaign_id"]),
#         castable("start_date", "date"),
#         allowed_values("channel", ["paid_search", "paid_social", "display", "email", "affiliate"]),
#         in_range("budget", minimum=0),
#         exists_in("campaign_id", spark.read.table("silver.marketing.campaign"), "campaign_id"),
#     ]
#     valid_rows, quarantined_rows = run_checks(df, checks, table_name="marketing.campaign", batch_id=batch_id)
#
# Severity:
#   "blocking" - failing rows are removed from valid_rows and returned in quarantined_rows
#   "warning"  - rows stay in valid_rows; the failure is only logged
# Every check writes one row to logging.data_quality_result.

# %%
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Optional

from pyspark.sql import DataFrame, Window, functions as F

BLOCKING = "blocking"
WARNING = "warning"


@dataclass
class Check:
    rule_name: str                                  # e.g. "campaign_id_not_null"
    severity: str                                   # BLOCKING or WARNING
    message: str                                    # human-readable reason, stored with quarantined rows
    mark_failures: Callable[[DataFrame], DataFrame]  # adds a boolean column `_failed`


# %% The checks
def not_null(column: str, severity: str = BLOCKING) -> Check:
    """Fails rows where the column is null or blank."""
    return Check(
        f"{column}_not_null", severity, f"{column} is missing",
        lambda df: df.withColumn("_failed", F.col(column).isNull() | (F.trim(F.col(column).cast("string")) == "")),
    )


def unique(columns: list, severity: str = BLOCKING) -> Check:
    """Fails every row whose combination of columns appears more than once."""
    name = "_".join(columns)
    window = Window.partitionBy(*columns)
    return Check(
        f"{name}_unique", severity, f"{', '.join(columns)} is duplicated",
        lambda df: df.withColumn("_failed", F.count(F.lit(1)).over(window) > 1),
    )


def castable(column: str, data_type: str, severity: str = BLOCKING) -> Check:
    """Fails rows where a non-blank value can't be converted to data_type (e.g. "date", "timestamp", "decimal(18,2)")."""
    return Check(
        f"{column}_castable_to_{data_type.split('(')[0]}", severity, f"{column} is not a valid {data_type}",
        lambda df: df.withColumn(
            "_failed",
            F.col(column).isNotNull()
            & (F.trim(F.col(column).cast("string")) != "")
            & F.expr(f"try_cast(`{column}` AS {data_type})").isNull(),
        ),
    )


def allowed_values(column: str, values: list, severity: str = WARNING) -> Check:
    """Fails rows where a non-null value isn't in the allowed list."""
    return Check(
        f"{column}_allowed_values", severity, f"{column} is not one of the allowed values",
        lambda df: df.withColumn("_failed", F.col(column).isNotNull() & ~F.col(column).isin(values)),
    )


def in_range(column: str, minimum: Optional[float] = None, maximum: Optional[float] = None,
             severity: str = BLOCKING) -> Check:
    """Fails rows where a numeric value is below minimum or above maximum. Nulls pass (use not_null for those)."""
    value = F.expr(f"try_cast(`{column}` AS double)")
    too_low = value < minimum if minimum is not None else F.lit(False)
    too_high = value > maximum if maximum is not None else F.lit(False)
    return Check(
        f"{column}_in_range", severity, f"{column} is outside {minimum} to {maximum}",
        lambda df: df.withColumn("_failed", F.coalesce(too_low | too_high, F.lit(False))),
    )


def exists_in(column: str, reference: DataFrame, reference_column: str, severity: str = WARNING) -> Check:
    """Fails rows whose non-null value has no match in the reference table (e.g. a lead whose session doesn't exist)."""
    keys = reference.select(F.col(reference_column).alias("_reference_key")).distinct()

    def mark(df: DataFrame) -> DataFrame:
        return (
            df.join(keys, df[column] == keys["_reference_key"], "left")
              .withColumn("_failed", F.col(column).isNotNull() & F.col("_reference_key").isNull())
              .drop("_reference_key")
        )

    return Check(f"{column}_exists_in_{reference_column}", severity, f"{column} has no matching {reference_column}", mark)


# %% Run a list of checks
def run_checks(df: DataFrame, checks: list, table_name: str, batch_id: str,
               write_results: bool = True) -> tuple:
    """Run every check, log one result row per check, and split the data.

    Returns (valid_rows, quarantined_rows). Quarantined rows carry `_failed_rule` and
    `_failure_message` for the first blocking check they failed.
    """
    checked_at = datetime.now(timezone.utc)
    marked = df.withColumn("_failed_rule", F.lit(None).cast("string")) \
               .withColumn("_failure_message", F.lit(None).cast("string"))
    results = []

    for check in checks:
        marked = check.mark_failures(marked).cache()
        rows_checked = marked.count()
        rows_failed = marked.filter("_failed").count()
        results.append((batch_id, table_name, check.rule_name, check.severity,
                        rows_checked, rows_failed, rows_failed == 0, checked_at))
        if check.severity == BLOCKING:
            first_failure = F.col("_failed") & F.col("_failed_rule").isNull()
            marked = marked.withColumn("_failed_rule", F.when(first_failure, F.lit(check.rule_name)).otherwise(F.col("_failed_rule"))) \
                           .withColumn("_failure_message", F.when(first_failure, F.lit(check.message)).otherwise(F.col("_failure_message")))
        marked = marked.drop("_failed")

    if write_results and results:
        spark.createDataFrame(
            results,
            "batch_id string, table_name string, rule_name string, severity string, "
            "rows_checked long, rows_failed long, passed boolean, checked_at timestamp",
        ).write.format("delta").mode("append").saveAsTable("logging.data_quality_result")

    valid_rows = marked.filter(F.col("_failed_rule").isNull()).drop("_failed_rule", "_failure_message")
    quarantined_rows = marked.filter(F.col("_failed_rule").isNotNull())
    return valid_rows, quarantined_rows
