# 01 — Architecture

## Principles

1. **Data flows one way:** Source → Bronze → Silver → Gold → consumers. A layer reads only from the layer directly below it (Gold may also read other Gold tables).
2. **Bronze is the system of record for what we received.** We can always rebuild Silver and Gold from Bronze.
3. **Every load is idempotent.** Re-running a load for the same window gives the same result.
4. **Delta everywhere.** All tables are Delta tables in OneLake. No other table format is used in Silver or Gold.
5. **Consumers only touch Gold.** Reports, semantic models, and external users never read Bronze or Silver directly.
6. **Everything is in Git.** If it isn't in source control, it doesn't exist.

## Layers at a glance

| | Bronze | Silver | Gold |
|---|---|---|---|
| **Purpose** | Land source data as received | Clean, typed, deduplicated, conformed entities | Business-ready models for analytics |
| **Shape** | Mirrors the source | One table per business entity | Star schemas (facts and dimensions), aggregates |
| **Write pattern** | Append-only | MERGE (upsert), SCD2 where required | Rebuild or MERGE |
| **Who reads it** | Data engineers | Data engineers, analytics engineers | Analysts, semantic models, reports |
| **Fabric item** | Lakehouse | Lakehouse | Lakehouse ([ADR 0002](../adr/0002-gold-on-lakehouse.md)) |

Full rules for each layer are in [02 Layer contracts](02-layer-contracts.md).

## Workspace topology

**One workspace per environment, one lakehouse per layer** ([ADR 0003](../adr/0003-workspace-per-environment.md)).

```
Domain: Sales
├── sales-dev    bronze  silver  gold  + notebooks, pipelines   (connected to Git)
├── sales-test   bronze  silver  gold  + notebooks, pipelines   (deployed)
└── sales-prod   bronze  silver  gold  + notebooks, pipelines   (deployed)
```

- A **domain** groups a business area's workspaces.
- A **workspace** holds one version of each item, so each environment needs its own.
- Changes move dev → test → prod with a Fabric deployment pipeline (see [07 DevOps](07-devops-and-environments.md)).
- Analysts who should only see Gold get item-level access to `gold`, not a workspace role.

## Item responsibilities

| Fabric item | Used for |
|---|---|
| Lakehouse | Storing Bronze/Silver/Gold Delta tables and raw files |
| Data pipeline (Data Factory) | Copying data from sources into Bronze; orchestrating notebooks |
| Notebook (PySpark / Spark SQL) | All transformations Bronze → Silver → Gold |
| Dataflow Gen2 | Only for low-volume, analyst-owned sources. Must still land in Bronze. |
| Warehouse | Not used by default; requires an ADR |
| Semantic model | Built on Gold (Direct Lake preferred) |
| Shortcut | Reading data already in OneLake/ADLS/S3 without copying. Shortcuts into Bronze are read-only sources, not a replacement for Bronze. |

## Cross-layer access

Notebooks in the Silver workspace read Bronze through **OneLake shortcuts** or by attaching the Bronze lakehouse — never by copying Bronze data into Silver's storage. The same applies Silver → Gold.

## Diagram

```
 Sources                Bronze                 Silver                 Gold                  Consumers
 ───────              ──────────             ──────────             ──────────             ─────────
 SQL DBs   ─┐        Files/ (raw)          cleansed entity       dim_* / fct_*         Semantic models
 APIs      ─┼─ pl_ ─▶ Tables/ (Delta,  ─nb_▶ tables (typed,   ─nb_▶ star schemas,   ──▶  Power BI reports
 Files     ─┤        append-only)          deduped, MERGE)       aggregates            SQL endpoint
 SaaS      ─┘        + _meta columns       + quarantine          + business logic      Exports
```
