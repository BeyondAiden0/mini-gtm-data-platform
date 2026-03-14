"""
Generate campaign data.
Campaigns represent marketing programs that generate leads and influence pipeline.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

CHANNELS = [
    "Paid Search", "Paid Social", "Organic Search", "Email",
    "Webinar", "Event", "Content Syndication", "Direct Mail",
    "Partner", "Referral",
]

CAMPAIGN_TYPES = [
    "Demand Gen", "Brand Awareness", "Product Launch",
    "Nurture", "ABM", "Event Promotion", "Thought Leadership",
]

CAMPAIGN_STATUSES = ["Active", "Completed", "Paused", "Draft"]

CAMPAIGN_NAME_TEMPLATES = [
    "{channel} - {type} - Q{q} {year}",
    "{type} Campaign - {channel}",
    "FY{year} {type} - {channel}",
]


_QUARTER_COST_MULT = {1: 1.25, 2: 1.0, 3: 1.25, 4: 0.85}

# Event campaigns cluster around conference months (Mar, Sep, Oct)
_EVENT_MONTH_WEIGHTS = [1, 1, 4, 1, 1, 1, 1, 1, 4, 4, 2, 1]


def generate_campaigns(output_path: Path, num_campaigns: int = 200):
    """Generate campaign data with seasonal spend patterns."""

    campaigns = []

    for campaign_id in range(1, num_campaigns + 1):
        channel = random.choice(CHANNELS)
        campaign_type = random.choice(CAMPAIGN_TYPES)

        # Event campaigns cluster around conference months
        if channel == "Event":
            year = random.randint(2020, 2024)
            month = random.choices(range(1, 13), weights=_EVENT_MONTH_WEIGHTS)[0]
            day = random.randint(1, 28)
            start_date = datetime(year, month, day)
        else:
            start_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1825))

        duration_days = random.randint(7, 120)
        end_date = start_date + timedelta(days=duration_days)

        quarter = (start_date.month - 1) // 3 + 1
        year = start_date.year

        template = random.choice(CAMPAIGN_NAME_TEMPLATES)
        name = template.format(channel=channel, type=campaign_type, q=quarter, year=year)

        status = random.choices(
            CAMPAIGN_STATUSES,
            weights=[0.30, 0.50, 0.10, 0.10],
        )[0]

        cost_ranges = {
            "Paid Search": (5000, 100000),
            "Paid Social": (3000, 80000),
            "Organic Search": (500, 5000),
            "Email": (200, 10000),
            "Webinar": (2000, 30000),
            "Event": (10000, 200000),
            "Content Syndication": (5000, 50000),
            "Direct Mail": (3000, 40000),
            "Partner": (1000, 20000),
            "Referral": (500, 10000),
        }
        cost = random.randint(*cost_ranges[channel])

        # Seasonal spend: Q1 and Q3 get bigger budgets, Q4 gets less
        cost = int(cost * _QUARTER_COST_MULT.get(quarter, 1.0))

        # Data quality issues
        # 5% chance of null cost
        if random.random() < 0.05:
            cost = None

        # 3% chance of negative cost
        if random.random() < 0.03 and cost is not None:
            cost = -cost

        # 2% chance of null channel
        if random.random() < 0.02:
            channel = None

        campaigns.append({
            "campaign_id": campaign_id,
            "name": name,
            "channel": channel,
            "type": campaign_type,
            "status": status,
            "cost": cost,
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "created_at": (start_date - timedelta(days=random.randint(1, 14))).isoformat(),
        })

    # Write to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "campaign_id", "name", "channel", "type", "status",
            "cost", "start_date", "end_date", "created_at",
        ])
        writer.writeheader()
        writer.writerows(campaigns)

    print(f"Generated {len(campaigns)} campaigns -> {output_path}")
    return campaigns


if __name__ == "__main__":
    output = Path(__file__).parent.parent / "sources" / "postgres" / "campaigns.csv"
    generate_campaigns(output)

