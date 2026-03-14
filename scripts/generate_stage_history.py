"""
Generate opportunity stage history data.
Each opportunity progresses through stages with timestamps,
enabling velocity analysis and bottleneck detection.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

STAGE_ORDER = [
    "Prospecting",
    "Discovery",
    "Qualification",
    "Proposal",
    "Negotiation",
    "Closed Won",
    "Closed Lost",
]

# Average days spent in each stage (varies by deal size and randomness)
AVG_DAYS_IN_STAGE = {
    "Prospecting": 12,
    "Discovery": 18,
    "Qualification": 15,
    "Proposal": 10,
    "Negotiation": 20,
}


def generate_stage_history(output_path: Path, opportunities: list):
    """Generate stage transition history for each opportunity."""

    history = []
    history_id = 1

    for opp in opportunities:
        stage = opp["stage"]
        created_date = datetime.fromisoformat(opp["created_date"])
        is_closed = opp.get("is_closed", False)
        if isinstance(is_closed, str):
            is_closed = is_closed.lower() == "true"

        close_date_str = opp.get("close_date")
        if close_date_str:
            close_date = datetime.fromisoformat(close_date_str)
        else:
            close_date = created_date + timedelta(days=90)

        # Determine which stages this opp passed through
        if stage in ("Closed Won", "Closed Lost"):
            final_idx = STAGE_ORDER.index(stage)
            # Closed deals went through stages 0..(final_idx-1), then jumped to Won/Lost
            passed_stages = STAGE_ORDER[:final_idx]
        else:
            current_idx = STAGE_ORDER.index(stage)
            passed_stages = STAGE_ORDER[:current_idx + 1]

        if not passed_stages:
            continue

        # Distribute time across passed stages
        if is_closed and close_date > created_date:
            total_days = (close_date - created_date).days
        else:
            total_days = sum(
                AVG_DAYS_IN_STAGE.get(s, 14) for s in passed_stages
            )

        # Generate random weights per stage to distribute total_days
        weights = [
            max(1, AVG_DAYS_IN_STAGE.get(s, 14) * random.uniform(0.4, 2.0))
            for s in passed_stages
        ]
        total_weight = sum(weights)

        cursor = created_date
        for i, s in enumerate(passed_stages):
            days_in = max(1, int(total_days * weights[i] / total_weight))
            entered_at = cursor
            exited_at = cursor + timedelta(days=days_in)

            is_last_stage = (i == len(passed_stages) - 1)

            # If this is the current stage of an open deal, no exit yet
            if is_last_stage and not is_closed:
                exited_at = None

            history.append({
                "stage_history_id": history_id,
                "opp_id": opp["opp_id"],
                "stage": s,
                "entered_at": entered_at.isoformat(),
                "exited_at": exited_at.isoformat() if exited_at else None,
                "days_in_stage": days_in if exited_at else None,
            })
            history_id += 1
            cursor = exited_at if exited_at else cursor + timedelta(days=days_in)

        # Add the final closed stage entry
        if is_closed and stage in ("Closed Won", "Closed Lost"):
            history.append({
                "stage_history_id": history_id,
                "opp_id": opp["opp_id"],
                "stage": stage,
                "entered_at": cursor.isoformat(),
                "exited_at": cursor.isoformat(),
                "days_in_stage": 0,
            })
            history_id += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "stage_history_id", "opp_id", "stage",
            "entered_at", "exited_at", "days_in_stage",
        ])
        writer.writeheader()
        writer.writerows(history)

    print(f"Generated {len(history)} stage history records -> {output_path}")
    return history


if __name__ == "__main__":
    from generate_accounts import generate_accounts
    from generate_opportunities import generate_opportunities

    base = Path(__file__).parent.parent / "sources"
    accounts = generate_accounts(base / "postgres" / "accounts.csv")
    opps = generate_opportunities(base / "postgres" / "opportunities.csv", accounts)
    generate_stage_history(base / "postgres" / "stage_history.csv", opps)
