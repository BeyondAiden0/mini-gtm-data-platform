"""
Generate contact data.
Contacts are linked to accounts and represent stakeholders in deals.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
]

TITLES = [
    "VP of Engineering", "CTO", "Director of IT", "Head of Data",
    "VP of Sales", "Chief Revenue Officer", "Director of Operations",
    "VP of Product", "CEO", "COO", "CFO", "Director of Marketing",
    "Head of Security", "VP of Infrastructure", "IT Manager",
    "Engineering Manager", "Data Engineer", "Solutions Architect",
    "Product Manager", "DevOps Lead",
]

ROLES = ["Champion", "Economic Buyer", "Technical Evaluator", "Coach", "End User", "Blocker"]

DOMAINS = ["acme.com", "globex.com", "initech.com", "umbrella.co", "waystar.io", "piedpiper.com"]


def generate_contacts(output_path: Path, accounts: list, num_contacts: int = 3000):
    """Generate contact data linked to accounts."""

    contacts = []

    for contact_id in range(1, num_contacts + 1):
        account = random.choice(accounts)
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        # Generate email
        domain = random.choice(DOMAINS)
        email = f"{first_name.lower()}.{last_name.lower()}@{domain}"

        # 5% chance of malformed email
        if random.random() < 0.05:
            email = f"{first_name.lower()}.{last_name.lower()}"

        # 3% chance of null email
        if random.random() < 0.03:
            email = None

        title = random.choice(TITLES)
        role = random.choices(
            ROLES,
            weights=[0.25, 0.15, 0.25, 0.10, 0.15, 0.10],
        )[0]

        # Created at (after account creation)
        account_created = datetime.fromisoformat(account["created_at"])
        days_after = random.randint(0, max(1, (datetime(2024, 12, 31) - account_created).days))
        created_at = account_created + timedelta(days=days_after)
        if created_at > datetime(2024, 12, 31):
            created_at = datetime(2024, 12, 31)

        # Phone
        phone = f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"

        # 8% chance of null phone
        if random.random() < 0.08:
            phone = None

        # 2% chance of null title
        if random.random() < 0.02:
            title = None

        contacts.append({
            "contact_id": contact_id,
            "account_id": account["account_id"],
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "title": title,
            "role": role,
            "created_at": created_at.isoformat(),
        })

    # Write to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "contact_id", "account_id", "first_name", "last_name",
            "email", "phone", "title", "role", "created_at",
        ])
        writer.writeheader()
        writer.writerows(contacts)

    print(f"Generated {len(contacts)} contacts -> {output_path}")
    return contacts


if __name__ == "__main__":
    from generate_accounts import generate_accounts

    base = Path(__file__).parent.parent / "sources"
    accounts = generate_accounts(base / "postgres" / "accounts.csv")
    generate_contacts(base / "postgres" / "contacts.csv", accounts)

