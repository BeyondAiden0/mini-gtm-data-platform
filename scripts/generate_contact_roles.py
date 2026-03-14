"""
Generate contact-opportunity role assignments.
Links contacts to specific deals they're involved in, with their role in that deal.
Enables multi-threading analysis (how many stakeholders per deal).
"""
import csv
import random
from pathlib import Path

DEAL_ROLES = [
    "Champion",
    "Economic Buyer",
    "Technical Evaluator",
    "Coach",
    "End User",
    "Blocker",
    "Executive Sponsor",
    "Legal Reviewer",
]

DEAL_ROLE_WEIGHTS = [0.22, 0.14, 0.22, 0.08, 0.14, 0.06, 0.08, 0.06]


def generate_contact_roles(output_path: Path, contacts: list, opportunities: list):
    """Generate contact-opportunity role assignments."""

    # Group contacts by account_id
    contacts_by_account = {}
    for c in contacts:
        aid = c["account_id"]
        if aid not in contacts_by_account:
            contacts_by_account[aid] = []
        contacts_by_account[aid].append(c)

    roles = []
    role_id = 1

    for opp in opportunities:
        account_id = opp["account_id"]
        account_contacts = contacts_by_account.get(account_id, [])
        if not account_contacts:
            continue

        # Number of contacts involved varies by stage
        stage = opp.get("stage", "")
        if stage in ("Closed Won", "Negotiation"):
            avg_contacts = 3.5
        elif stage in ("Proposal", "Qualification"):
            avg_contacts = 2.5
        else:
            avg_contacts = 1.5

        num_contacts = max(1, min(
            len(account_contacts),
            int(random.gauss(avg_contacts, 1.0))
        ))

        selected = random.sample(account_contacts, k=num_contacts)
        assigned_roles = set()

        for contact in selected:
            # Pick a role, avoiding duplicates where possible
            available_roles = [r for r in DEAL_ROLES if r not in assigned_roles]
            if not available_roles:
                available_roles = DEAL_ROLES

            available_weights = [
                DEAL_ROLE_WEIGHTS[DEAL_ROLES.index(r)] for r in available_roles
            ]
            deal_role = random.choices(available_roles, weights=available_weights)[0]
            assigned_roles.add(deal_role)

            is_primary = (deal_role in ("Champion", "Economic Buyer", "Executive Sponsor"))

            roles.append({
                "contact_role_id": role_id,
                "contact_id": contact["contact_id"],
                "opp_id": opp["opp_id"],
                "role": deal_role,
                "is_primary": is_primary,
            })
            role_id += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "contact_role_id", "contact_id", "opp_id", "role", "is_primary",
        ])
        writer.writeheader()
        writer.writerows(roles)

    print(f"Generated {len(roles)} contact role records -> {output_path}")
    return roles


if __name__ == "__main__":
    from generate_accounts import generate_accounts
    from generate_opportunities import generate_opportunities
    from generate_contacts import generate_contacts

    base = Path(__file__).parent.parent / "sources"
    accounts = generate_accounts(base / "postgres" / "accounts.csv")
    opps = generate_opportunities(base / "postgres" / "opportunities.csv", accounts)
    contacts = generate_contacts(base / "postgres" / "contacts.csv", accounts)
    generate_contact_roles(base / "postgres" / "contact_roles.csv", contacts, opps)
