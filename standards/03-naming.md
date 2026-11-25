# 03 — Naming Conventions

Names must make sense to someone new to the project, without a decoder ([ADR 0013](../adr/0013-plain-english-names.md)).

General rules:
- Plain English words, lowercase, `snake_case`. No type codes (`nb_`, `pl_`), no abbreviations except those in the glossary.
- Only letters, numbers and `_`, starting with a letter (Fabric's rule for lakehouses, applied to every item).
- Names describe *what* something is or does, not *who* built it or *when*.
- No environment in item names; the workspace name carries it.
- Fabric shows each item's type as an icon and can filter by type, so the name doesn't need to.
- Two items of the same type in one workspace never share a name (deployment pipelines pair items by name and type).

## Workspaces

`<domain>-<env>`, e.g. `marketing-dev`, `marketing-prod`. `<env>` is one of `dev`, `test`, `prod`.

Lakehouses in every workspace: `bronze`, `silver`, `gold`.

## Fabric items

| Item | Pattern | Example |
|---|---|---|
| Lakehouse | the layer | `bronze`, `silver`, `gold` |
| Notebook (load to Bronze) | `bronze_load_<source>_<entity>` | `bronze_load_ads_campaign` |
| Notebook (Silver) | `silver_clean_<entity>` | `silver_clean_campaign` |
| Notebook (Gold) | `gold_build_<table>` | `gold_build_ad_spend_daily` |
| Notebook (shared helpers) | what it holds | `data_quality_checks` |
| Data pipeline (copy) | `copy_<source>_to_bronze` | `copy_ads_to_bronze` |
| Data pipeline (orchestration) | `<domain>_daily_run` | `marketing_daily_run` |
| Dataflow Gen2 | `load_<what>` | `load_budget_spreadsheet` |
| Semantic model | `<domain>_model` | `marketing_model` |
| Report | what it shows | `campaign_performance` |
| Spark environment | `<purpose>_spark_environment` | `default_spark_environment` |
| Deployment pipeline | `<domain>_deployment` | `marketing_deployment` |
| Shortcut | same name as the target table or folder | `campaign` |

## Tables

Lakehouse schemas are enabled ([ADR 0007](../adr/0007-lakehouse-schemas.md)). Full name: `<lakehouse>.<schema>.<table>`.

| Layer | Schema | Table pattern | Example |
|---|---|---|---|
| Bronze | `<source_system>` | `<source_entity>` | `bronze.ads.campaign`, `bronze.crm.lead` |
| Silver | `<subject>` | `<entity>` (singular) | `silver.marketing.campaign`, `silver.marketing.web_session` |
| Silver quarantine | `<subject>` | `<entity>_quarantine` | `silver.marketing.campaign_quarantine` |
| Gold: things (dimensions) | `<subject>` | `<entity>` (singular) | `gold.marketing.campaign` |
| Gold: events (facts) | `<subject>` | `<event>_<grain>` | `gold.marketing.ad_spend_daily` |
| Gold: summaries | `<subject>` | `<event>_<grain>` | `gold.marketing.ad_spend_monthly` |
| Logging | `logging` | `<purpose>` | `bronze.logging.run_log`, `silver.logging.data_quality_result` |

The table's description says whether it is a dimension or a fact and states its grain.

## Columns

| Kind | Rule | Example |
|---|---|---|
| Surrogate key | `<entity>_key` | `campaign_key` |
| Business / natural key | `<entity>_id` | `campaign_id` |
| Boolean | `is_` / `has_` prefix | `is_active`, `has_discount` |
| Date | `_date` suffix | `spend_date` |
| Timestamp (UTC) | `_at` suffix | `converted_at` |
| Amount | `_amount` suffix, currency in a separate column or in the name | `spend_amount`, `spend_amount_usd` |
| Count / quantity | `_count` / `_quantity` | `click_count`, `lead_count` |
| Metadata | leading underscore | `_ingested_at`, `_batch_id` |

Bronze keeps source column names; only characters Delta doesn't allow (spaces, `,;{}()\n\t=`) are replaced with `_`.

## Glossary of allowed abbreviations

`id`, `utc`, ISO currency codes (`usd`, `eur`). Add to this list by PR.
