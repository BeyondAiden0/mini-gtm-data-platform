"""
Generate account data.
Accounts are foundational - opportunities, contacts, and leads reference them.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

INDUSTRIES = [
    "Technology", "Financial Services", "Healthcare", "Manufacturing",
    "Retail", "Media & Entertainment", "Education", "Government",
    "Telecommunications", "Energy", "Professional Services", "Transportation",
]

COMPANY_PREFIXES = [
    "Acme", "Global", "Pacific", "Apex", "Pinnacle", "Summit", "Nova",
    "Vertex", "Horizon", "Atlas", "Quantum", "Synergy", "Nexus", "Elevate",
    "Catalyst", "Vanguard", "Zenith", "Optima", "Fusion", "Velocity",
]

COMPANY_SUFFIXES = [
    "Corp", "Inc", "Solutions", "Systems", "Technologies", "Group",
    "Labs", "Dynamics", "Networks", "Platforms", "Digital", "Analytics",
    "Software", "Services", "Enterprises", "Holdings", "Partners",
]

REGIONS = ["North America", "EMEA", "APAC", "LATAM"]

REP_NAMES = [
    "Sarah Chen", "Marcus Johnson", "Emily Rodriguez", "James Wilson",
    "Priya Patel", "David Kim", "Rachel Martinez", "Alex Thompson",
    "Jordan Lee", "Taylor Anderson", "Casey Williams", "Morgan Brown",
    "Sam Davis", "Jamie Garcia", "Riley Taylor", "Drew Miller",
]

REP_TIERS = {
    1: "top", 2: "top", 3: "top",
    4: "solid", 5: "solid", 6: "solid",
    7: "solid", 8: "solid",
    9: "developing", 10: "developing",
    11: "developing", 12: "developing",
    13: "underperformer", 14: "underperformer",
    15: "ramping", 16: "ramping",
}

# Enterprise account allocation weights by rep tier
_SEGMENT_WEIGHTS_BY_TIER = {
    "top":             [0.35, 0.40, 0.25],  # smb, mid, enterprise
    "solid":           [0.50, 0.35, 0.15],
    "developing":      [0.55, 0.35, 0.10],
    "underperformer":  [0.60, 0.30, 0.10],
    "ramping":         [0.55, 0.35, 0.10],
}


def generate_accounts(output_path: Path, num_accounts: int = 1000):
    """Generate account data with realistic GTM patterns."""

    accounts = []

    for account_id in range(1, num_accounts + 1):
        name = f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)}"
        industry = random.choice(INDUSTRIES)

        owner_id = random.randint(1, len(REP_NAMES))
        tier = REP_TIERS[owner_id]

        # Employee count distribution shaped by rep tier
        seg_weights = _SEGMENT_WEIGHTS_BY_TIER[tier]
        employee_bucket = random.choices(
            ["smb", "mid_market", "enterprise"],
            weights=seg_weights,
        )[0]
        employee_ranges = {
            "smb": (10, 200),
            "mid_market": (201, 2000),
            "enterprise": (2001, 50000),
        }
        employee_count = random.randint(*employee_ranges[employee_bucket])

        # ARR correlates with company size
        arr_base = {
            "smb": random.randint(0, 50000),
            "mid_market": random.randint(10000, 250000),
            "enterprise": random.randint(50000, 2000000),
        }
        arr = arr_base[employee_bucket]

        region = random.choice(REGIONS)

        # Ramping reps only have recently-created accounts
        if tier == "ramping":
            created_at = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))
        else:
            created_at = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1825))

        # Data quality issues
        # 3% chance of null industry
        if random.random() < 0.03:
            industry = None

        # 5% chance of null employee count
        if random.random() < 0.05:
            employee_count = None

        # 2% chance of negative ARR (data error)
        if random.random() < 0.02:
            arr = -arr

        # 4% chance of null region
        if random.random() < 0.04:
            region = None

        # Latent variable: product engagement propensity (not written to CSV).
        # Higher for larger companies and Technology/Financial Services verticals.
        base_engagement = random.random()
        if employee_bucket == "enterprise":
            base_engagement = min(1.0, base_engagement + 0.25)
        elif employee_bucket == "mid_market":
            base_engagement = min(1.0, base_engagement + 0.10)
        if industry in ("Technology", "Financial Services"):
            base_engagement = min(1.0, base_engagement + 0.15)

        accounts.append({
            "account_id": account_id,
            "name": name,
            "industry": industry,
            "employee_count": employee_count,
            "arr": arr,
            "region": region,
            "owner_id": owner_id,
            "created_at": created_at.isoformat(),
            "_product_engagement": round(base_engagement, 3),
            "_employee_bucket": employee_bucket,
        })

    # Write to CSV (exclude internal fields prefixed with _)
    csv_fieldnames = [
        "account_id", "name", "industry", "employee_count",
        "arr", "region", "owner_id", "created_at",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(accounts)

    print(f"Generated {len(accounts)} accounts -> {output_path}")
    return accounts


if __name__ == "__main__":
    output = Path(__file__).parent.parent / "sources" / "postgres" / "accounts.csv"
    generate_accounts(output)

