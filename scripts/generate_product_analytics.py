"""
Generate product analytics data (Amplitude/Mixpanel-style).
Tracks product users linked to CRM accounts and their feature-level usage events.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


ROLES = ["admin", "editor", "viewer"]
ROLE_WEIGHTS = [0.15, 0.35, 0.50]

PLAN_TIERS = ["free", "starter", "professional", "enterprise"]

FEATURES = [
    "Dashboard Builder",
    "Reports",
    "API",
    "Integrations",
    "Data Export",
    "Alerts",
    "User Management",
    "Workflow Automation",
    "Custom Fields",
    "Analytics",
]

ACTIONS = ["view", "create", "edit", "delete", "share"]
ACTION_WEIGHTS = [0.40, 0.20, 0.20, 0.05, 0.15]

FIRST_NAMES = [
    "Alice", "Bob", "Carol", "Dan", "Eve", "Frank", "Grace", "Hank",
    "Ivy", "Jack", "Karen", "Leo", "Mia", "Nate", "Olivia", "Paul",
    "Quinn", "Rosa", "Steve", "Tina", "Uma", "Vince", "Wendy", "Xander",
]

LAST_NAMES = [
    "Adams", "Baker", "Clark", "Davis", "Evans", "Foster", "Garcia",
    "Hall", "Ingram", "Jones", "Kim", "Lopez", "Miller", "Nguyen",
    "Owens", "Park", "Quinn", "Rivera", "Smith", "Taylor",
]


def generate_product_users(output_path: Path, accounts: list, num_users: int = 2000):
    """Generate product users linked to CRM accounts.

    High _product_engagement accounts get more users, higher active rates,
    and more admin/editor roles.
    """
    users = []

    account_plans = {}
    for acct in accounts:
        emp = acct.get("employee_count")
        if emp and isinstance(emp, int) and emp > 0:
            if emp <= 200:
                tier = random.choices(PLAN_TIERS, weights=[0.30, 0.40, 0.25, 0.05])[0]
            elif emp <= 2000:
                tier = random.choices(PLAN_TIERS, weights=[0.05, 0.20, 0.50, 0.25])[0]
            else:
                tier = random.choices(PLAN_TIERS, weights=[0.02, 0.08, 0.30, 0.60])[0]
        else:
            tier = random.choice(PLAN_TIERS)
        account_plans[acct["account_id"]] = tier

    # Weight account selection by engagement so high-engagement accounts get more users
    engagement_scores = [acct.get("_product_engagement", 0.5) for acct in accounts]
    selection_weights = [max(0.1, s ** 0.5) for s in engagement_scores]

    data_end = datetime(2025, 2, 28)

    for user_id in range(1, num_users + 1):
        account = random.choices(accounts, weights=selection_weights)[0]
        account_id = account["account_id"]
        engagement = account.get("_product_engagement", 0.5)

        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        company = account["name"].lower().replace(" ", "")
        email = f"{first_name.lower()}.{last_name.lower()}@{company}.com"

        # High-engagement accounts have more admins and editors
        if engagement > 0.7:
            role = random.choices(ROLES, weights=[0.25, 0.40, 0.35])[0]
        else:
            role = random.choices(ROLES, weights=ROLE_WEIGHTS)[0]

        plan_tier = account_plans[account_id]

        account_created = datetime.fromisoformat(account["created_at"])
        signup_offset = random.randint(0, max(1, (data_end - account_created).days))
        signup_date = account_created + timedelta(days=signup_offset)
        if signup_date > data_end:
            signup_date = data_end - timedelta(days=random.randint(0, 30))

        # Active rate scales with engagement
        active_prob = 0.50 + engagement * 0.40  # range: 0.50 – 0.90
        is_active = random.random() < active_prob
        if is_active:
            last_active_date = data_end - timedelta(days=random.randint(0, 30))
        else:
            last_active_date = signup_date + timedelta(days=random.randint(7, 365))
            if last_active_date > data_end:
                last_active_date = data_end

        if random.random() < 0.03:
            email = None

        users.append({
            "product_user_id": user_id,
            "account_id": account_id,
            "email": email,
            "role": role,
            "plan_tier": plan_tier,
            "signup_date": signup_date.date().isoformat(),
            "last_active_date": last_active_date.date().isoformat(),
            "is_active": is_active,
            "_engagement": engagement,
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "product_user_id", "account_id", "email", "role",
                "plan_tier", "signup_date", "last_active_date", "is_active",
            ],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(users)

    print(f"Generated {len(users)} product users -> {output_path}")
    return users


# Feature weights for high-engagement accounts (broader, more advanced features)
_HIGH_ENGAGEMENT_FEATURE_WEIGHTS = [12, 12, 10, 10, 8, 8, 6, 14, 10, 10]
# Feature weights for low-engagement accounts (concentrated on basics)
_LOW_ENGAGEMENT_FEATURE_WEIGHTS = [25, 25, 2, 2, 5, 3, 1, 2, 5, 30]


def generate_product_events(output_path: Path, users: list, num_events: int = 50000):
    """Generate feature-level usage events correlated with account engagement."""

    active_users = [u for u in users if u["is_active"]]
    inactive_users = [u for u in users if not u["is_active"]]

    # Weight active user selection by engagement so high-engagement users generate more events
    active_weights = [max(0.1, u.get("_engagement", 0.5)) for u in active_users]

    events = []

    for event_id in range(1, num_events + 1):
        if random.random() < 0.90 and active_users:
            user = random.choices(active_users, weights=active_weights)[0]
        elif inactive_users:
            user = random.choice(inactive_users)
        else:
            user = random.choice(users)

        engagement = user.get("_engagement", 0.5)

        signup = datetime.fromisoformat(user["signup_date"])
        last_active = datetime.fromisoformat(user["last_active_date"])

        days_range = max(1, (last_active - signup).days)
        event_date = signup + timedelta(days=random.randint(0, days_range))

        if event_date.weekday() >= 5 and random.random() < 0.70:
            event_date -= timedelta(days=event_date.weekday() - 4)

        hour = random.choices(
            range(24),
            weights=[1, 1, 1, 1, 1, 2, 4, 8, 10, 10, 9, 8, 7, 8, 9, 10, 8, 6, 4, 3, 2, 1, 1, 1],
        )[0]
        event_time = event_date.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))

        # Feature selection: high-engagement users use broader features
        if user["role"] == "admin":
            if engagement > 0.6:
                feature = random.choices(FEATURES, weights=_HIGH_ENGAGEMENT_FEATURE_WEIGHTS)[0]
            else:
                feature = random.choice(FEATURES)
        elif user["role"] == "editor":
            if engagement > 0.6:
                feature = random.choices(FEATURES, weights=_HIGH_ENGAGEMENT_FEATURE_WEIGHTS)[0]
            else:
                feature = random.choices(FEATURES, weights=[15, 15, 5, 5, 10, 5, 3, 15, 12, 15])[0]
        else:
            feature = random.choices(FEATURES, weights=_LOW_ENGAGEMENT_FEATURE_WEIGHTS)[0]

        # High-engagement users do more create/edit actions (not just viewing)
        if engagement > 0.7 and user["role"] != "viewer":
            action = random.choices(ACTIONS, weights=[0.25, 0.25, 0.25, 0.05, 0.20])[0]
        else:
            action = random.choices(ACTIONS, weights=ACTION_WEIGHTS)[0]

        if user["role"] == "viewer" and random.random() < 0.80:
            action = "view"

        if random.random() < 0.02:
            event_time = datetime(2030, 3, 15, 10, 0)

        events.append({
            "event_id": event_id,
            "product_user_id": user["product_user_id"],
            "account_id": user["account_id"],
            "feature": feature,
            "action": action,
            "event_timestamp": event_time.isoformat(),
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "event_id", "product_user_id", "account_id",
            "feature", "action", "event_timestamp",
        ])
        writer.writeheader()
        writer.writerows(events)

    print(f"Generated {len(events)} product events -> {output_path}")
    return events


if __name__ == "__main__":
    from generate_accounts import generate_accounts

    base = Path(__file__).parent.parent / "sources"
    accounts = generate_accounts(base / "postgres" / "accounts.csv")
    users = generate_product_users(base / "postgres" / "product_users.csv", accounts)
    generate_product_events(base / "postgres" / "product_events.csv", users)
