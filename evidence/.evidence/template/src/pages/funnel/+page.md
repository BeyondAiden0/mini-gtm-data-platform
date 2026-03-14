---
title: Full Funnel Analysis
---

# Full Funnel Analysis

Lead-to-close conversion, marketing attribution, and channel ROI.

## Funnel Overview

```sql funnel_summary
SELECT
    COUNT(*) as total_leads,
    COUNT(CASE WHEN reached_mql = true THEN 1 END) as mqls,
    COUNT(CASE WHEN reached_sql = true THEN 1 END) as sqls,
    COUNT(CASE WHEN reached_opportunity = true THEN 1 END) as opportunities,
    COUNT(CASE WHEN reached_closed_won = true THEN 1 END) as closed_won,
    COUNT(CASE WHEN reached_mql = true THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) as lead_to_mql_pct,
    COUNT(CASE WHEN reached_sql = true THEN 1 END)::DECIMAL / NULLIF(COUNT(CASE WHEN reached_mql = true THEN 1 END), 0) as mql_to_sql_pct,
    COUNT(CASE WHEN reached_opportunity = true THEN 1 END)::DECIMAL / NULLIF(COUNT(CASE WHEN reached_sql = true THEN 1 END), 0) as sql_to_opp_pct,
    COUNT(CASE WHEN reached_closed_won = true THEN 1 END)::DECIMAL / NULLIF(COUNT(CASE WHEN reached_opportunity = true THEN 1 END), 0) as opp_to_won_pct
FROM warehouse.fct_funnel
```

<BigValue
    data={funnel_summary}
    value=total_leads
    fmt='#,##0'
    title="Total Leads"
/>

<BigValue
    data={funnel_summary}
    value=mqls
    fmt='#,##0'
    title="MQLs"
/>

<BigValue
    data={funnel_summary}
    value=sqls
    fmt='#,##0'
    title="SQLs"
/>

<BigValue
    data={funnel_summary}
    value=opportunities
    fmt='#,##0'
    title="Opportunities"
/>

<BigValue
    data={funnel_summary}
    value=closed_won
    fmt='#,##0'
    title="Closed Won"
/>

## Conversion Rates

```sql conversion_rates
WITH funnel AS (
    SELECT
        COUNT(*) as total_leads,
        COUNT(CASE WHEN reached_mql = true THEN 1 END) as mqls,
        COUNT(CASE WHEN reached_sql = true THEN 1 END) as sqls,
        COUNT(CASE WHEN reached_opportunity = true THEN 1 END) as opportunities,
        COUNT(CASE WHEN reached_closed_won = true THEN 1 END) as closed_won
    FROM warehouse.fct_funnel
)
SELECT 'Lead → MQL' as stage, ROUND(mqls::DECIMAL / NULLIF(total_leads, 0) * 100, 1) as conversion_rate FROM funnel
UNION ALL
SELECT 'MQL → SQL', ROUND(sqls::DECIMAL / NULLIF(mqls, 0) * 100, 1) FROM funnel
UNION ALL
SELECT 'SQL → Opp', ROUND(opportunities::DECIMAL / NULLIF(sqls, 0) * 100, 1) FROM funnel
UNION ALL
SELECT 'Opp → Won', ROUND(closed_won::DECIMAL / NULLIF(opportunities, 0) * 100, 1) FROM funnel
```

<BarChart
    data={conversion_rates}
    x=stage
    y=conversion_rate
    title="Funnel Conversion Rates (%)"
    yFmt='#,##0.0'
/>

## Leads by Source

```sql source_performance
SELECT
    lead_source,
    COUNT(*) as total_leads,
    COUNT(CASE WHEN reached_mql = true THEN 1 END) as mqls,
    COUNT(CASE WHEN reached_opportunity = true THEN 1 END) as converted,
    COUNT(CASE WHEN reached_closed_won = true THEN 1 END) as won,
    SUM(CASE WHEN reached_closed_won = true THEN opp_amount ELSE 0 END) as won_revenue,
    COUNT(CASE WHEN reached_opportunity = true THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) as conversion_rate_pct
FROM warehouse.fct_funnel
WHERE lead_source IS NOT NULL
GROUP BY lead_source
ORDER BY total_leads DESC
```

<BarChart
    data={source_performance}
    x=lead_source
    y=total_leads
    title="Leads by Source"
/>

<DataTable data={source_performance} rows=15>
    <Column id=lead_source/>
    <Column id=total_leads fmt='#,##0'/>
    <Column id=mqls fmt='#,##0'/>
    <Column id=converted fmt='#,##0'/>
    <Column id=won fmt='#,##0'/>
    <Column id=won_revenue fmt='$#,##0'/>
    <Column id=conversion_rate_pct fmt='#,##0.0'/>
</DataTable>

## Marketing Channel ROI

```sql channel_roi
SELECT
    first_campaign_channel as channel,
    COUNT(DISTINCT lead_id) as leads_touched,
    COUNT(CASE WHEN reached_opportunity = true THEN 1 END) as conversions,
    SUM(CASE WHEN reached_closed_won = true THEN opp_amount ELSE 0 END) as revenue_influenced,
    COUNT(CASE WHEN reached_opportunity = true THEN 1 END)::DECIMAL / NULLIF(COUNT(DISTINCT lead_id), 0) as conversion_rate_pct
FROM warehouse.fct_funnel
WHERE first_campaign_channel IS NOT NULL
GROUP BY channel
ORDER BY revenue_influenced DESC
```

<BarChart
    data={channel_roi}
    x=channel
    y=revenue_influenced
    title="Revenue Influenced by Channel"
    yFmt='$#,##0'
/>

<DataTable data={channel_roi} rows=15>
    <Column id=channel/>
    <Column id=leads_touched fmt='#,##0'/>
    <Column id=conversions fmt='#,##0'/>
    <Column id=revenue_influenced fmt='$#,##0'/>
    <Column id=conversion_rate_pct fmt='#,##0.0'/>
</DataTable>

## Lead Volume Over Time

```sql monthly_leads
SELECT
    DATE_TRUNC('month', lead_created_at::date) as month,
    COUNT(*) as new_leads,
    COUNT(CASE WHEN reached_mql = true THEN 1 END) as mqls,
    COUNT(CASE WHEN reached_opportunity = true THEN 1 END) as converted
FROM warehouse.fct_funnel
GROUP BY month
ORDER BY month
```

<LineChart
    data={monthly_leads}
    x=month
    y={["new_leads", "mqls", "converted"]}
    title="Monthly Lead Volume"
/>

## Engagement Analysis

```sql engagement_vs_conversion
SELECT
    CASE
        WHEN total_activities = 0 THEN '0 activities'
        WHEN total_activities BETWEEN 1 AND 3 THEN '1-3 activities'
        WHEN total_activities BETWEEN 4 AND 7 THEN '4-7 activities'
        WHEN total_activities BETWEEN 8 AND 15 THEN '8-15 activities'
        ELSE '15+ activities'
    END as engagement_bucket,
    COUNT(*) as lead_count,
    COUNT(CASE WHEN reached_opportunity = true THEN 1 END) as converted,
    COUNT(CASE WHEN reached_opportunity = true THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) as conversion_rate_pct
FROM warehouse.fct_funnel
GROUP BY engagement_bucket
ORDER BY
    CASE engagement_bucket
        WHEN '0 activities' THEN 1
        WHEN '1-3 activities' THEN 2
        WHEN '4-7 activities' THEN 3
        WHEN '8-15 activities' THEN 4
        ELSE 5
    END
```

<BarChart
    data={engagement_vs_conversion}
    x=engagement_bucket
    y=conversion_rate_pct
    title="Conversion Rate by Engagement Level (%)"
    yFmt='#,##0.0'
/>

<DataTable data={engagement_vs_conversion}>
    <Column id=engagement_bucket/>
    <Column id=lead_count fmt='#,##0'/>
    <Column id=converted fmt='#,##0'/>
    <Column id=conversion_rate_pct fmt='#,##0.0'/>
</DataTable>

## Campaign Type Performance

```sql campaign_type_perf
SELECT
    first_campaign_type as campaign_type,
    COUNT(DISTINCT lead_id) as leads,
    COUNT(CASE WHEN reached_mql = true THEN 1 END) as mqls,
    COUNT(CASE WHEN reached_opportunity = true THEN 1 END) as converted,
    SUM(CASE WHEN reached_closed_won = true THEN opp_amount ELSE 0 END) as revenue
FROM warehouse.fct_funnel
WHERE first_campaign_type IS NOT NULL
GROUP BY campaign_type
ORDER BY revenue DESC
```

<BarChart
    data={campaign_type_perf}
    x=campaign_type
    y=revenue
    title="Revenue by Campaign Type"
    yFmt='$#,##0'
/>

