# 03 — Naming Conventions

General rules: lowercase, `snake_case`, no spaces, ASCII only, no abbreviations unless listed in the glossary at the bottom. Names describe *what* something is, not *who* built it or *when*.

## Workspaces

`<domain>-<env>` — e.g. `marketing-dev`, `marketing-prod`. `<env>` is one of `dev`, `test`, `prod`.

Lakehouses in every workspace: `bronze`, `silver`, `gold`.

## Fabric items

| Item | Prefix | Example |
|---|---|---|
| Lakehouse | none — named by layer | `bronze`, `silver`, `gold` |
| Warehouse | `wh_` | `wh_gold_marketing` |
| Notebook | `nb_` | `nb_silver_campaign` |
| Data pipeline | `pl_` | `pl_ingest_ads`, `pl_orchestrate_marketing` |
| Dataflow Gen2 | `df_` | `df_ingest_budget_sheet` |
| Semantic model | `sm_` | `sm_marketing` |
| Report | `rpt_` | `rpt_campaign_performance` |
| Environment (Spark) | `env_` | `env_default` |
| Deployment pipeline | `dp_` | `dp_marketing` |
| Shortcut | same name as the target table/folder | `campaign` |

Notebook names include the layer and entity: `nb_<layer>_<entity>` (e.g. `nb_bronze_ads_campaign`, `nb_gold_fct_ad_spend`). Shared helper notebooks: `nb_util_<purpose>`.

## Tables

Lakehouse schemas are enabled ([ADR 0007](../adr/0007-lakehouse-schemas.md)). Full name: `<lakehouse>.<schema>.<table>`.

| Layer | Schema | Table pattern | Example |
|---|---|---|---|
| Bronze | `<source_system>` | `<source_entity>` | `bronze.ads.campaign`, `bronze.crm.lead` |
| Silver | `<subject>` | `<entity>` (singular) | `silver.marketing.campaign`, `silver.marketing.web_session` |
| Silver quarantine | `<subject>` | `<entity>_quarantine` | `silver.marketing.campaign_quarantine` |
| Gold dimension | `<subject>` | `dim_<entity>` | `gold.marketing.dim_campaign` |
| Gold fact | `<subject>` | `fct_<process>` | `gold.marketing.fct_ad_spend` |
| Gold aggregate | `<subject>` | `agg_<subject>_<grain>` | `gold.marketing.agg_spend_monthly` |
| Logging | `logging` | `<purpose>` | `bronze.logging.run_log`, `silver.logging.dq_result` |

## Columns

| Kind | Rule | Example |
|---|---|---|
| Surrogate key | `<entity>_key` | `campaign_key` |
| Business / natural key | `<entity>_id` | `campaign_id` |
| Boolean | `is_` / `has_` prefix | `is_active`, `has_discount` |
| Date | `_date` suffix | `spend_date` |
| Timestamp (UTC) | `_at` suffix | `shipped_at` |
| Amount | `_amount` suffix, currency in a separate column or in the name | `spend_amount`, `spend_amount_usd` |
| Count / quantity | `_count` / `_qty` | `click_count`, `lead_count` |
| Metadata | leading underscore | `_ingested_at`, `_batch_id` |

Bronze keeps source column names; only characters Delta doesn't allow (spaces, `,;{}()\n\t=`) are replaced with `_`.

## Glossary of allowed abbreviations

`id`, `qty`, `amt` (avoid — prefer `amount`), `pct`, `dim`, `fct`, `agg`, `utc`, `usd`/ISO currency codes. Add to this list by PR.
