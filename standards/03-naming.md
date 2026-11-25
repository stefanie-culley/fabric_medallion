# 03 — Naming Conventions

General rules: lowercase, `snake_case`, no spaces, ASCII only, no abbreviations unless listed in the glossary at the bottom. Names describe *what* something is, not *who* built it or *when*.

## Workspaces

`<domain>-<env>` — e.g. `sales-dev`, `sales-prod`. `<env>` is one of `dev`, `test`, `prod`.

Lakehouses in every workspace: `bronze`, `silver`, `gold`.

## Fabric items

| Item | Prefix | Example |
|---|---|---|
| Lakehouse | none — named by layer | `bronze`, `silver`, `gold` |
| Warehouse | `wh_` | `wh_gold_sales` |
| Notebook | `nb_` | `nb_silver_customer` |
| Data pipeline | `pl_` | `pl_ingest_erp`, `pl_orchestrate_sales` |
| Dataflow Gen2 | `df_` | `df_ingest_budget_sheet` |
| Semantic model | `sm_` | `sm_sales` |
| Report | `rpt_` | `rpt_sales_overview` |
| Environment (Spark) | `env_` | `env_default` |
| Deployment pipeline | `dp_` | `dp_sales` |
| Shortcut | same name as the target table/folder | `customer` |

Notebook names include the layer and entity: `nb_<layer>_<entity>` (e.g. `nb_bronze_erp_customer`, `nb_gold_fct_sales`). Shared helper notebooks: `nb_util_<purpose>`.

## Tables

Lakehouse schemas are enabled ([ADR 0007](../adr/0007-lakehouse-schemas.md)). Full name: `<lakehouse>.<schema>.<table>`.

| Layer | Schema | Table pattern | Example |
|---|---|---|---|
| Bronze | `<source_system>` | `<source_entity>` | `bronze.erp.customer`, `bronze.crm.opportunity` |
| Silver | `<subject>` | `<entity>` (singular) | `silver.sales.customer`, `silver.sales.sales_order` |
| Silver quarantine | `<subject>` | `<entity>_quarantine` | `silver.sales.customer_quarantine` |
| Gold dimension | `<subject>` | `dim_<entity>` | `gold.sales.dim_customer` |
| Gold fact | `<subject>` | `fct_<process>` | `gold.sales.fct_sales` |
| Gold aggregate | `<subject>` | `agg_<subject>_<grain>` | `gold.sales.agg_sales_monthly` |
| Logging | `logging` | `<purpose>` | `bronze.logging.run_log`, `silver.logging.dq_result` |

## Columns

| Kind | Rule | Example |
|---|---|---|
| Surrogate key | `<entity>_key` | `customer_key` |
| Business / natural key | `<entity>_id` | `customer_id` |
| Boolean | `is_` / `has_` prefix | `is_active`, `has_discount` |
| Date | `_date` suffix | `order_date` |
| Timestamp (UTC) | `_at` suffix | `shipped_at` |
| Amount | `_amount` suffix, currency in a separate column or in the name | `net_amount`, `net_amount_usd` |
| Count / quantity | `_count` / `_qty` | `line_count`, `order_qty` |
| Metadata | leading underscore | `_ingested_at`, `_batch_id` |

Bronze keeps source column names; only characters Delta doesn't allow (spaces, `,;{}()\n\t=`) are replaced with `_`.

## Glossary of allowed abbreviations

`id`, `qty`, `amt` (avoid — prefer `amount`), `pct`, `dim`, `fct`, `agg`, `utc`, `usd`/ISO currency codes. Add to this list by PR.
