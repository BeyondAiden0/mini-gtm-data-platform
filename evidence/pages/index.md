---
title: GTM Pipeline Overview
---

# Pipeline Overview

Welcome to the GTM Data Platform dashboard. Track pipeline health, deal velocity, and forecast across your go-to-market organization.

## Key Metrics

```sql pipeline_summary
SELECT
    COUNT(DISTINCT opp_id) as total_opportunities,
    COUNT(DISTINCT CASE WHEN is_closed = false THEN opp_id END) as open_deals,
    COUNT(DISTINCT CASE WHEN is_won = true THEN opp_id END) as won_deals,
    SUM(CASE WHEN is_closed = false THEN amount ELSE 0 END) as open_pipeline,
    SUM(CASE WHEN is_won = true THEN amount ELSE 0 END) as closed_won_revenue,
    AVG(CASE WHEN is_won = true THEN amount END) as avg_won_deal_size,
    AVG(CASE WHEN is_won = true THEN cycle_days END) as avg_sales_cycle_days
FROM warehouse.fct_opportunities
```

<BigValue
    data={pipeline_summary}
    value=open_pipeline
    fmt='$#,##0'
    title="Open Pipeline"
/>

<BigValue
    data={pipeline_summary}
    value=closed_won_revenue
    fmt='$#,##0'
    title="Closed Won Revenue"
/>

<BigValue
    data={pipeline_summary}
    value=open_deals
    fmt='#,##0'
    title="Open Deals"
/>

<BigValue
    data={pipeline_summary}
    value=avg_won_deal_size
    fmt='$#,##0'
    title="Avg Won Deal Size"
/>

<BigValue
    data={pipeline_summary}
    value=avg_sales_cycle_days
    fmt='#,##0'
    title="Avg Sales Cycle (days)"
/>

## Pipeline by Stage

```sql stage_distribution
SELECT
    stage,
    COUNT(DISTINCT opp_id) as deal_count,
    SUM(amount) as total_amount
FROM warehouse.fct_opportunities
WHERE is_closed = false
GROUP BY stage
ORDER BY
    CASE stage
        WHEN 'Prospecting' THEN 1
        WHEN 'Discovery' THEN 2
        WHEN 'Qualification' THEN 3
        WHEN 'Proposal' THEN 4
        WHEN 'Negotiation' THEN 5
        ELSE 6
    END
```

<BarChart
    data={stage_distribution}
    x=stage
    y=total_amount
    title="Open Pipeline by Stage"
    yFmt='$#,##0'
/>

## Monthly Pipeline Trend

```sql monthly_pipeline
SELECT
    DATE_TRUNC('month', created_date::date) as month,
    SUM(CASE WHEN is_closed = false THEN amount ELSE 0 END) as pipeline_created,
    SUM(CASE WHEN is_won = true THEN amount ELSE 0 END) as closed_won,
    COUNT(DISTINCT opp_id) as deals_created
FROM warehouse.fct_opportunities
GROUP BY month
ORDER BY month
```

<LineChart
    data={monthly_pipeline}
    x=month
    y={["pipeline_created", "closed_won"]}
    title="Monthly Pipeline Created vs Closed Won"
    yFmt='$#,##0'
/>

## Pipeline by Segment

```sql segment_pipeline
SELECT
    account_segment,
    COUNT(DISTINCT opp_id) as deals,
    SUM(CASE WHEN is_closed = false THEN amount ELSE 0 END) as open_pipeline,
    SUM(CASE WHEN is_won = true THEN amount ELSE 0 END) as closed_won,
    AVG(CASE WHEN is_won = true THEN amount END) as avg_deal_size
FROM warehouse.fct_opportunities
GROUP BY account_segment
ORDER BY open_pipeline DESC
```

<BarChart
    data={segment_pipeline}
    x=account_segment
    y={["open_pipeline", "closed_won"]}
    title="Pipeline by Account Segment"
    yFmt='$#,##0'
/>

## Pipeline by Region

```sql region_pipeline
SELECT
    region,
    COUNT(DISTINCT opp_id) as deals,
    SUM(CASE WHEN is_closed = false THEN amount ELSE 0 END) as open_pipeline,
    SUM(CASE WHEN is_won = true THEN amount ELSE 0 END) as closed_won
FROM warehouse.fct_opportunities
WHERE region IS NOT NULL
GROUP BY region
ORDER BY open_pipeline DESC
```

<BarChart
    data={region_pipeline}
    x=region
    y=open_pipeline
    title="Open Pipeline by Region"
    yFmt='$#,##0'
/>

## Navigation

- [Deal Intelligence](/deals) - Win/loss analysis, competitive intel, call insights
- [Full Funnel](/funnel) - Lead-to-close conversion, marketing attribution
- [Forecast](/forecast) - Forecast by category, rep-level commit analysis
- [Product Usage](/adoption) - Product analytics, feature adoption, account health

## Data Sources

This dashboard is powered by:
- **DuckDB Warehouse**: `warehouse/data.duckdb`
- **dbt Models**: `marts.fct_opportunities`, `marts.fct_calls`, `marts.fct_funnel`, `marts.dim_accounts`, `marts.dim_reps`, `marts.fct_product_usage`
- **Raw Data Sources**: CRM (accounts, opportunities, contacts, leads), Sales Calls (calls, trackers), Marketing (campaigns, lead activities), Product Analytics (users, events)

