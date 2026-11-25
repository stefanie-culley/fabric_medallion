# 08 — Trial & Cost

## Starting without a paid capacity

| Option | What you get | Limits |
|---|---|---|
| [Microsoft Fabric trial](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-trial) | Lakehouse, Data Factory, pipelines, notebooks, up to 1 TB OneLake storage | **60 days.** Availability depends on tenant settings. Items become inactive when it ends unless moved to a paid capacity. |
| [Azure free account](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account) | $200 credit for 30 days (new customers) plus some always-free services | Credits are not a plan for ongoing Fabric capacity. |
| Azure DevOps | Free for up to five users, unlimited private Git repos | — |
| [Microsoft Learn](https://learn.microsoft.com/en-us/training/browse/?products=fabric) | Free Fabric training and tutorials | — |

## Rules during the trial

1. **Connect the trial workspace to Git on day one.** When the trial ends, Fabric items go inactive; Git is how we keep the work.
2. Use the single-workspace layout (see [01 Architecture](01-architecture.md)) to keep things simple.
3. Use sample or public data. Don't load production PII into a trial.
4. Track trial start and end dates in the team calendar; review at day 45 whether to buy capacity.

## Cost awareness on paid capacity

- Fabric bills by **capacity (F SKU)**, not per item. Everything in workspaces on that capacity shares it.
- Pause dev/test capacities outside working hours if they're on separate capacities.
- Watch the **Fabric Capacity Metrics app** for throttling and which items use the most capacity units.
- Notebooks: stop sessions when done; set a session timeout.
- Prefer shortcuts over copying data that already lives in OneLake or ADLS.
