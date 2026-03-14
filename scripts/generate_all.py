"""
Master script to generate all synthetic GTM data in the correct dependency order.

Order:
1. Accounts (foundational)
2. Opportunities (references accounts)
3. Stage History (references opportunities)
4. Contacts (references accounts)
5. Contact Roles (references contacts + opportunities)
6. Leads (some convert to opportunities)
7. Calls (references opportunities)
8. Call Trackers (references calls)
9. Campaigns (standalone)
10. Lead Activities (references leads and campaigns)
11. Product Users (references accounts - Product Analytics)
12. Product Events (references users - Product Analytics)
"""
from pathlib import Path
from generate_accounts import generate_accounts
from generate_opportunities import generate_opportunities
from generate_contacts import generate_contacts
from generate_contact_roles import generate_contact_roles
from generate_leads import generate_leads
from generate_calls import generate_calls
from generate_call_trackers import generate_call_trackers
from generate_stage_history import generate_stage_history
from generate_campaigns import generate_campaigns
from generate_lead_activities import generate_lead_activities
from generate_product_analytics import generate_product_users, generate_product_events


def main():
    base_path = Path(__file__).parent.parent / "sources"

    print("=" * 60)
    print("Generating synthetic GTM data platform")
    print("=" * 60)

    print("\n[1/12] Generating accounts...")
    accounts = generate_accounts(
        base_path / "postgres" / "accounts.csv",
        num_accounts=1000,
    )

    print("\n[2/12] Generating opportunities...")
    opportunities = generate_opportunities(
        base_path / "postgres" / "opportunities.csv",
        accounts=accounts,
        num_opps=5000,
    )

    print("\n[3/12] Generating opportunity stage history...")
    generate_stage_history(
        base_path / "postgres" / "stage_history.csv",
        opportunities=opportunities,
    )

    print("\n[4/12] Generating contacts...")
    contacts = generate_contacts(
        base_path / "postgres" / "contacts.csv",
        accounts=accounts,
        num_contacts=3000,
    )

    print("\n[5/12] Generating contact-opportunity roles...")
    generate_contact_roles(
        base_path / "postgres" / "contact_roles.csv",
        contacts=contacts,
        opportunities=opportunities,
    )

    print("\n[6/12] Generating leads...")
    leads = generate_leads(
        base_path / "postgres" / "leads.csv",
        opportunities=opportunities,
        num_leads=8000,
    )

    print("\n[7/12] Generating calls...")
    calls = generate_calls(
        base_path / "postgres" / "calls.csv",
        opportunities=opportunities,
        num_calls=10000,
    )

    print("\n[8/12] Generating call trackers...")
    generate_call_trackers(
        base_path / "postgres" / "call_trackers.csv",
        calls=calls,
    )

    print("\n[9/12] Generating campaigns...")
    campaigns = generate_campaigns(
        base_path / "postgres" / "campaigns.csv",
        num_campaigns=200,
    )

    print("\n[10/12] Generating lead activities...")
    generate_lead_activities(
        base_path / "postgres" / "lead_activities.csv",
        leads=leads,
        campaigns=campaigns,
        num_activities=30000,
    )

    print("\n[11/12] Generating product users...")
    product_users = generate_product_users(
        base_path / "postgres" / "product_users.csv",
        accounts=accounts,
        num_users=2000,
    )

    print("\n[12/12] Generating product usage events...")
    generate_product_events(
        base_path / "postgres" / "product_events.csv",
        users=product_users,
        num_events=50000,
    )

    print("\n" + "=" * 60)
    print("GTM data generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
