"""
Generate opportunity data.
Opportunities reference accounts and are central to pipeline/forecast analysis.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from generate_accounts import REP_TIERS

STAGES = [
    "Prospecting",
    "Discovery",
    "Qualification",
    "Proposal",
    "Negotiation",
    "Closed Won",
    "Closed Lost",
]

# Baseline stage weights (~30% win rate among closed deals)
BASE_STAGE_WEIGHTS = [0.18, 0.17, 0.20, 0.12, 0.06, 0.08, 0.19]

LEAD_SOURCES = [
    "Inbound - Web", "Inbound - Content", "Outbound - SDR", "Outbound - AE",
    "Partner Referral", "Event", "Webinar", "Product-Led",
]

# Win-rate modifier by lead source (additive shift on base ~30%)
_SOURCE_WIN_MODIFIER = {
    "Partner Referral": 0.18,
    "Product-Led": 0.12,
    "Event": 0.06,
    "Webinar": 0.04,
    "Inbound - Web": 0.0,
    "Inbound - Content": 0.0,
    "Outbound - SDR": -0.05,
    "Outbound - AE": -0.08,
}

# Win-rate modifier by rep tier
_TIER_WIN_MODIFIER = {
    "top": 0.15,
    "solid": 0.0,
    "developing": -0.08,
    "underperformer": -0.15,
    "ramping": -0.05,
}

# Cycle-time multiplier by rep tier (lower = faster)
_TIER_CYCLE_MULTIPLIER = {
    "top": 0.75,
    "solid": 1.0,
    "developing": 1.15,
    "underperformer": 1.30,
    "ramping": 1.10,
}

# Probability of flipping a Closed Won to Closed Lost per competitor
_COMPETITOR_FLIP_PROB = {
    "CompetitorA": 0.55,
    "CompetitorB": 0.30,
    "CompetitorC": 0.15,
    "CompetitorD": 0.20,
    "CompetitorE": 0.25,
    "Open Source Alternative": 0.20,
}

FORECAST_CATEGORIES = {
    "Prospecting": "Pipeline",
    "Discovery": "Pipeline",
    "Qualification": "Best Case",
    "Proposal": "Best Case",
    "Negotiation": "Commit",
    "Closed Won": "Closed",
    "Closed Lost": "Omitted",
}

COMPETITORS = [
    None, None, None,
    "CompetitorA", "CompetitorB", "CompetitorC", "CompetitorD",
    "CompetitorE", "Open Source Alternative",
]

LOSS_REASONS = [
    "Price", "Feature Gap", "Competitor", "No Decision", "Timing",
    "Lost to Status Quo", "Champion Left", "Budget Cut",
]

OPP_NAME_TEMPLATES = {
    "New Business": ["{company} - New Business", "{company} - Platform Deal", "{company} - Initial License"],
    "Expansion": ["{company} - Expansion", "{company} - Upsell", "{company} - Additional Seats"],
    "Renewal": ["{company} - Renewal", "{company} - Contract Renewal"],
}

OPP_TYPES = ["New Business", "Expansion", "Renewal"]
OPP_TYPE_WEIGHTS = [0.60, 0.25, 0.15]


def _adjusted_stage_weights(source_mod: float, tier_mod: float, engagement_mod: float) -> list:
    """Shift the Closed Won / Closed Lost ratio while keeping open-stage weights unchanged."""
    weights = list(BASE_STAGE_WEIGHTS)
    total_closed = weights[5] + weights[6]
    base_wr = weights[5] / total_closed
    new_wr = max(0.05, min(0.90, base_wr + source_mod + tier_mod + engagement_mod))
    weights[5] = total_closed * new_wr
    weights[6] = total_closed * (1 - new_wr)
    return weights


def _quarter_weighted_close_date(base_date: datetime, min_days: int, max_days: int) -> datetime:
    """Pick a close date biased toward end-of-quarter (last 2 weeks of Mar/Jun/Sep/Dec)."""
    candidate = base_date + timedelta(days=random.randint(min_days, max_days))
    month = candidate.month
    day = candidate.day
    is_eoq_month = month in (3, 6, 9, 12)
    is_last_two_weeks = day >= 16
    if is_eoq_month and is_last_two_weeks:
        return candidate
    # 40% chance to shift toward end-of-quarter
    if random.random() < 0.40:
        # Find the next quarter-end month
        for eoq_month in [3, 6, 9, 12]:
            if eoq_month >= candidate.month:
                target_month = eoq_month
                break
        else:
            target_month = 3
            candidate = candidate.replace(year=candidate.year + 1)
        try:
            candidate = candidate.replace(month=target_month, day=random.randint(16, 28))
        except ValueError:
            pass
    return candidate


def generate_opportunities(output_path: Path, accounts: list, num_opps: int = 5000):
    """Generate opportunity data with win rates driven by rep tier, lead source, and product engagement."""

    opportunities = []
    accounts_with_won_opps = set()

    for opp_id in range(1, num_opps + 1):
        account = random.choice(accounts)

        # Determine opportunity type
        opp_type = random.choices(OPP_TYPES, weights=OPP_TYPE_WEIGHTS)[0]

        if opp_type in ("Expansion", "Renewal") and account["account_id"] not in accounts_with_won_opps:
            opp_type = "New Business"

        template = random.choice(OPP_NAME_TEMPLATES[opp_type])
        opp_name = template.format(company=account["name"])

        # Owner — usually same as account owner, but 30% chance different
        if random.random() < 0.7:
            owner_id = account["owner_id"]
        else:
            owner_id = random.randint(1, 16)

        tier = REP_TIERS[owner_id]

        # Lead source (picked before stage so it can influence outcome)
        lead_source = random.choice(LEAD_SOURCES)

        # --- Compute win-rate modifiers ---
        source_mod = _SOURCE_WIN_MODIFIER.get(lead_source, 0.0)
        tier_mod = _TIER_WIN_MODIFIER.get(tier, 0.0)
        engagement = account.get("_product_engagement", 0.5)
        engagement_mod = 0.0
        if opp_type in ("Expansion", "Renewal"):
            engagement_mod = engagement * 0.15

        stage_weights = _adjusted_stage_weights(source_mod, tier_mod, engagement_mod)
        stage = random.choices(STAGES, weights=stage_weights)[0]

        # --- Competitor assignment (before potential flip) ---
        if stage == "Closed Lost":
            competitor = random.choice(COMPETITORS + ["CompetitorA", "CompetitorB"])
        else:
            competitor = random.choice(COMPETITORS)

        # Competitor-based outcome flip: a tough competitor can turn a Won into a Lost
        if stage == "Closed Won" and competitor is not None:
            flip_prob = _COMPETITOR_FLIP_PROB.get(competitor, 0.0)
            if random.random() < flip_prob:
                stage = "Closed Lost"

        # Amount correlates with account size and opp type
        emp = account.get("employee_count")
        if emp and isinstance(emp, int) and emp > 0:
            if emp <= 200:
                base_amount = random.randint(5000, 50000)
            elif emp <= 2000:
                base_amount = random.randint(20000, 200000)
            else:
                base_amount = random.randint(50000, 1000000)
        else:
            base_amount = random.randint(10000, 100000)

        # Product-engaged accounts get slightly larger deal sizes
        if engagement > 0.7:
            base_amount = int(base_amount * random.uniform(1.05, 1.25))

        if opp_type == "Expansion":
            amount = int(base_amount * random.uniform(0.2, 0.6))
        elif opp_type == "Renewal":
            amount = int(base_amount * random.uniform(0.8, 1.1))
        else:
            amount = base_amount

        # Created date — slight bias toward beginning of quarter
        account_created = datetime.fromisoformat(account["created_at"])
        days_after = random.randint(0, max(1, (datetime(2024, 12, 31) - account_created).days))
        created_date = account_created + timedelta(days=days_after)
        if created_date > datetime(2024, 12, 31):
            created_date = datetime(2024, 12, 31) - timedelta(days=random.randint(0, 30))

        # Nudge created_date toward beginning of quarter (first 3 weeks) 30% of the time
        if random.random() < 0.30 and created_date.day > 21:
            created_date = created_date.replace(day=random.randint(1, 15))

        # Close date
        is_closed = stage in ("Closed Won", "Closed Lost")
        is_won = stage == "Closed Won"

        cycle_mult = _TIER_CYCLE_MULTIPLIER.get(tier, 1.0)
        if is_closed:
            min_cycle = int(14 * cycle_mult)
            max_cycle = int(180 * cycle_mult)
            close_date = _quarter_weighted_close_date(created_date, min_cycle, max_cycle)
            if close_date > datetime(2024, 12, 31):
                close_date = datetime(2024, 12, 31)
        else:
            close_date = created_date + timedelta(days=random.randint(30, 270))

        forecast_category = FORECAST_CATEGORIES[stage]

        # Loss reason
        loss_reason = random.choice(LOSS_REASONS) if stage == "Closed Lost" else None

        # Days in current stage — top reps spend fewer days
        max_days_in_stage = int(60 * cycle_mult)
        days_in_stage = random.randint(1, max(2, max_days_in_stage))

        # Next step — underperformers more likely to leave blank
        next_steps = [
            "Schedule demo", "Send proposal", "Executive alignment",
            "Technical review", "Legal review", "Contract signing",
            "POC setup", "Reference call", None,
        ]
        if not is_closed:
            if tier == "underperformer":
                next_step = random.choice(next_steps + [None, None, None])
            else:
                next_step = random.choice(next_steps)
        else:
            next_step = None

        # --- Data quality issues (unchanged) ---
        if random.random() < 0.03:
            amount = None
        if random.random() < 0.02:
            close_date = created_date - timedelta(days=random.randint(1, 30))
        if random.random() < 0.05:
            lead_source = None
        if random.random() < 0.03:
            oid = random.randint(1, max(1, opp_id - 50))
        else:
            oid = opp_id

        if is_won:
            accounts_with_won_opps.add(account["account_id"])

        opportunities.append({
            "opp_id": oid,
            "account_id": account["account_id"],
            "owner_id": owner_id,
            "name": opp_name,
            "stage": stage,
            "amount": amount,
            "close_date": close_date.date().isoformat() if isinstance(close_date, datetime) else close_date,
            "created_date": created_date.date().isoformat(),
            "lead_source": lead_source,
            "forecast_category": forecast_category,
            "is_won": is_won,
            "is_closed": is_closed,
            "competitor": competitor,
            "loss_reason": loss_reason,
            "days_in_stage": days_in_stage,
            "next_step": next_step,
            "opportunity_type": opp_type,
            "created_at": created_date.isoformat(),
        })

    # Write to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "opp_id", "account_id", "owner_id", "name", "stage", "amount",
            "close_date", "created_date", "lead_source", "forecast_category",
            "is_won", "is_closed", "competitor", "loss_reason",
            "days_in_stage", "next_step", "opportunity_type", "created_at",
        ])
        writer.writeheader()
        writer.writerows(opportunities)

    print(f"Generated {len(opportunities)} opportunities -> {output_path}")
    return opportunities


if __name__ == "__main__":
    from generate_accounts import generate_accounts

    base = Path(__file__).parent.parent / "sources"
    accounts = generate_accounts(base / "postgres" / "accounts.csv")
    generate_opportunities(base / "postgres" / "opportunities.csv", accounts)

