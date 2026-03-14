"""
Generate lead data.
Leads represent inbound/outbound prospects that may convert to opportunities.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson",
]

COMPANIES = [
    "TechFlow Inc", "DataBridge Corp", "CloudScale Systems", "InnovateCo",
    "QuantumLogic Labs", "NexGen Solutions", "PrimePath Digital", "CyberVault",
    "StreamLine Analytics", "Agile Dynamics", "BrightWave Tech", "CoreStack",
    "FutureForge", "Insight Platforms", "MetaSync", "PulsePoint Digital",
    "RapidCloud", "ScaleUp Systems", "TrueNorth Data", "VertexAI",
]

LEAD_SOURCES = [
    "Inbound - Web", "Inbound - Content", "Inbound - Webinar",
    "Outbound - SDR", "Outbound - Cold", "Event", "Partner Referral",
    "Product-Led", "Social Media", "Paid Search",
]

LEAD_STATUSES = [
    "New", "Working", "MQL", "SQL", "Converted", "Disqualified", "Nurture",
]

# Base status weights:        New   Working MQL   SQL   Converted Disqualified Nurture
_BASE_STATUS_WEIGHTS =       [0.15, 0.15,   0.15, 0.10, 0.20,     0.15,        0.10]

# Source-specific conversion rate multipliers (applied to the "Converted" weight)
_SOURCE_CONVERSION_MULT = {
    "Product-Led": 2.0,
    "Partner Referral": 1.8,
    "Inbound - Webinar": 1.3,
    "Event": 1.2,
    "Inbound - Web": 1.0,
    "Inbound - Content": 1.0,
    "Paid Search": 0.9,
    "Outbound - SDR": 0.6,
    "Social Media": 0.4,
    "Outbound - Cold": 0.3,
}


def generate_leads(output_path: Path, opportunities: list, num_leads: int = 8000):
    """Generate lead data with source-specific conversion rates."""

    leads = []
    convertible_opps = [o for o in opportunities if o["stage"] != "Prospecting"]
    random.shuffle(convertible_opps)

    for lead_id in range(1, num_leads + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        company = random.choice(COMPANIES)

        email = f"{first_name.lower()}.{last_name.lower()}{lead_id}@{company.lower().replace(' ', '').replace(',', '')}.com"

        if random.random() < 0.03:
            email = f"{first_name.lower()}.{last_name.lower()}"

        source = random.choice(LEAD_SOURCES)

        # Adjust conversion probability by source
        weights = list(_BASE_STATUS_WEIGHTS)
        conv_mult = _SOURCE_CONVERSION_MULT.get(source, 1.0)
        weights[4] = weights[4] * conv_mult  # index 4 = Converted
        status = random.choices(LEAD_STATUSES, weights=weights)[0]

        created_at = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1825))

        # Conversion logic
        converted_opp_id = None
        converted_date = None
        converted_account_id = None

        if status == "Converted" and convertible_opps:
            opp = convertible_opps.pop() if convertible_opps else None
            if opp:
                converted_opp_id = opp["opp_id"]
                converted_account_id = opp["account_id"]
                opp_created = datetime.fromisoformat(opp["created_at"])
                converted_date = (opp_created - timedelta(days=random.randint(0, 14))).date().isoformat()
                # Lead should be created before conversion
                created_at = opp_created - timedelta(days=random.randint(7, 90))

        # Score (0-100, MQL threshold = 50)
        if status in ("MQL", "SQL", "Converted"):
            score = random.randint(50, 100)
        elif status == "Disqualified":
            score = random.randint(0, 30)
        else:
            score = random.randint(10, 70)

        # Data quality issues
        # 4% null email
        if random.random() < 0.04:
            email = None

        # 3% null source
        if random.random() < 0.03:
            source = None

        # 2% negative score
        if random.random() < 0.02:
            score = -score

        leads.append({
            "lead_id": lead_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "company": company,
            "source": source,
            "status": status,
            "score": score,
            "converted_opp_id": converted_opp_id,
            "converted_account_id": converted_account_id,
            "converted_date": converted_date,
            "created_at": created_at.isoformat(),
        })

    # Write to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "lead_id", "first_name", "last_name", "email", "company",
            "source", "status", "score", "converted_opp_id",
            "converted_account_id", "converted_date", "created_at",
        ])
        writer.writeheader()
        writer.writerows(leads)

    print(f"Generated {len(leads)} leads -> {output_path}")
    return leads


if __name__ == "__main__":
    from generate_accounts import generate_accounts
    from generate_opportunities import generate_opportunities

    base = Path(__file__).parent.parent / "sources"
    accounts = generate_accounts(base / "postgres" / "accounts.csv")
    opps = generate_opportunities(base / "postgres" / "opportunities.csv", accounts)
    generate_leads(base / "postgres" / "leads.csv", opps)

