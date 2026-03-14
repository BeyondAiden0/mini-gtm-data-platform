"""
Generate lead activity data.
Activities track lead engagement with marketing campaigns (form fills, clicks, etc.).
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

ACTIVITY_TYPES = [
    "Form Fill", "Email Open", "Email Click", "Webinar Registration",
    "Webinar Attended", "Content Download", "Page Visit", "Ad Click",
    "Unsubscribe", "Email Bounce",
]


def generate_lead_activities(output_path: Path, leads: list, campaigns: list, num_activities: int = 30000):
    """Generate lead activity data linking leads to campaigns."""

    activities = []

    for activity_id in range(1, num_activities + 1):
        lead = random.choice(leads)
        campaign = random.choice(campaigns)

        activity_type = random.choices(
            ACTIVITY_TYPES,
            weights=[0.15, 0.25, 0.10, 0.08, 0.05, 0.12, 0.10, 0.08, 0.03, 0.04],
        )[0]

        # Activity date within campaign window
        try:
            campaign_start = datetime.fromisoformat(campaign["start_date"])
        except (ValueError, TypeError):
            campaign_start = datetime(2022, 1, 1)
        try:
            campaign_end = datetime.fromisoformat(campaign["end_date"])
        except (ValueError, TypeError):
            campaign_end = campaign_start + timedelta(days=30)

        campaign_duration = max(1, (campaign_end - campaign_start).days)
        activity_date = campaign_start + timedelta(
            days=random.randint(0, campaign_duration),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        # Ensure not in future beyond data range
        if activity_date > datetime(2024, 12, 31):
            activity_date = datetime(2024, 12, 31) - timedelta(days=random.randint(0, 30))

        # UTM source for web activities
        utm_source = None
        if activity_type in ("Page Visit", "Ad Click", "Form Fill"):
            utm_source = random.choice(["google", "linkedin", "facebook", "twitter", "direct", "referral", None])

        # Data quality issues
        # 3% chance of null activity type
        if random.random() < 0.03:
            activity_type = None

        # 2% chance of future timestamp
        if random.random() < 0.02:
            activity_date = datetime(2030, 3, 15, 14, 30)

        # 4% chance of null campaign_id
        campaign_id = None if random.random() < 0.04 else campaign["campaign_id"]

        activities.append({
            "activity_id": activity_id,
            "lead_id": lead["lead_id"],
            "campaign_id": campaign_id,
            "activity_type": activity_type,
            "activity_date": activity_date.isoformat(),
            "utm_source": utm_source,
        })

    # Write to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "activity_id", "lead_id", "campaign_id",
            "activity_type", "activity_date", "utm_source",
        ])
        writer.writeheader()
        writer.writerows(activities)

    print(f"Generated {len(activities)} lead activities -> {output_path}")
    return activities


if __name__ == "__main__":
    from generate_accounts import generate_accounts
    from generate_opportunities import generate_opportunities
    from generate_leads import generate_leads
    from generate_campaigns import generate_campaigns

    base = Path(__file__).parent.parent / "sources"
    accounts = generate_accounts(base / "postgres" / "accounts.csv")
    opps = generate_opportunities(base / "postgres" / "opportunities.csv", accounts)
    leads = generate_leads(base / "postgres" / "leads.csv", opps)
    campaigns = generate_campaigns(base / "postgres" / "campaigns.csv")
    generate_lead_activities(base / "postgres" / "lead_activities.csv", leads, campaigns)

