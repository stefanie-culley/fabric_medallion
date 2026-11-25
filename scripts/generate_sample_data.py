"""Generate synthetic marketing analytics sample data into samples/.

See adr/0010-synthetic-marketing-sample-data.md. Standard library only.
Output is deterministic (fixed seed): re-running gives identical files.

Layout mirrors bronze/Files:  samples/<source_system>/<entity>/ingest_date=YYYY-MM-DD/<file>.csv
Event data is split into one file per month; campaign is a single snapshot.

Usage:  python scripts/generate_sample_data.py
"""

import csv
import random
import shutil
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

SEED = 42
START = date(2026, 5, 1)
END = date(2026, 10, 31)
N_CAMPAIGNS = 12
N_SESSIONS = 20_000
N_LEADS = 1_500
N_CONVERSIONS = 300

OUT = Path(__file__).resolve().parent.parent / "samples"
rng = random.Random(SEED)

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
COUNTRIES = ["US", "CA", "GB", "DE", "FR", "AU", "NL", "IE"]
PLANS = {"basic": 49.0, "pro": 149.0, "enterprise": 899.0}


def iso(ts: datetime) -> str:
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def month_end(d: date) -> date:
    return d.replace(day=monthrange(d.year, d.month)[1])


def random_ts(day: date) -> datetime:
    return datetime(day.year, day.month, day.day, tzinfo=timezone.utc) + timedelta(
        seconds=rng.randint(0, 86_399))


def days_between(a: date, b: date):
    for i in range((b - a).days + 1):
        yield a + timedelta(days=i)


# ---------------------------------------------------------------- campaigns
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
            "ModifiedDate": iso(random_ts(START)),
        })
    return rows


# ---------------------------------------------------------------- ad spend
def make_ad_spend(campaigns):
    rows = []
    for c in campaigns:
        _, _, imp_range, ctr, cpc = CHANNELS[c["Channel"]]
        if imp_range is None:  # email has no paid media
            continue
        for day in days_between(date.fromisoformat(c["StartDate"]), date.fromisoformat(c["EndDate"])):
            impressions = rng.randint(*imp_range)
            clicks = max(0, round(impressions * ctr * rng.uniform(0.7, 1.3)))
            spend = round(clicks * cpc * rng.uniform(0.85, 1.15), 2)
            rows.append({
                "CampaignID": c["CampaignID"], "Date": day.isoformat(),
                "Impressions": impressions, "Clicks": clicks, "Spend": f"{spend:.2f}",
                "_day": day,
            })
    return rows


# ---------------------------------------------------------------- sessions
def make_sessions(campaigns):
    all_days = list(days_between(START, END))
    rows = []
    for i in range(1, N_SESSIONS + 1):
        day = rng.choice(all_days)
        active = [c for c in campaigns
                  if c["StartDate"] <= day.isoformat() <= c["EndDate"]]
        if active and rng.random() < 0.55:
            c = rng.choice(active)
            source, medium = CHANNELS[c["Channel"]][:2]
            campaign_id = c["CampaignID"]
        else:
            source, medium = rng.choice(ORGANIC_SOURCES)
            campaign_id = ""
        ts = random_ts(day)
        rows.append({
            "SessionID": f"S{i:06d}", "SessionStartUtc": iso(ts),
            "TrafficSource": source, "Medium": medium, "CampaignID": campaign_id,
            "DeviceType": rng.choices(DEVICES, weights=[55, 40, 5])[0],
            "PageViews": max(1, int(rng.expovariate(1 / 3))),
            "DurationSeconds": int(rng.expovariate(1 / 150)),
            "_day": day, "_ts": ts,
        })
    return rows


# ---------------------------------------------------------------- leads
def make_leads(sessions):
    candidates = [s for s in sessions if s["PageViews"] >= 2]
    picked = sorted(rng.sample(candidates, N_LEADS), key=lambda s: s["_ts"])
    rows = []
    for i, s in enumerate(picked, start=1):
        created = s["_ts"] + timedelta(minutes=rng.randint(1, 20))
        rows.append({
            "LeadID": f"L{i:05d}", "SessionID": s["SessionID"],
            "CreatedAtUtc": iso(created), "Email": f"lead{i:05d}@example.com",
            "CountryCode": rng.choice(COUNTRIES), "ModifiedDate": iso(created),
            "_day": created.date(), "_ts": created,
        })
    return rows


# ---------------------------------------------------------------- conversions
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
            "ConvertedAtUtc": iso(converted), "Plan": plan,
            "Revenue": f"{PLANS[plan]:.2f}", "Currency": "USD",
            "_day": converted.date(),
        })
    return rows


# ---------------------------------------------------------------- messy rows
def add_messy_rows(campaigns, ad_spend, sessions, leads, conversions):
    """Deliberate data quality problems for Silver to catch. Documented in samples/README.md."""
    # campaign: inconsistent channel value; a re-sent row with a later ModifiedDate (dedup)
    campaigns[1]["Channel"] = " Paid Social "
    updated = dict(campaigns[0], Budget=campaigns[0]["Budget"] + 5_000,
                   ModifiedDate=iso(random_ts(START + timedelta(days=45))))
    campaigns.append(updated)

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
        s["SessionStartUtc"] = "not available"

    # leads: messy email casing/whitespace, missing country, duplicate
    for lead in rng.sample(leads, 15):
        lead["Email"] = f"  {lead['Email'].upper()} "
    for lead in rng.sample(leads, 15):
        lead["CountryCode"] = ""
    leads.append(dict(rng.choice(leads)))

    # conversions: missing revenue; orphan LeadID (referential check)
    conversions[5]["Revenue"] = ""
    conversions[6]["LeadID"] = "L99999"


# ---------------------------------------------------------------- output
def write_monthly(system, entity, rows):
    by_month = {}
    for r in rows:
        by_month.setdefault(month_end(r["_day"]), []).append(r)
    for m_end, month_rows in sorted(by_month.items()):
        write_csv(system, entity, m_end, f"{entity}_{m_end:%Y-%m}.csv", month_rows)


def write_csv(system, entity, ingest_date, filename, rows):
    folder = OUT / system / entity / f"ingest_date={ingest_date.isoformat()}"
    folder.mkdir(parents=True, exist_ok=True)
    fields = [k for k in rows[0] if not k.startswith("_")]
    with open(folder / filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    campaigns = make_campaigns()
    ad_spend = make_ad_spend(campaigns)
    sessions = make_sessions(campaigns)
    leads = make_leads(sessions)
    conversions = make_conversions(leads)
    add_messy_rows(campaigns, ad_spend, sessions, leads, conversions)

    for system in ("ads", "web", "crm"):  # only folders this script owns
        shutil.rmtree(OUT / system, ignore_errors=True)

    write_csv("ads", "campaign", START, "campaign.csv", campaigns)
    write_monthly("ads", "ad_spend", ad_spend)
    write_monthly("web", "session", sessions)
    write_monthly("crm", "lead", leads)
    write_monthly("crm", "conversion", conversions)

    for path in sorted(OUT.rglob("*.csv")):
        rows = sum(1 for _ in open(path, encoding="utf-8")) - 1
        print(f"{path.relative_to(OUT)}  {rows} rows  {path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
