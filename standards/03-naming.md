# 03 — Naming Conventions

General rules: lowercase, `snake_case`, no spaces, ASCII only, no abbreviations unless listed in the glossary at the bottom. Names describe *what* something is, not *who* built it or *when*.

## Workspaces

`<domain>-<env>` — e.g. `sales-dev`, `sales-prod`. `<env>` is one of `dev`, `test`, `prod`.

Lakehouses in every workspace: `lh_bronze`, `lh_silver`, `lh_gold`.

## Fabric items

| Item | Prefix | Example |
|---|---|---|
| Lakehouse | `lh_` | `lh_bronze`, `lh_silver_sales` |
| Warehouse | `wh_` | `wh_gold_sales` |
| Notebook | `nb_` | `nb_silver_customer` |
| Data pipeline | `pl_` | `pl_ingest_erp`, `pl_orchestrate_sales` |
| Dataflow Gen2 | `df_` | `df_ingest_budget_sheet` |
| Semantic model | `sm_` | `sm_sales` |
| Report | `rpt_` | `rpt_sales_overview` |
| Environment (Spark) | `env_` | `env_default` |
| Deployment pipeline | `dp_` | `dp_sales` |
| Shortcut | same name as the target table/folder | `erp_customer` |

Notebook names include the layer and entity: `nb_<layer>_<entity>` (e.g. `nb_bronze_erp_customer`, `nb_gold_fct_sales`). Shared helper notebooks: `nb_util_<purpose>`.

## Tables

| Layer | Pattern | Example |
|---|---|---|
| Bronze | `<source_system>_<source_entity>` | `erp_customer`, `crm_opportunity` |
| Silver | `<entity>` (singular) | `customer`, `sales_order` |
| Silver quarantine | `<entity>_quarantine` | `customer_quarantine` |
| Gold dimension | `dim_<entity>` | `dim_customer`, `dim_date` |
| Gold fact | `fct_<process>` | `fct_sales`, `fct_inventory_snapshot` |
| Gold aggregate | `agg_<subject>_<grain>` | `agg_sales_monthly` |
| Ops / logging | `ops_<purpose>` | `ops_run_log`, `ops_dq_result` |

If lakehouse schemas are enabled, use a schema per source in Bronze (`erp.customer`) and per domain in Silver/Gold (`sales.customer`). **DECIDE** whether we enable lakehouse schemas.

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

`id`, `qty`, `amt` (avoid — prefer `amount`), `pct`, `dim`, `fct`, `agg`, `ops`, `utc`, `usd`/ISO currency codes. Add to this list by PR.
