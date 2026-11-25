# Notebook: generate_sample_data
# Creates the synthetic marketing sample data (ADR 0010) as CSV files in the bronze lakehouse's Files area.
# Copy into a Fabric notebook named `generate_sample_data`; each "# %%" block is one cell.
# Default lakehouse: bronze. Output is the same every run (fixed seed).
#
# Layout: Files/<source_system>/<entity>/ingest_date=YYYY-MM-DD/<file>.csv
# Event data is one file per month; campaign is a single snapshot.
#
# Source time zones (like real systems, sources are not in UTC):
#   ads  - local time in the ad account's zone, no offset    (America/Los_Angeles)
#   crm  - local time in the CRM's zone, no offset           (America/New_York)
#   web  - visitor's local time WITH offset                  (e.g. 2026-07-21T15:01:29-05:00)
# Spark converts UTC to local time when writing, so no time zone library is needed.

# %% [parameters]
output_root = "/lakehouse/default/Files"   # default lakehouse (bronze) Files area
seed = 42

# %%
import random
import shutil
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from pyspark.sql import functions as F

spark.conf.set("spark.sql.session.timeZone", "UTC")

START = date(2026, 5, 1)
END = date(2026, 10, 31)
N_CAMPAIGNS = 12
N_SESSIONS = 20_000
N_LEADS = 1_500
N_CONVERSIONS = 300

ADS_TIME_ZONE = "America/Los_Angeles"
CRM_TIME_ZONE = "America/New_York"

rng = random.Random(seed)

# channel: (traffic_source, medium, daily impressions range, click-through rate, cost per click)
CHANNELS = {
    "paid_search": ("google", "cpc", (2_000, 6_000), 0.045, 1.80),
    "paid_social": ("facebook", "paid_social", (5_000, 15_000), 0.012, 0.95),
    "display": ("display_network", "display", (10_000, 30_000), 0.004, 0.60),
    "email": ("newsletter", "email", None, None, None),
    "affiliate": ("partner", "affiliate", (1_000, 3_000), 0.020, 1.20),
}
THEMES = ["Summer Launch", "Brand Awareness", "Retargeting", "Webinar Promo",
          "Back to School", "Holiday Preview"]
ORGANIC_SOURCES = [("google", "organic"), ("direct", "none"), ("linkedin", "referral"),
                   ("bing", "organic")]
DEVICES = ["desktop", "mobile", "tablet"]
# Visitor UTC offsets (minutes) and weights; sessions are recorded in the visitor's local time with offset.
VISITOR_OFFSETS = [(-480, 15), (-300, 45), (0, 15), (60, 15), (600, 10)]
COUNTRIES = ["US", "CA", "GB", "DE", "FR", "AU", "NL", "IE"]
PLANS = {"basic": 49.0, "pro": 149.0, "enterprise": 899.0}


def random_utc(day: date) -> datetime:
    return datetime(day.year, day.month, day.day, tzinfo=timezone.utc) + timedelta(seconds=rng.randint(0, 86_399))


def with_offset(ts: datetime, offset_minutes: int) -> str:
    """UTC instant -> local time with offset, e.g. 2026-05-01T09:15:00-05:00."""
    return ts.astimezone(timezone(timedelta(minutes=offset_minutes))).isoformat(timespec="seconds")


def month_end(d: date) -> date:
    return d.replace(day=monthrange(d.year, d.month)[1])


def days_between(a: date, b: date):
    for i in range((b - a).days + 1):
        yield a + timedelta(days=i)

# %% Build the data. Columns that become local time hold UTC datetimes until they're written.
def make_campaigns():
    channels = list(CHANNELS)
    rows = []
    for i in range(1, N_CAMPAIGNS + 1):
        channel = channels[(i - 1) % len(channels)]
        start = START + timedelta(days=rng.randint(0, 120))
        end = min(start + timedelta(days=rng.randint(30, 90)), END)
        budget = 2_000 if channel == "email" else rng.choice([10_000, 15_000, 25_000, 40_000])
        rows.append({
            "CampaignID": f"CMP-{i:03d}",
            "CampaignName": f"{rng.choice(THEMES)} - {channel.replace('_', ' ').title()}",
            "Channel": channel,
            "Budget": budget,
            "StartDate": start.isoformat(),
            "EndDate": end.isoformat(),
            "ModifiedDate": random_utc(START),
        })
    return rows


def make_ad_spend(campaigns):
    rows = []
    for c in campaigns:
        _, _, impression_range, click_rate, cost_per_click = CHANNELS[c["Channel"]]
        if impression_range is None:  # email has no paid media
            continue
        for day in days_between(date.fromisoformat(c["StartDate"]), date.fromisoformat(c["EndDate"])):
            impressions = rng.randint(*impression_range)
            clicks = max(0, round(impressions * click_rate * rng.uniform(0.7, 1.3)))
            spend = round(clicks * cost_per_click * rng.uniform(0.85, 1.15), 2)
            rows.append({
                "CampaignID": c["CampaignID"], "Date": day.isoformat(),  # date in the ad account's time zone
                "Impressions": impressions, "Clicks": clicks, "Spend": f"{spend:.2f}",
                "_day": day,
            })
    return rows


def make_sessions(campaigns):
    all_days = list(days_between(START, END))
    offsets, weights = zip(*VISITOR_OFFSETS)
    rows = []
    for i in range(1, N_SESSIONS + 1):
        day = rng.choice(all_days)
        active = [c for c in campaigns if c["StartDate"] <= day.isoformat() <= c["EndDate"]]
        if active and rng.random() < 0.55:
            c = rng.choice(active)
            source, medium = CHANNELS[c["Channel"]][:2]
            campaign_id = c["CampaignID"]
        else:
            source, medium = rng.choice(ORGANIC_SOURCES)
            campaign_id = ""
        ts = random_utc(day)
        rows.append({
            "SessionID": f"S{i:06d}",
            "SessionStart": with_offset(ts, rng.choices(offsets, weights)[0]),
            "TrafficSource": source, "Medium": medium, "CampaignID": campaign_id,
            "DeviceType": rng.choices(DEVICES, weights=[55, 40, 5])[0],
            "PageViews": max(1, int(rng.expovariate(1 / 3))),
            "DurationSeconds": int(rng.expovariate(1 / 150)),
            "_day": day, "_ts": ts,
        })
    return rows


def make_leads(sessions):
    candidates = [s for s in sessions if s["PageViews"] >= 2]
    picked = sorted(rng.sample(candidates, N_LEADS), key=lambda s: s["_ts"])
    rows = []
    for i, s in enumerate(picked, start=1):
        created = s["_ts"] + timedelta(minutes=rng.randint(1, 20))
        rows.append({
            "LeadID": f"L{i:05d}", "SessionID": s["SessionID"],
            "CreatedAt": created, "Email": f"lead{i:05d}@example.com",
            "CountryCode": rng.choice(COUNTRIES), "ModifiedDate": created,
            "_day": created.date(), "_ts": created,
        })
    return rows


def make_conversions(leads):
    end_ts = datetime(END.year, END.month, END.day, 23, 59, 59, tzinfo=timezone.utc)
    candidates = []
    for lead in leads:
        converted = lead["_ts"] + timedelta(days=rng.randint(1, 30), minutes=rng.randint(0, 600))
        if converted <= end_ts:
            candidates.append((lead, converted))
    picked = sorted(rng.sample(candidates, N_CONVERSIONS), key=lambda x: x[1])
    rows = []
    for i, (lead, converted) in enumerate(picked, start=1):
        plan = rng.choices(list(PLANS), weights=[60, 32, 8])[0]
        rows.append({
            "ConversionID": f"C{i:05d}", "LeadID": lead["LeadID"],
            "ConvertedAt": converted, "Plan": plan,
            "Revenue": f"{PLANS[plan]:.2f}", "Currency": "USD",
            "_day": converted.date(),
        })
    return rows


def add_messy_rows(campaigns, ad_spend, sessions, leads, conversions):
    """Deliberate data quality problems for Silver to catch. Documented in samples/README.md."""
    # campaign: inconsistent channel value; a re-sent row with a later ModifiedDate (dedup)
    campaigns[1]["Channel"] = " Paid Social "
    campaigns.append(dict(campaigns[0], Budget=campaigns[0]["Budget"] + 5_000,
                          ModifiedDate=random_utc(START + timedelta(days=45))))
    # ad_spend: negative spend; US-style date; exact duplicate
    ad_spend[10]["Spend"] = "-125.00"
    ad_spend[20]["Date"] = ad_spend[20]["_day"].strftime("%m/%d/%Y")
    ad_spend.append(dict(ad_spend[30]))
    # sessions (~1%): duplicates, missing SessionID, unparseable timestamp
    for s in rng.sample(sessions, 100):
        sessions.append(dict(s))
    for s in rng.sample(sessions, 50):
        s["SessionID"] = ""
    for s in rng.sample(sessions, 50):
        s["SessionStart"] = "not available"
    # leads: messy email casing/whitespace, missing country, duplicate
    for lead in rng.sample(leads, 15):
        lead["Email"] = f"  {lead['Email'].upper()} "
    for lead in rng.sample(leads, 15):
        lead["CountryCode"] = ""
    leads.append(dict(rng.choice(leads)))
    # conversions: missing revenue; orphan LeadID (referential check)
    conversions[5]["Revenue"] = ""
    conversions[6]["LeadID"] = "L99999"


campaigns = make_campaigns()
ad_spend = make_ad_spend(campaigns)
sessions = make_sessions(campaigns)
leads = make_leads(sessions)
conversions = make_conversions(leads)
add_messy_rows(campaigns, ad_spend, sessions, leads, conversions)

# %% Write CSV files. Spark converts UTC datetimes to each source's local time (no offset).
def write_csv(system, entity, ingest_date, filename, rows, local_time_zone=None):
    fields = [k for k in rows[0] if not k.startswith("_")]
    df = spark.createDataFrame([tuple(r[f] for f in fields) for r in rows], fields)
    for column, data_type in df.dtypes:
        if data_type == "timestamp":
            df = df.withColumn(column, F.date_format(F.from_utc_timestamp(column, local_time_zone), "yyyy-MM-dd HH:mm:ss"))
    folder = Path(output_root) / system / entity / f"ingest_date={ingest_date.isoformat()}"
    folder.mkdir(parents=True, exist_ok=True)
    df.toPandas().to_csv(folder / filename, index=False, lineterminator="\n")


def write_monthly(system, entity, rows, local_time_zone=None):
    by_month = {}
    for r in rows:
        by_month.setdefault(month_end(r["_day"]), []).append(r)
    for last_day, month_rows in sorted(by_month.items()):
        write_csv(system, entity, last_day, f"{entity}_{last_day:%Y-%m}.csv", month_rows, local_time_zone)


for system in ("ads", "web", "crm"):  # only folders this notebook owns
    shutil.rmtree(Path(output_root) / system, ignore_errors=True)

write_csv("ads", "campaign", START, "campaign.csv", campaigns, ADS_TIME_ZONE)
write_monthly("ads", "ad_spend", ad_spend)
write_monthly("web", "session", sessions)
write_monthly("crm", "lead", leads, CRM_TIME_ZONE)
write_monthly("crm", "conversion", conversions, CRM_TIME_ZONE)

for path in sorted(Path(output_root).glob("*/*/*/*.csv")):
    print(path.relative_to(output_root), sum(1 for _ in open(path, encoding="utf-8")) - 1, "rows")
