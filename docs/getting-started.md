# Getting started: run this standard in a Fabric trial

This guide takes you from no Fabric account to sample data in Bronze and a clean `campaign` table in Silver. It takes about an hour.

What you need:
- A **work or school account** (Microsoft Entra ID). Personal addresses such as Gmail or Outlook.com can't start a Fabric trial. If you don't have one, see [Fabric trial](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-trial) for the options.
- A **GitHub account** and a copy (fork) of this repo.

## 1. Start the trial
1. Go to [app.fabric.microsoft.com](https://app.fabric.microsoft.com) and sign in with your work or school account.
2. Select your profile picture (top right) → **Start trial**, then confirm.
3. Note the end date (60 days). See [08 Trial & cost](../standards/08-trial-and-cost.md) for the rules during the trial.

## 2. Create the workspace
1. **Workspaces** → **New workspace**. Name it `marketing-dev`.
2. Under **Advanced**, choose the **Trial** license mode, then **Apply**.

The trial uses one workspace. Test and prod workspaces come later ([ADR 0003](../adr/0003-workspace-per-environment.md)).

## 3. Create the three lakehouses
In `marketing-dev`, select **New item** → **Lakehouse** three times. Name them `bronze`, `silver` and `gold`. Tick **Lakehouse schemas** if the option is shown ([ADR 0007](../adr/0007-lakehouse-schemas.md)).

## 4. Connect to GitHub on day one
When the trial ends, items go inactive. Git is how you keep the work.
1. In your fork on GitHub, create a branch named `dev`.
2. Create a fine-grained personal access token for the fork with **Contents: Read and write**.
3. In Fabric: workspace **settings** → **Git integration** → **GitHub**. Paste the token, then pick your fork, branch `dev` and folder `fabric`.
4. Select **Connect and sync**.

Changes reach `main` by pull request ([07 DevOps](../standards/07-devops-and-environments.md)).

## 5. Create the schemas
Create a notebook named `setup_schemas`, add the `bronze`, `silver` and `gold` lakehouses to it, and run:

```sql
%%sql
CREATE SCHEMA IF NOT EXISTS bronze.ads;
CREATE SCHEMA IF NOT EXISTS bronze.logging;
CREATE SCHEMA IF NOT EXISTS silver.marketing;
CREATE SCHEMA IF NOT EXISTS silver.logging;
CREATE SCHEMA IF NOT EXISTS gold.marketing;
CREATE SCHEMA IF NOT EXISTS gold.logging;
```

## 6. Add the notebooks
For each file below, create a notebook with the same name and copy the code in. Each `# %%` line starts a new cell. On the cell marked `[parameters]`, open the cell's **...** menu and select **Toggle parameter cell**.

| Notebook | From | Default lakehouse |
|---|---|---|
| `generate_sample_data` | [generate_sample_data.py](../templates/notebooks/generate_sample_data.py) | `bronze` |
| `data_quality_checks` | [data_quality_checks.py](../templates/notebooks/data_quality_checks.py) | none |
| `bronze_load_ads_campaign` | [bronze_load_template.py](../templates/notebooks/bronze_load_template.py) | `bronze` |
| `silver_clean_campaign` | [silver_clean_template.py](../templates/notebooks/silver_clean_template.py) | `silver` |

Set the default lakehouse in the notebook's **Explorer** pane: **Add data items** → pick the lakehouse.

## 7. Run it
1. **Run** `generate_sample_data`. Check that `bronze` → **Files** now has `ads`, `crm` and `web` folders.
2. In `bronze_load_ads_campaign`, set `load_date = "2026-05-01"`, then run it. Table `bronze.ads.campaign` should have 13 rows.
3. Run `silver_clean_campaign`. Table `silver.marketing.campaign` should have 12 rows: one duplicate is removed.
4. Check the logs:

```sql
%%sql
SELECT * FROM bronze.logging.run_log;
SELECT * FROM silver.logging.data_quality_result;
```

One warning is expected: a campaign with an unknown channel. See [samples/README.md](../samples/README.md) for every planted problem.

## 8. Commit
Workspace **Source control** → select the changed items → **Commit**. Then open a pull request from `dev` to `main` on GitHub.

## Next steps
- Add Silver notebooks for `ad_spend`, `session`, `lead` and `conversion`, then run the [Gold template](../templates/notebooks/gold_build_template.py).
- Wire the notebooks into a `marketing_daily_run` pipeline ([04 Ingestion](../standards/04-ingestion-and-orchestration.md)).
