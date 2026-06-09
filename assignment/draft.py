from context import formatMoney


def opening(context: dict) -> str:
    summary = context["summary"]
    opportunities = context["opportunities"]
    usage = context["productUsage"]
    marketing = context["marketing"]

    if opportunities:
        opp = opportunities[0]
        return (
            f"I noticed {summary.get('name')} has an opportunity in {opp.get('stage')} "
            f"with {formatMoney(opp.get('amount'))} in scope."
        )

    if usage:
        return (
            f"I noticed {summary.get('name')} is currently in the {usage.get('engagement_tier')} "
            f"product usage tier with {usage.get('active_users')} active users."
        )

    if marketing:
        lead = marketing[0]
        return (
            f"I saw recent engagement from {lead.get('email')} around "
            f"{lead.get('first_campaign_name') or 'your marketing programs'}."
        )

    return f"I was looking at {summary.get('name')} and your work in {summary.get('industry')}."


def reason(context: dict) -> str:
    opportunities = context["opportunities"]
    calls = context["calls"]
    usage = context["productUsage"]

    if opportunities:
        opp = opportunities[0]
        if opp.get("next_step"):
            return f"The next step listed is {opp.get('next_step')}, so I thought it would be useful to reconnect to discuss next steps."
        if opp.get("buying_signal_mentions", 0) > 0:
            return "This seemed like a timely moment to followup due to previous interest in purchase."

    if calls:
        call = calls[0]
        if call.get("risk_mentions", 0) > 0 or call.get("objection_mentions", 0) > 0:
            return "I also saw some risk or objection signals in recent calls, which may be worth addressing directly."

    if usage and usage.get("usage_trend_pct") is not None:
        return "The product usage trend also looked like a useful signal for a conversation."

    return "I thought there may be a useful reason to compare priorities and see where we can help."


def draftEmail(context: dict) -> str:
    summary = context["summary"]
    accountName = summary.get("name")
    if not accountName:
        return "No information found about this account/prospect"

    return f"""Hello, 

I hope you're doing well.

{opening(context)}

{reason(context)}

Would it be worth finding a few minutes this week to compare priorities and see if there is a useful next step?

Best,
<Name>
"""
