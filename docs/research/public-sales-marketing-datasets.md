# Public sales and marketing datasets for sample data

Researched 2026-11-25. The goal is small, redistributable sample data for this public, MIT-licensed repo, to show bronze, silver and gold layers in Microsoft Fabric. Facts come from each dataset owner's own page, license file or release. Anything not confirmed there is marked **unverified**.

## Recommendation

1. **Contoso Data Generator V2, "csv-10k" ready-to-use set (SQLBI): use this as the primary sales sample.** Both the generator repo and the data repo are MIT-licensed, the data is synthetic, and the tool is built for Fabric/OneLake. The CSV set is a star schema: sales/orders/orderrows facts plus customer, product, store, date and currency-exchange dimensions, all with order/delivery dates. Most files in the 10k set are already under 400 KB. Two files are larger: `customer.csv` (23.9 MB) and `currencyexchange.csv` (1.3 MB). Filter `customer.csv` down to the 1,663 customers who appear in `orders.csv`, and filter `currencyexchange.csv` by date. MIT matches this repo's license.
2. **AdventureWorksDW CSVs in `microsoft/sql-server-samples` (MIT): use as a second option, or for marketing-flavoured tables.** It has more marketing-style tables than Contoso: `DimPromotion`, `DimSalesReason`/`FactInternetSalesReason`, `FactSurveyResponse` and `ProspectiveBuyer`. The drawbacks: the files are pipe-delimited with no header row, and the fact files are 11–30 MB, so you would need to cut a date-range subset.

Neither dataset has real ad-spend or web-session data. A marketing source with a clear license is **UCI Bank Marketing (CC BY 4.0)**. It is a single table of campaign contacts, so it works for a "campaign" side feed but not as a star schema. Attribution is required.

## Comparison

| Name | Contents | Size | Format | License | Redistributable in public repo | PII | Related tables / date col | Link |
|---|---|---|---|---|---|---|---|---|
| Contoso Data Generator V2 (csv-10k) | Sales, orders, order rows, customer, product, store, date, currency exchange | 5.4 MB .7z; 10k set ≈ 1,682 orders, 3,996 sales rows | CSV (also Parquet, Delta, .bak) | MIT | **Yes** | Synthetic ("fake customers"); source of the fake names **unverified** | Yes (8 tables) / OrderDate, DeliveryDate | [repo](https://github.com/sql-bi/Contoso-Data-Generator-V2-Data) |
| AdventureWorksDW (install-script CSVs) | ~29 Dim/Fact CSVs: internet and reseller sales, customer, product, promotion, sales reason, survey, quota, currency | Files from 29 B to 30 MB | Pipe-delimited, no header, UTF-8 | MIT | **Yes** | Fictional company data | Yes (star schema) / date keys | [folder](https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/adventure-works/data-warehouse-install-script) |
| Wide World Importers DW | Wholesale sales, purchasing, stock (Fabric tutorial uses its Parquet) | **unverified** | .bak / Parquet in Fabric tutorial blob | MIT (+ Natural Earth / data.gov pieces) | **Yes** (keep the attribution notes) | Fictional | Yes / yes | [Learn](https://learn.microsoft.com/en-us/sql/samples/wide-world-importers-what-is) |
| Olist Brazilian e-commerce | Orders, items, payments, reviews, customers, sellers, products, geolocation (~100k orders, 2016–2018) | 126 MB (Kaggle); CSVs 0.16–61 MB | CSV | **Conflicting:** MIT on Olist's GitHub repo; CC BY-NC-SA 4.0 on Kaggle | **Unclear** | Anonymised real data; free-text reviews by real customers | Yes (9 tables) / purchase timestamps | [GitHub](https://github.com/olist/work-at-olist-data), [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) |
| UCI Online Retail / Online Retail II | Invoice lines of a UK online retailer | 541,909 rows / 22.6 MB; 1,067,371 rows / 43.5 MB | XLSX | CC BY 4.0 | **Yes**, with attribution | Real transactions; CustomerID is a pseudonymous 5-digit ID | Single table (dims can be derived) / InvoiceDate | [I](https://archive.ics.uci.edu/dataset/352/online+retail), [II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) |
| UCI Bank Marketing | Telemarketing campaign contacts and outcomes | 45,211 rows; zip 999.8 KB | CSV (in zip) | CC BY 4.0 | **Yes**, with attribution | Real bank clients, no names; anonymisation not stated on the page | Single table / month and day only | [UCI](https://archive.ics.uci.edu/dataset/222/bank+marketing) |
| Maven Fuzzy Factory (toy store e-commerce) | Website sessions, pageviews, orders, returns, products | **unverified** (page says "30K+ orders from 400K+ sessions") | CSV | "Public Domain" label on the page | **Probably**, but the page metadata looks inconsistent | **unverified** | "Multiple tables" / **unverified** | [Maven](https://mavenanalytics.io/data-playground/toy-store-e-commerce-database) |
| Olist Marketing Funnel | ~8,000 MQLs and closed deals, 2017-06 to 2018-06 | 875 KB | CSV | CC BY-NC-SA 4.0 | **No** (NC, ShareAlike conflicts with MIT) | Anonymised | Yes / yes | [Kaggle](https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist) |
| GA4 obfuscated sample e-commerce | Google Merchandise Store GA4 events, 2020-11-01 to 2021-01-31 | **unverified** | BigQuery table | No license on the page | **Unclear** | Obfuscated | Event table / event date | [Google](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset) |
| Instacart 2017 | 3M+ grocery orders | — | CSV | Instacart Dataset Terms (non-commercial, no redistribution) | **No** | Anonymised | Yes | see Rejected |
| Tableau Superstore | Orders, returns, people | — | XLS | No dataset license found | **Unclear** | Fictional | Yes | see Rejected |

## Candidates

### Contoso Data Generator V2 (SQLBI)
- The generator produces "sample data, ready to be imported into PowerBI or Fabric OneLake". It outputs Parquet, Delta, CSV and more, and "Delta Table output can be directly used in Fabric LakeHouse without any conversion". The tool needs static files including "fake customers". Source: [generator README](https://github.com/sql-bi/Contoso-Data-Generator-V2).
- License: MIT, "Copyright (c) 2022 SQLBI" ([LICENSE](https://github.com/sql-bi/Contoso-Data-Generator-V2/blob/main/LICENSE)). The data repo [sql-bi/Contoso-Data-Generator-V2-Data](https://github.com/sql-bi/Contoso-Data-Generator-V2-Data) is also MIT, according to its GitHub license metadata.
- The [`ready-to-use-data` release](https://github.com/sql-bi/Contoso-Data-Generator-V2-Data/releases/tag/ready-to-use-data) offers sizes from 10K to 100M orders in csv, delta, parquet, bak and pbix. The `csv-10k.7z` archive is 5,409,141 bytes.
- Contents I checked in `csv-10k.7z` (line counts include the header):

  | File | Size | Lines |
  |---|---|---|
  | `sales.csv` | 333 KB | 3,997 |
  | `orderrows.csv` | 149 KB | 3,997 |
  | `orders.csv` | 78 KB | 1,682 |
  | `product.csv` | 371 KB | 2,518 |
  | `store.csv` | 6 KB | 75 |
  | `date.csv` | 188 KB | 1,827 |
  | `currencyexchange.csv` | 1.26 MB | 45,651 |
  | `customer.csv` | 23.9 MB | 104,991 |

- `OrderDate` runs from 2022-05-21 to 2026-03-21. Only 1,663 distinct customers appear in `orders.csv`.
- The customer rows hold realistic fake names, addresses, birthdays and occupations. The source of these fake identities is not documented: the [docs site](https://docs.sqlbi.com/contoso-data-generator/) only says "fake customers". It is **unverified** whether that upstream source puts any terms on them.
- Windows' built-in `tar.exe` can extract the `.7z` archives.

### AdventureWorksDW (Microsoft)
- The repo license is MIT ([license.txt](https://github.com/microsoft/sql-server-samples/blob/master/license.txt)). AdventureWorks is a sample database "originally published by Microsoft". `AdventureWorksDW` is the data-warehouse version ([README](https://github.com/microsoft/sql-server-samples/blob/master/samples/databases/adventure-works/README.md)).
- The [data-warehouse install script folder](https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/adventure-works/data-warehouse-install-script) has CSVs per table. Examples: `FactInternetSales.csv` is 11.7 MB, `FactResellerSales.csv` 14.0 MB, `FactProductInventory.csv` 30.3 MB, `DimCustomer.csv` 4.5 MB, `DimProduct.csv` 9.3 MB, `DimPromotion.csv` 4 KB, `DimSalesReason.csv` 247 B, `FactInternetSalesReason.csv` 778 KB and `FactSurveyResponse.csv` 186 KB.
- `instawdbdw.sql` loads the files with `FIELDTERMINATOR = '|'` and `CODEPAGE = '65001'`. I checked `DimPromotion.csv`: it is UTF-8, pipe-delimited, with no header row. Bronze ingestion would need the column list from the script.
- The README says dates were adjusted in the SQL Server 2025 release. The date range of the CSVs is **unverified**.

### Wide World Importers (Microsoft)
- WWI is a fictitious wholesale novelty goods importer. The WideWorldImportersDW database is a dimensional model. Terms of use point to the same MIT `license.txt`, and the page adds: "The sample database includes public data that's been loaded from data.gov and Natural Earth data." Source: [Learn](https://learn.microsoft.com/en-us/sql/samples/wide-world-importers-what-is).
- The Fabric lakehouse tutorial copies `WideWorldImportersDW/parquet` from the public blob `https://fabrictutorialdata.blob.core.windows.net/sampledata/` ([Learn tutorial](https://learn.microsoft.com/en-us/fabric/data-engineering/tutorial-lakehouse-data-ingestion)). File sizes and row counts are **unverified**. There is no CSV in that path.

### Olist Brazilian e-commerce
- Kaggle states the license as **CC BY-NC-SA 4.0**, a total size of 126,186,995 bytes, about 100k orders from 2016 to 2018, and "real commercial data, it has been anonymised". Company names in review text were replaced with Game of Thrones house names. Source: [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), read through the Kaggle API metadata.
- Olist's own GitHub repo [olist/work-at-olist-data](https://github.com/olist/work-at-olist-data) is **MIT** ("Copyright (c) 2019 @olist"). It contains the same nine CSV file names, for example `olist_orders_dataset.csv` (17.7 MB) and `olist_geolocation_dataset.csv` (61.3 MB).
- The owner publishes the data under two incompatible licenses. MIT from the owner's own repo is arguably a valid grant, but I would treat it as **unclear** without confirmation from Olist. The reviews also contain real customers' free text.

### UCI Online Retail / Online Retail II
- Both are CC BY 4.0. Online Retail I has 541,909 instances from 01/12/2010 to 09/12/2011 in a 22.6 MB XLSX ([UCI 352](https://archive.ics.uci.edu/dataset/352/online+retail)). Online Retail II has 1,067,371 instances from 01/12/2009 to 09/12/2011 in 43.5 MB ([UCI 502](https://archive.ics.uci.edu/dataset/502/online+retail+ii)).
- Each is a single table: Invoice, StockCode, Description, Quantity, InvoiceDate, Price, CustomerID and Country. You would derive customer, product and date dimensions in silver. It is real UK retailer data with pseudonymous customer IDs. Citation: Chen, D. (2015), doi:10.24432/C5BW33.

### UCI Bank Marketing
- CC BY 4.0, 45,211 instances, a 999.8 KB zip. It comes from "direct marketing campaigns (phone calls) of a Portuguese banking institution", May 2008 to November 2010 ([UCI 222](https://archive.ics.uci.edu/dataset/222/bank+marketing)).
- It is a single table with no names, and the page does not state whether the data was anonymised. It is useful as a campaign or response feed.

### Maven Analytics Data Playground
- The dataset pages show "License: Public Domain". Examples: [Toy Store E-Commerce (Maven Fuzzy Factory)](https://mavenanalytics.io/data-playground/toy-store-e-commerce-database), with website sessions, pageviews, orders and returns, and [Marketing Campaign Results](https://mavenanalytics.io/data-playground/marketing-campaign-results).
- The page metadata looked unreliable when I fetched it. Both pages showed "499 records / 25 fields", which contradicts their descriptions (2,240 customers; 30K+ orders), and the tags were off. I could not reach the site's terms page (it returned 404).
- Table names, sizes and PII status are **unverified**. Download a file and confirm the license on the page before using it.

## Rejected / unclear

- **Instacart Online Grocery Shopping 2017: rejected.** The dataset terms allow only non-commercial, as-is use and say "You will not provide, transmit or make available the Dataset to any third party". I read the terms from a copy hosted as a [GitHub gist](https://gist.github.com/jeremystan/582eba13d6ee27ed465c43dc78934700), because the original Instacart page was not reachable.
- **Olist Marketing Funnel: rejected.** It is CC BY-NC-SA 4.0 on Kaggle ([Kaggle](https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist)), and I found no MIT copy.
- **Olist Brazilian e-commerce: unclear.** Its license is MIT on GitHub but CC BY-NC-SA on Kaggle (see above). The files are also large, and the reviews are real customer text.
- **GA4 obfuscated sample (BigQuery): unclear.** The [Google page](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset) states no license. The BigQuery public dataset terms that would govern copying extracts into a repo were not checked (**unverified**). The data is nested event JSON, not CSV.
- **Tableau Superstore: unclear.** I found no license for the dataset itself on Tableau's [legal pages](https://www.tableau.com/legal). Many copies circulate on Kaggle with no clear provenance.
- **Contoso (V2) customer identities: minor caveat.** They are synthetic, but their upstream source is undocumented (see above).
- **data.gov / data.europa.eu: not evaluated in depth.** Licenses vary per dataset, and they rarely hold related sales or marketing tables.
- **Kaggle re-uploads in general** (Superstore, "marketing campaign", "ad spend" datasets): most list CC0 or similar, but the uploader usually does not own the underlying data. Treat their provenance as unclear unless the original owner publishes the license.
