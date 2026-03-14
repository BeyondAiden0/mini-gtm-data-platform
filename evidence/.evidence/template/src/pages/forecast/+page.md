---
title: Forecast & Commit
---

# Forecast & Commit Analysis

Pipeline forecast by category, rep-level performance, and quarterly trends.

## Forecast Summary

```sql forecast_summary
SELECT
    forecast_category,
    COUNT(DISTINCT opp_id) as deal_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_deal_size
FROM warehouse.fct_opportunities
WHERE is_closed = false OR forecast_category = 'Closed'
GROUP BY forecast_category
ORDER BY
    CASE forecast_category
        WHEN 'Closed' THEN 1
        WHEN 'Commit' THEN 2
        WHEN 'Best Case' THEN 3
        WHEN 'Pipeline' THEN 4
        WHEN 'Omitted' THEN 5
    END
```

<BarChart
    data={forecast_summary}
    x=forecast_category
    y=total_amount
    title="Pipeline by Forecast Category"
    yFmt='$#,##0'
/>

<DataTable data={forecast_summary}>
    <Column id=forecast_category/>
    <Column id=deal_count fmt='#,##0'/>
    <Column id=total_amount fmt='$#,##0'/>
    <Column id=avg_deal_size fmt='$#,##0'/>
</DataTable>

## Weighted Pipeline

```sql weighted_pipeline
SELECT
    forecast_category,
    SUM(amount) as unweighted,
    SUM(CASE forecast_category
        WHEN 'Commit' THEN amount * 0.90
        WHEN 'Best Case' THEN amount * 0.50
        WHEN 'Pipeline' THEN amount * 0.20
        ELSE 0
    END) as weighted
FROM warehouse.fct_opportunities
WHERE is_closed = false
GROUP BY forecast_category
ORDER BY
    CASE forecast_category
        WHEN 'Commit' THEN 1
        WHEN 'Best Case' THEN 2
        WHEN 'Pipeline' THEN 3
        ELSE 4
    END
```

<BarChart
    data={weighted_pipeline}
    x=forecast_category
    y={["unweighted", "weighted"]}
    title="Weighted vs Unweighted Pipeline"
    yFmt='$#,##0'
/>

## Quarterly Trends

```sql quarterly_trends
SELECT
    DATE_TRUNC('quarter', close_date::date) as quarter,
    SUM(CASE WHEN is_won = true THEN amount ELSE 0 END) as closed_won,
    SUM(CASE WHEN is_closed = false THEN amount ELSE 0 END) as still_open,
    SUM(CASE WHEN stage = 'Closed Lost' THEN amount ELSE 0 END) as closed_lost,
    COUNT(DISTINCT CASE WHEN is_won = true THEN opp_id END) as won_count
FROM warehouse.fct_opportunities
GROUP BY quarter
ORDER BY quarter
```

<LineChart
    data={quarterly_trends}
    x=quarter
    y={["closed_won", "closed_lost"]}
    title="Quarterly Closed Won vs Lost"
    yFmt='$#,##0'
/>

## Rep Performance

```sql rep_performance
SELECT
    rep_name,
    closed_won_revenue,
    open_pipeline,
    commit_amount,
    best_case_amount,
    won_deals,
    win_rate,
    avg_deal_size,
    total_calls,
    completed_calls
FROM warehouse.dim_reps
ORDER BY closed_won_revenue DESC
```

<DataTable data={rep_performance} rows=20>
    <Column id=rep_name/>
    <Column id=closed_won_revenue fmt='$#,##0'/>
    <Column id=open_pipeline fmt='$#,##0'/>
    <Column id=commit_amount fmt='$#,##0'/>
    <Column id=best_case_amount fmt='$#,##0'/>
    <Column id=won_deals fmt='#,##0'/>
    <Column id=win_rate fmt='#,##0.0%'/>
    <Column id=avg_deal_size fmt='$#,##0'/>
    <Column id=total_calls fmt='#,##0'/>
</DataTable>

## Rep Commit Breakdown

```sql rep_commit
SELECT
    rep_name,
    commit_amount,
    best_case_amount,
    open_pipeline,
    closed_won_revenue
FROM warehouse.dim_reps
WHERE commit_amount > 0 OR best_case_amount > 0
ORDER BY commit_amount DESC
```

<BarChart
    data={rep_commit}
    x=rep_name
    y={["commit_amount", "best_case_amount"]}
    title="Rep Commit vs Best Case"
    yFmt='$#,##0'
/>

## Win Rate by Lead Source

```sql source_win_rate
SELECT
    lead_source,
    COUNT(DISTINCT opp_id) as deals,
    COUNT(DISTINCT CASE WHEN is_won = true THEN opp_id END) as won,
    SUM(CASE WHEN is_won = true THEN amount ELSE 0 END) as won_revenue,
    COUNT(DISTINCT CASE WHEN is_won = true THEN opp_id END)::DECIMAL
        / NULLIF(COUNT(DISTINCT CASE WHEN is_closed = true THEN opp_id END), 0)
    as win_rate_pct,
    AVG(CASE WHEN is_won = true THEN cycle_days END) as avg_cycle_days
FROM warehouse.fct_opportunities
WHERE lead_source IS NOT NULL
GROUP BY lead_source
ORDER BY won_revenue DESC
```

<BarChart
    data={source_win_rate}
    x=lead_source
    y=win_rate_pct
    title="Win Rate by Lead Source (%)"
    yFmt='#,##0.0'
/>

<DataTable data={source_win_rate}>
    <Column id=lead_source/>
    <Column id=deals fmt='#,##0'/>
    <Column id=won fmt='#,##0'/>
    <Column id=won_revenue fmt='$#,##0'/>
    <Column id=win_rate_pct fmt='#,##0.0'/>
    <Column id=avg_cycle_days fmt='#,##0'/>
</DataTable>

## Deal Velocity by Segment

```sql velocity_by_segment
SELECT
    account_segment,
    AVG(CASE WHEN is_won = true THEN cycle_days END) as avg_won_cycle_days,
    AVG(CASE WHEN stage = 'Closed Lost' THEN cycle_days END) as avg_lost_cycle_days,
    AVG(CASE WHEN is_won = true THEN amount END) as avg_won_amount
FROM warehouse.fct_opportunities
WHERE is_closed = true
GROUP BY account_segment
ORDER BY avg_won_cycle_days
```

<BarChart
    data={velocity_by_segment}
    x=account_segment
    y={["avg_won_cycle_days", "avg_lost_cycle_days"]}
    title="Average Sales Cycle by Segment (days)"
    yFmt='#,##0'
/>

