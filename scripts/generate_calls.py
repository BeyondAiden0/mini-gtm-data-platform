"""
Generate call data.
Calls are linked to opportunities and reps (owners).
Call patterns (talk ratio, questions, next steps) differ by deal outcome and rep tier.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from generate_accounts import REP_TIERS

CALL_TYPES = ["Discovery", "Demo", "Follow-Up", "Negotiation", "QBR", "Check-In", "Technical Deep Dive"]
CALL_DISPOSITIONS = ["Completed", "No Show", "Rescheduled", "Voicemail"]

# Outcome-based call pattern ranges: (talk_ratio, question_count, next_steps_prob, monologue_max)
_CALL_PROFILES = {
    "won":  {"talk_ratio": (0.30, 0.55), "questions": (8, 25), "next_steps_prob": 0.75, "monologue_max": 180},
    "lost": {"talk_ratio": (0.50, 0.85), "questions": (2, 15), "next_steps_prob": 0.30, "monologue_max": 300},
    "open": {"talk_ratio": (0.35, 0.70), "questions": (4, 20), "next_steps_prob": 0.50, "monologue_max": 240},
}

# Rep tier adjustments (additive shift on talk_ratio, multiplicative on questions)
_TIER_CALL_ADJUST = {
    "top":             {"talk_shift": -0.05, "question_mult": 1.2, "next_steps_boost": 0.10},
    "solid":           {"talk_shift": 0.0,   "question_mult": 1.0, "next_steps_boost": 0.0},
    "developing":      {"talk_shift": 0.03,  "question_mult": 0.9, "next_steps_boost": -0.05},
    "underperformer":  {"talk_shift": 0.08,  "question_mult": 0.7, "next_steps_boost": -0.15},
    "ramping":         {"talk_shift": 0.05,  "question_mult": 0.8, "next_steps_boost": -0.05},
}


def generate_calls(output_path: Path, opportunities: list, num_calls: int = 10000):
    """Generate call metadata linked to opportunities with outcome-correlated patterns."""

    calls = []

    for call_id in range(1, num_calls + 1):
        opp = random.choice(opportunities)

        owner_id = opp["owner_id"]
        opp_id = opp["opp_id"]
        is_won = opp.get("is_won", False)
        is_closed = opp.get("is_closed", False)
        opp_stage = opp.get("stage", "")
        tier = REP_TIERS.get(owner_id, "solid")

        if is_won:
            profile = _CALL_PROFILES["won"]
        elif is_closed:
            profile = _CALL_PROFILES["lost"]
        else:
            profile = _CALL_PROFILES["open"]

        tier_adj = _TIER_CALL_ADJUST.get(tier, _TIER_CALL_ADJUST["solid"])

        # Call date around the opp lifecycle
        opp_created = datetime.fromisoformat(opp["created_at"])
        days_offset = random.randint(0, 120)
        call_date = opp_created + timedelta(days=days_offset)
        if call_date > datetime(2024, 12, 31):
            call_date = datetime(2024, 12, 31) - timedelta(days=random.randint(0, 30))

        call_date = call_date.replace(
            hour=random.choices(range(8, 18), weights=[1, 3, 5, 5, 5, 5, 5, 5, 3, 1])[0],
            minute=random.choice([0, 15, 30, 45]),
        )

        call_type = random.choice(CALL_TYPES)
        disposition = random.choices(
            CALL_DISPOSITIONS,
            weights=[0.75, 0.10, 0.10, 0.05],
        )[0]

        if disposition == "No Show":
            duration_minutes = 0
        elif disposition == "Voicemail":
            duration_minutes = random.randint(1, 3)
        else:
            duration_minutes = random.randint(15, 60)

        direction = random.choices(["Outbound", "Inbound"], weights=[0.7, 0.3])[0]
        num_participants = random.randint(2, 8) if disposition == "Completed" else 1

        # --- Outcome-correlated call metrics ---
        if disposition == "Completed" and duration_minutes > 0:
            tr_lo, tr_hi = profile["talk_ratio"]
            talk_ratio_rep = round(
                max(0.15, min(0.95, random.uniform(tr_lo, tr_hi) + tier_adj["talk_shift"])),
                2,
            )

            q_lo, q_hi = profile["questions"]
            question_count = max(1, int(random.randint(q_lo, q_hi) * tier_adj["question_mult"]))

            ns_prob = max(0.05, min(0.95, profile["next_steps_prob"] + tier_adj["next_steps_boost"]))
            next_steps_mentioned = random.random() < ns_prob

            mono_max = min(profile["monologue_max"], duration_minutes * 60)
            longest_monologue_sec = random.randint(30, max(31, mono_max))
        else:
            talk_ratio_rep = None
            question_count = 0
            next_steps_mentioned = False
            longest_monologue_sec = None

        # --- Data quality issues (unchanged) ---
        if random.random() < 0.03:
            duration_minutes = None
        if random.random() < 0.02 and duration_minutes is not None:
            duration_minutes = -abs(duration_minutes)
        if random.random() < 0.04 and talk_ratio_rep is not None:
            talk_ratio_rep = round(random.uniform(1.01, 1.50), 2)
        if random.random() < 0.03:
            call_date = datetime(2030, 6, 15, 10, 0)

        calls.append({
            "call_id": call_id,
            "opp_id": opp_id,
            "owner_id": owner_id,
            "call_date": call_date.isoformat(),
            "duration_minutes": duration_minutes,
            "direction": direction,
            "call_type": call_type,
            "disposition": disposition,
            "num_participants": num_participants,
            "talk_ratio_rep": talk_ratio_rep,
            "longest_monologue_sec": longest_monologue_sec,
            "question_count": question_count,
            "next_steps_mentioned": next_steps_mentioned,
            "_opp_stage": opp_stage,
        })

    # Write to CSV (exclude internal fields)
    csv_fieldnames = [
        "call_id", "opp_id", "owner_id", "call_date", "duration_minutes",
        "direction", "call_type", "disposition", "num_participants",
        "talk_ratio_rep", "longest_monologue_sec", "question_count",
        "next_steps_mentioned",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(calls)

    print(f"Generated {len(calls)} calls -> {output_path}")
    return calls


if __name__ == "__main__":
    from generate_accounts import generate_accounts
    from generate_opportunities import generate_opportunities

    base = Path(__file__).parent.parent / "sources"
    accounts = generate_accounts(base / "postgres" / "accounts.csv")
    opps = generate_opportunities(base / "postgres" / "opportunities.csv", accounts)
    generate_calls(base / "postgres" / "calls.csv", opps)

