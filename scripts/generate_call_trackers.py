"""
Generate call tracker/topic data.
Trackers detect key topics mentioned during calls (competitors, pricing, etc.).
"""
import csv
import random
from pathlib import Path

TRACKER_CATEGORIES = {
    "Competitor": [
        "Competitor - CompetitorA",
        "Competitor - CompetitorB",
        "Competitor - CompetitorC",
        "Competitor - CompetitorD",
        "Competitor - CompetitorE",
        "Competitor - Open Source Alternative",
    ],
    "Pricing": [
        "Pricing - Requested Quote",
        "Pricing - Compared to Competitor",
        "Pricing - Enterprise Tier",
        "Pricing - Volume Discount",
        "Pricing - Too Expensive Objection",
    ],
    "Discount": [
        "Discount - Multi-Year Ask",
        "Discount - End of Quarter",
        "Discount - Competitive Match",
    ],
    "Budget": [
        "Budget - Approved",
        "Budget - Needs Approval",
        "Budget - Freeze Mentioned",
        "Budget - Reallocating Funds",
    ],
    "Risk": [
        "Risk - Champion Leaving",
        "Risk - Budget Freeze",
        "Risk - Competitor Evaluation",
        "Risk - No Decision Likely",
        "Risk - Delayed Timeline",
        "Risk - Stakeholder Pushback",
        "Risk - Legal Blockers",
    ],
    "Security": [
        "Security - SSO Requirement",
        "Security - SOC2 Compliance",
        "Security - Data Residency",
        "Security - Penetration Testing",
        "Security - GDPR Compliance",
    ],
    "Buying Signal": [
        "Next Steps Discussed",
        "Decision Maker Involved",
        "Procurement Process Started",
        "POC Requested",
        "Reference Call Requested",
        "Decision Timeline Confirmed",
        "Contract Review Started",
    ],
    "Objection": [
        "Objection - Missing Feature",
        "Objection - Too Complex",
        "Objection - Switching Cost",
        "Objection - Team Adoption Concern",
        "Objection - Need More Stakeholder Buy-in",
    ],
    "Technical": [
        "Technical - API Integration",
        "Technical - Data Migration Plan",
        "Technical - Custom Workflow Needs",
        "Technical - Performance Requirements",
        "Technical - SSO / SAML Setup",
    ],
}

TRACKER_NAMES = [name for names in TRACKER_CATEGORIES.values() for name in names]

# Outcome-specific category weights: won deals surface more buying signals,
# lost deals surface more risk/objection/competitor topics.
_CATEGORY_WEIGHTS_BY_OUTCOME = {
    "won": {
        "Competitor": 0.8, "Pricing": 1.2, "Discount": 0.9, "Budget": 1.1,
        "Risk": 0.5, "Security": 0.8, "Buying Signal": 2.5, "Objection": 0.5, "Technical": 1.0,
    },
    "lost": {
        "Competitor": 2.5, "Pricing": 1.5, "Discount": 0.6, "Budget": 0.8,
        "Risk": 2.2, "Security": 0.7, "Buying Signal": 0.6, "Objection": 2.0, "Technical": 0.8,
    },
    "open": {
        "Competitor": 1.5, "Pricing": 1.3, "Discount": 0.8, "Budget": 1.0,
        "Risk": 1.2, "Security": 0.7, "Buying Signal": 1.4, "Objection": 1.0, "Technical": 0.9,
    },
}


def _build_tracker_weights(outcome: str) -> list[float]:
    cat_weights = _CATEGORY_WEIGHTS_BY_OUTCOME.get(outcome, _CATEGORY_WEIGHTS_BY_OUTCOME["open"])
    weights = []
    for category, names in TRACKER_CATEGORIES.items():
        w = cat_weights[category] / len(names)
        weights.extend([w] * len(names))
    total = sum(weights)
    return [w / total for w in weights]


def _category_for(tracker_name: str) -> str:
    for category, names in TRACKER_CATEGORIES.items():
        if tracker_name in names:
            return category
    return "Unknown"


def generate_call_trackers(output_path: Path, calls: list, avg_trackers_per_call: float = 3.0):
    """Generate tracker/topic detection data for calls with outcome-correlated topic distributions."""

    trackers = []
    tracker_id = 1

    # Pre-build per-outcome weight vectors
    weights_cache = {outcome: _build_tracker_weights(outcome) for outcome in ("won", "lost", "open")}

    for call in calls:
        duration = call.get("duration_minutes")
        disposition = call.get("disposition")
        if disposition != "Completed" or duration is None or (isinstance(duration, (int, float)) and duration <= 0):
            continue

        # Determine outcome from the internal _opp_stage field
        opp_stage = call.get("_opp_stage", "")
        if opp_stage == "Closed Won":
            outcome = "won"
        elif opp_stage == "Closed Lost":
            outcome = "lost"
        else:
            outcome = "open"

        normed_weights = weights_cache[outcome]

        duration_factor = min(float(duration) / 30.0, 2.0)
        adjusted_avg = avg_trackers_per_call * duration_factor
        num_trackers = max(0, int(random.gauss(adjusted_avg, 1.5)))
        num_trackers = min(num_trackers, 8)

        if num_trackers == 0:
            continue

        # Weighted sampling without replacement
        indices = list(range(len(TRACKER_NAMES)))
        selected_indices = []
        remaining_weights = list(normed_weights)
        for _ in range(min(num_trackers, len(TRACKER_NAMES))):
            total = sum(remaining_weights[i] for i in indices if i not in selected_indices)
            if total <= 0:
                break
            r = random.random() * total
            cumulative = 0
            for idx in indices:
                if idx in selected_indices:
                    continue
                cumulative += remaining_weights[idx]
                if cumulative >= r:
                    selected_indices.append(idx)
                    break

        for idx in selected_indices:
            tracker_name = TRACKER_NAMES[idx]
            mention_count = random.randint(1, 8)

            if random.random() < 0.02:
                mention_count = -mention_count

            name = None if random.random() < 0.03 else tracker_name

            trackers.append({
                "tracker_id": tracker_id,
                "call_id": call["call_id"],
                "tracker_name": name,
                "tracker_category": _category_for(tracker_name) if name else None,
                "mention_count": mention_count,
            })
            tracker_id += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "tracker_id", "call_id", "tracker_name", "tracker_category", "mention_count",
        ])
        writer.writeheader()
        writer.writerows(trackers)

    print(f"Generated {len(trackers)} call tracker records -> {output_path}")
    return trackers


if __name__ == "__main__":
    from generate_accounts import generate_accounts
    from generate_opportunities import generate_opportunities
    from generate_calls import generate_calls

    base = Path(__file__).parent.parent / "sources"
    accounts = generate_accounts(base / "postgres" / "accounts.csv")
    opps = generate_opportunities(base / "postgres" / "opportunities.csv", accounts)
    calls = generate_calls(base / "postgres" / "calls.csv", opps)
    generate_call_trackers(base / "postgres" / "call_trackers.csv", calls)

