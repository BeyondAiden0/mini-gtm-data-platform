import duckdb

# turn one DuckDB result into dict
def oneRow(conn: duckdb.DuckDBPyConnection, query: str, params: list) -> dict:
    result = conn.execute(query, params)
    row = result.fetchone()

    if not row:

        return {}
    columns = [item[0] for item in result.description]
    return dict(zip(columns, row))

# turn many DuckDB results to a dict
def manyRows(conn: duckdb.DuckDBPyConnection, query: str, params: list) -> list[dict]:
    result = conn.execute(query, params)
    rows = result.fetchall()
    columns = [item[0] for item in result.description]
    return [dict(zip(columns, row)) for row in rows]

# pull information from DB about the account (marts.dim_accounts)
def getAccountSummary(conn: duckdb.DuckDBPyConnection, accountId: int) -> dict:
    return oneRow(
        conn,
        """
        select
            account_id,
            name,
            industry,
            employee_count,
            arr,
            region,
            segment,
            total_opportunities,
            open_opportunities,
            won_opportunities,
            lost_opportunities,
            open_pipeline,
            closed_won_revenue,
            contact_count,
            champion_count,
            economic_buyer_count
        from marts.dim_accounts
        where account_id = ?
        limit 1
        """,
        [accountId],
    )
    
# pull information from the DB about call information (marts.fct_calls)
def getCalls(conn: duckdb.DuckDBPyConnection, accountId: int) -> list[dict]:
    return manyRows(
        conn,
        """
        select
            call_date,
            call_type,
            duration_minutes,
            next_steps_mentioned,
            buying_signal_mentions,
            risk_mentions,
            objection_mentions,
            competitor_mentions,
            pricing_mentions
        from marts.fct_calls
        where account_id = ?
        order by call_date desc

        """,
        [accountId],
    )

# pull information from the DB about the marketing lead records (marts.fct_funnel)
def getMarketing(conn: duckdb.DuckDBPyConnection, accountId: int) -> list[dict]:
    return manyRows(
        conn,
        """
        select
            first_name,
            last_name,
            email,
            lead_source,
            lead_status,
            lead_score,
            total_activities,
            campaigns_touched,
            email_clicks,
            webinars_attended,
            content_downloads,
            first_campaign_name,
            first_campaign_channel
        from marts.fct_funnel
        where converted_account_id = ?
        order by lead_score desc

        """,
        [accountId],
    )
    
# pull information from the DB about the opportunities available (marts.fct_opportunities)
def getOpportunities(conn: duckdb.DuckDBPyConnection, accountId: int) -> list[dict]:
    return manyRows(
        conn,
        """
        select
            opp_name,
            stage,
            amount,
            close_date,
            forecast_category,
            next_step,
            competitor,
            loss_reason,
            total_calls,
            buying_signal_mentions,
            risk_mentions,
            objection_mentions,
            pricing_mentions
        from marts.fct_opportunities
        where account_id = ?
        order by is_closed asc, close_date desc

        """,
        [accountId],
    )

# pull information from the DB about product usage (mart.fct_product_usage)
def getProductUsage(conn: duckdb.DuckDBPyConnection, accountId: int) -> dict:
    return oneRow(
        conn,
        """
        select
            usage_month,
            active_users,
            total_events,
            unique_features_used,
            usage_trend_pct,
            engagement_tier,
            api_events,
            dashboard_events,
            integration_events,
            automation_events
        from marts.fct_product_usage
        where account_id = ?
        order by usage_month desc
        limit 1
        """,
        [accountId],
    )

# helper for agent.py to concact all the retrieved information into a dict
def getAccountContext(conn: duckdb.DuckDBPyConnection, account: dict) -> dict:
    accountId = account["accountId"]

    return {
        "matchedAccount": account,
        "summary": getAccountSummary(conn, accountId),
        "opportunities": getOpportunities(conn, accountId),
        "calls": getCalls(conn, accountId),
        "marketing": getMarketing(conn, accountId),
        "productUsage": getProductUsage(conn, accountId),
    }

# turn money numbers into an actual money number (5000 -> $5,000)
def formatMoney(value) -> str:
    if value is None:
        return "unknown"
    return f"${int(value):,}"

