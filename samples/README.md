# Sample data — synthetic marketing analytics

Fake data for demos, tests and onboarding ([ADR 0010](../adr/0010-synthetic-marketing-sample-data.md)). No real people: IDs only, emails use the reserved `example.com` domain.

Regenerate (same output every time):

```
python scripts/generate_sample_data.py
```

## Layout

Folders mirror `bronze/Files/`, so you can upload `samples/*` as-is:
`<source_system>/<entity>/ingest_date=YYYY-MM-DD/<file>.csv`

Event data is one file per month (2026-05 to 2026-10), which gives incremental loads six batches to process.

| File | Rows | Key | Contents |
|---|---|---|---|
| `ads/campaign` | 13 | `CampaignID` | Campaigns: name, channel, budget, start/end dates |
| `ads/ad_spend` | ~570 | `CampaignID` + `Date` | Daily impressions, clicks, spend (no rows for email campaigns) |
| `web/session` | ~20,100 | `SessionID` | Website visits: traffic source, medium, campaign (blank = organic/direct), device |
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
| session | 50 rows with `SessionStartUtc = "not available"` | Cast check → quarantine |
| lead | 15 emails in upper case with spaces | Trim + lowercase |
| lead | 15 rows with blank `CountryCode` | Warning |
| lead | One duplicate row | Dedup |
| lead | Some `SessionID`s point to sessions whose ID was blanked | Referential check (warning) |
| conversion | One blank `Revenue` | Not-null check |
| conversion | One `LeadID` (`L99999`) that doesn't exist | Referential check (warning) |
