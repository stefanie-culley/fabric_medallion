# Sample data — synthetic marketing analytics

Fake data for demos, tests and onboarding ([ADR 0010](../adr/0010-synthetic-marketing-sample-data.md)). No real people: IDs only, emails use the reserved `example.com` domain.

## Where the data comes from

The [`generate_sample_data`](../templates/notebooks/generate_sample_data.py) Fabric notebook writes these files straight into the `bronze` lakehouse's Files area. Output is the same every run (fixed seed). The CSV files here are a copy of its output, so you can browse the data without Fabric.

## Layout

Folders mirror `bronze/Files/`:
`<source_system>/<entity>/ingest_date=YYYY-MM-DD/<file>.csv`

## Time zones

Like real systems, the sources don't record UTC:

| Source | How times are recorded | Example |
|---|---|---|
| `ads` | Local time in the ad account's zone, **no offset** (`America/Los_Angeles`). `Date` is a day in that zone. | `2026-05-01 03:00:48` |
| `crm` | Local time in the CRM's zone, **no offset** (`America/New_York`) | `2026-07-01 02:02:21` |
| `web` | Visitor's local time **with offset** | `2026-07-21T15:01:29-05:00` |

Silver converts all of these to UTC ([ADR 0014](../adr/0014-utc-timestamps-with-offset.md)).

Event data is one file per month (2026-05 to 2026-10), which gives incremental loads six batches to process.

| File | Rows | Key | Contents |
|---|---|---|---|
| `ads/campaign` | 13 | `CampaignID` | Campaigns: name, channel, budget, start/end dates |
| `ads/ad_spend` | ~570 | `CampaignID` + `Date` | Daily impressions, clicks, spend (no rows for email campaigns) |
| `web/session` | ~20,100 | `SessionID` | Website visits in the visitor's local time with UTC offset (e.g. `2026-07-21T15:01:29-05:00`): traffic source, medium, campaign (blank = organic/direct), device |
| `crm/lead` | ~1,500 | `LeadID` | Sign-ups, each linked to a `SessionID` |
| `crm/conversion` | 300 | `ConversionID` | Leads that became customers: plan, revenue (USD) |

Funnel: campaign → ad_spend → session → lead → conversion.

## Deliberate data quality problems

These are there on purpose so Silver checks have something to catch. Don't "fix" them in the files.

| File | Problem | Expected handling |
|---|---|---|
| campaign | `CMP-002` channel is `" Paid Social "` instead of `paid_social` | Domain value check (warning) |
| campaign | `CMP-001` appears twice; the second row has a later `ModifiedDate` and higher budget | Dedup: latest wins |
| ad_spend | One row has negative `Spend` | Range check |
| ad_spend | One row has a US-style date (`MM/DD/YYYY`) | Cast check → quarantine |
| ad_spend | One exact duplicate row | Dedup |
| session | 100 exact duplicate rows | Dedup |
| session | 50 rows with blank `SessionID` | Business key not null → quarantine |
| session | 50 rows with `SessionStart = "not available"` | Cast check → quarantine |
| lead | 15 emails in upper case with spaces | Trim + lowercase |
| lead | 15 rows with blank `CountryCode` | Warning |
| lead | One duplicate row | Dedup |
| lead | Some `SessionID`s point to sessions whose ID was blanked | Referential check (warning) |
| conversion | One blank `Revenue` | Not-null check |
| conversion | One `LeadID` (`L99999`) that doesn't exist | Referential check (warning) |
