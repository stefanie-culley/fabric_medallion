# Fabric item naming: UI support, Microsoft guidance, community practice

Researched 2026-11-25. The goal is to decide how this standard names Fabric items (notebooks, pipelines, lakehouses, semantic models, reports). Facts come from Microsoft Learn and Microsoft's own GitHub samples unless a section is labelled **community/opinion**. Anything not confirmed is marked **unverified**.

## Recommendation

1. **Microsoft has no official naming convention for Fabric items.** Its only naming guidance covers *workspaces*. Whatever this standard picks is a team choice, so write down the reason for it.
2. **A type prefix is optional.** The Fabric UI already shows the item type and can filter by type, and the item type is stored in Git and in the API. A prefix mainly helps alphabetical grouping in long lists.
3. **Apply the lakehouse character rule to every item:** start with a letter, use only letters, digits and `_`, and stay under 123 characters. This is the strictest documented rule, and it keeps names safe in Spark/SQL references and Git folder names.
4. **Keep the environment (dev/test/prod) out of item names.** Deployment pipelines pair items by name and type, so put the stage in the workspace name.
5. **Never give two items of the same type the same name in one workspace.** Items of *different* types can share a name.

## 1. Can the UI filter or sort by item type?

Yes.

- **Workspace list view.** The toolbar "contains a search box, filter, and the list view and lineage view selectors". The items list has "several columns" with key item information ([Workspaces](https://learn.microsoft.com/en-us/fabric/fundamentals/workspaces)). Fabric's general content-list guidance says: "Select **Filter** (upper-right of a content list) to refine results by type, time, and owner", with the example "Type (report, notebook)". You sort by selecting a column header, but "Not all columns are sortable" ([Fabric Home: search, filter, sort](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-home)). The workspace page text does not name a "Type" column; it is visible in screenshots and community posts only (**unverified** from text). Whether that column is sortable is also **unverified**.
- **OneLake catalog (explore tab).** The items list has columns Name, **Type**, Owner, Refreshed, Location, Endorsement and Sensitivity. You can narrow it with "the item type and tag selectors" and a workspace filter. The type selector works by category ("Data types", "Insight types"), not by single item type ([OneLake catalog explore](https://learn.microsoft.com/en-us/fabric/governance/onelake-catalog-explore)).
- **Elsewhere.** Global search finds items "by name, title, creator, tag, or workspace". The object explorer lets you "view items of a specific type or search for an item by a keyword". Open-item tabs show an "icon for the item type" ([Fabric Home](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-home)). The REST API [List Items](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-items) takes a `type` filter.

## 2. Does Microsoft recommend an item naming convention?

**No. I found no Microsoft Learn page that recommends type prefixes (`nb_`, `pl_`, `lh_`) or any other item naming pattern.**

### What Microsoft does say

- **Workspaces only.** [Tenant-level workspace planning](https://learn.microsoft.com/en-us/power-bi/guidance/powerbi-implementation-planning-workspaces-tenant-level-planning) has a "Workspace naming conventions" section: "Usually, naming conventions are a requirement and not a suggestion." It suggests a standard prefix ("*FIN-Quarterly Financials*") and a stage suffix: "We recommend appending *[Dev]* or *[Test]* suffixes but leaving production as a user-friendly name without a suffix." The checklist says to "Decide whether to create strict naming convention requirements or allow more flexible requirements". This section covers workspace names, not item names.
- **Medallion layout, not names.** [Medallion architecture in Fabric](https://learn.microsoft.com/en-us/fabric/onelake/onelake-medallion-lakehouse-architecture) says "Keep each layer separated in its own lakehouse or warehouse" and "we recommend that you create each lakehouse in its own, separate workspace". It gives no naming pattern.

### Hard rules that constrain names

- **Lakehouse:** "Lakehouse name must begin with a letter (A–Z or a–z) and may only contain alphanumeric characters and underscores thereafter. Special characters, spaces, and symbols are not permitted. The total length of the name must not exceed 123 characters." ([Create a lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/create-lakehouse))
- **Other item types:** the REST API says "The display name must follow naming rules according to item type". One of its errors is `ItemDisplayNameAlreadyInUse` ([Create Item](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/create-item)). I found no single page that lists the rules for each type (**unverified**). Notebooks, reports and semantic models do accept spaces; see the Microsoft samples below.
- **Table names:** the lakehouse tutorial says the Dataflow query name "is used as the table name in the lakehouse, so it must be lowercase and must not contain spaces" ([Lakehouse tutorial](https://learn.microsoft.com/en-us/fabric/data-engineering/tutorial-build-lakehouse)). A general table-name rule (characters, length) is **unverified**.
- **Description:** at most 256 characters ([Create Item](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/create-item)).

### Uniqueness: can a notebook and a lakehouse share a name?

- Items are identified by **name plus type**. Git folders are named `{display name}.{public facing type}`, and invalid characters are replaced with HTML numbers ([Git source code format](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format)). Deployment pipelines pair items on "Item Name", "Item Type" and folder location ([Assign a workspace](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/assign-pipeline)).
- **Different types can share a name.** Microsoft's own repos contain such pairs: `ABC.Report` with `ABC.SemanticModel` in [microsoft/fabric-cicd `sample/workspace`](https://github.com/microsoft/fabric-cicd/tree/main/sample/workspace), and `Bank Customer Churn Analysis.Report` with `.SemanticModel` in [microsoft/fabric-samples](https://github.com/microsoft/fabric-samples/tree/main/docs-samples/data-science/enrich-powerbi-report-with-machine-learning). A notebook and a lakehouse with the *same* name is not shown in any Microsoft source, so that specific combination is **unverified**.
- **Same name and same type causes problems.** "When you deploy a Power BI item for the first time, if another item in the target stage has the same name and type ... the deployment fails" ([Deployment process](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/understand-the-deployment-process)). Also: "If two or more items in the workspace to be paired have the same name, type and folder, pairing fails" ([Assign a workspace](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/assign-pipeline)).
- **Renaming after pairing:** "Once items are paired, renaming them *doesn't* unpair the items" (same page). After a workspace is connected to Git, renaming an item changes its Git folder name ([Git source code format](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format)).

### Names Microsoft uses in its own samples (no consistent pattern)

| Source | Names |
|---|---|
| [Lakehouse tutorial](https://learn.microsoft.com/en-us/fabric/data-engineering/tutorial-build-lakehouse) | `wwilakehouse`, `Customer Dimension Data` (dataflow), table `dimension_customer` |
| [fabric-samples cicd-local](https://github.com/microsoft/fabric-samples/tree/main/docs-samples/cicd/fabric-cicd-local/fabric_items) | `Contoso_LH` (lakehouse), `Notebook_1` |
| [fabric-samples churn analysis](https://github.com/microsoft/fabric-samples/tree/main/docs-samples/data-science/enrich-powerbi-report-with-machine-learning) | `BankCustomerChurnLakehouse`, `00 - Ingest Churn Data as Semantic Model` (notebook), `Bank Customer Churn Analysis` (report and semantic model) |
| [fabric-cicd sample workspace](https://github.com/microsoft/fabric-cicd/tree/main/sample/workspace) | `Diabetes_LH`, `Test_WH`, `Hello World` (notebook), `Run Hello World` (pipeline), `World` (environment) |
| [fabric-samples community: metadata-driven ingestion](https://github.com/microsoft/fabric-samples/tree/main/community-samples/Metadata-driven%20Ingestion%20Framework) | `PL_DynamicIngestionPipelineFullLoad_PGSQL` (community-contributed) |

The samples mix three styles: a type *suffix* (`_LH`, `_WH`, `...Lakehouse`), plain names with spaces, and, in one community sample, a `PL_` prefix. This is evidence of habit, not guidance.

## 3. Common practice (community/opinion)

Everything in this section is **community/opinion**, not Microsoft guidance.

- **Camp A: type prefix first.**
  - [Data Mozart, "The Name Game"](https://data-mozart.com/the-name-game-naming-microsoft-fabric-from-tenant-to-table/) (Nikola Ilic, updated 2026-04) uses `<type>_<project>_<purpose>`: `lh_sales_curated`, `sm_sales_executive`, `rpt_sales_executive_overview`. For code items it adds a layer: `pl_sales_bronze_pos_ingest`, `nb_sales_silver_transform`. Reasons: the prefix makes "the item type sortable and instantly recognizable", and "Optimize for sorting, not for English". It also says never to give a lakehouse and its semantic model the same name, and to keep version suffixes (`v2`, `FINAL`) out of names.
  - Fabric community forum answers suggest the same short codes (`lh_`, `wh_`, `pl_`, `df_`, `nb_`) and point to the Azure Cloud Adoption Framework abbreviation list as a starting point. I saw these only in search snippets because the forum blocked direct fetches (**unverified** wording).
- **Camp B: workload + type + order + layer.**
  - [Advancing Analytics, "What's in a name?"](https://www.advancinganalytics.co.uk/blog/2023/8/16/whats-in-a-name-naming-your-fabric-artifacts) (Johnny Winter, 2023) uses `<experience>_<type>_<index>_<stage>_<description>`, for example `DE_LH_100_BRONZE_WideWorldImporters`. Reasons: items of the same experience and type "will always appear together", the 100/200/300 index orders steps, and the UI's monochrome icons are hard to scan. It applies the lakehouse character rule to all items. It also says reports and apps should "continue to have business friendly and intuitive names".
  - [XTIVIA](https://www.xtivia.com/blog/microsoft-fabric-resource-naming-conventions/) (2024) uses `project_experience_type_index_layer_purpose`, for example `customer360_de_lakehouse_200_silver`. It deliberately leaves the environment out "so that Fabric Deployment Pipelines can auto-pair resources by name". It says: "Microsoft has not released any Fabric naming conventions."
- **Camp C: plain descriptive names, at least for business-facing items.**
  - A forum user argues that prefixes are redundant because "you always see the type of the item in the view". Another forum post advises against prefixes on semantic models, reports, dashboards and apps. Both come from search snippets only (**unverified** wording).
  - Advancing Analytics (above) agrees for reports and apps. Microsoft's own samples mostly use plain names.

**Summary of the split:** engineering items (lakehouse, notebook, pipeline, dataflow, environment) often get a type prefix or suffix plus a layer. Consumer items (reports, apps, sometimes semantic models) usually get business-friendly names. Nobody recommends putting dev/test/prod in item names.

## Unverified

- Whether the workspace list view has a "Type" column, and whether it is sortable (seen in screenshots and community posts, not stated in the text).
- Whether a notebook and a lakehouse can share a name in one workspace. Report and semantic model pairs are confirmed.
- Character and length rules for item types other than lakehouses, and general rules for table names.
- The exact wording of the Fabric community forum posts (the forum returned 403, so they are cited from search snippets).
