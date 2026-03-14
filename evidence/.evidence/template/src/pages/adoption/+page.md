---
title: Product Usage & Adoption
---

# Product Usage & Adoption

Track how customers use your product. Identify expansion opportunities, churn risk, and feature adoption gaps.

## Overall Usage Metrics

```sql usage_overview
SELECT
    COUNT(DISTINCT account_id) as active_accounts,
    SUM(total_events) as total_events,
    SUM(active_users) as total_user_months,
    ROUND(AVG(total_events), 1) as avg_events_per_account_month,
    ROUND(AVG(active_users), 1) as avg_users_per_account_month,
    ROUND(AVG(unique_features_used), 1) as avg_features_used
FROM warehouse.fct_product_usage
```

<BigValue
    data={usage_overview}
    value=active_accounts
    fmt='#,##0'
    title="Active Accounts"
/>

<BigValue
    data={usage_overview}
    value=total_events
    fmt='#,##0'
    title="Total Events"
/>

<BigValue
    data={usage_overview}
    value=avg_events_per_account_month
    fmt='#,##0.0'
    title="Avg Events / Account / Month"
/>

<BigValue
    data={usage_overview}
    value=avg_features_used
    fmt='#,##0.0'
    title="Avg Features Used"
/>

## Usage Trend Over Time

```sql monthly_usage
SELECT
    usage_month,
    COUNT(DISTINCT account_id) as active_accounts,
    SUM(active_users) as active_users,
    SUM(total_events) as total_events
FROM warehouse.fct_product_usage
GROUP BY usage_month
ORDER BY usage_month
```

<LineChart
    data={monthly_usage}
    x=usage_month
    y={["active_accounts", "active_users"]}
    title="Monthly Active Accounts & Users"
/>

<LineChart
    data={monthly_usage}
    x=usage_month
    y=total_events
    title="Monthly Events"
/>

## Usage by Account Segment

```sql segment_usage
SELECT
    account_segment,
    COUNT(DISTINCT account_id) as accounts,
    ROUND(AVG(total_events), 0) as avg_events,
    ROUND(AVG(active_users), 1) as avg_users,
    ROUND(AVG(unique_features_used), 1) as avg_features,
    SUM(api_events) as total_api_events,
    SUM(automation_events) as total_automation_events
FROM warehouse.fct_product_usage
GROUP BY account_segment
ORDER BY avg_events DESC
```

<BarChart
    data={segment_usage}
    x=account_segment
    y=avg_events
    title="Avg Monthly Events by Segment"
/>

<DataTable data={segment_usage}>
    <Column id=account_segment/>
    <Column id=accounts fmt='#,##0'/>
    <Column id=avg_events fmt='#,##0'/>
    <Column id=avg_users fmt='#,##0.0'/>
    <Column id=avg_features fmt='#,##0.0'/>
    <Column id=total_api_events fmt='#,##0'/>
    <Column id=total_automation_events fmt='#,##0'/>
</DataTable>

## Feature Adoption

```sql feature_adoption
SELECT
    'Dashboard Builder' as feature, SUM(dashboard_events) as events FROM warehouse.fct_product_usage
UNION ALL SELECT 'Reports', SUM(report_events) FROM warehouse.fct_product_usage
UNION ALL SELECT 'API', SUM(api_events) FROM warehouse.fct_product_usage
UNION ALL SELECT 'Integrations', SUM(integration_events) FROM warehouse.fct_product_usage
UNION ALL SELECT 'Workflow Automation', SUM(automation_events) FROM warehouse.fct_product_usage
UNION ALL SELECT 'Data Export', SUM(export_events) FROM warehouse.fct_product_usage
ORDER BY events DESC
```

<BarChart
    data={feature_adoption}
    x=feature
    y=events
    title="Feature Usage (Total Events)"
/>

## Engagement Tiers

```sql engagement_tiers
SELECT
    engagement_tier,
    COUNT(DISTINCT account_id) as accounts,
    ROUND(AVG(total_events), 0) as avg_events,
    ROUND(AVG(active_users), 1) as avg_users,
    ROUND(AVG(unique_features_used), 1) as avg_features
FROM warehouse.fct_product_usage
GROUP BY engagement_tier
ORDER BY
    CASE engagement_tier
        WHEN 'Power User' THEN 1
        WHEN 'Regular' THEN 2
        WHEN 'Occasional' THEN 3
        WHEN 'Rare' THEN 4
    END
```

<BarChart
    data={engagement_tiers}
    x=engagement_tier
    y=accounts
    title="Accounts by Engagement Tier"
/>

<DataTable data={engagement_tiers}>
    <Column id=engagement_tier/>
    <Column id=accounts fmt='#,##0'/>
    <Column id=avg_events fmt='#,##0'/>
    <Column id=avg_users fmt='#,##0.0'/>
    <Column id=avg_features fmt='#,##0.0'/>
</DataTable>

## Usage vs Revenue

```sql usage_vs_arr
SELECT
    account_segment,
    engagement_tier,
    COUNT(DISTINCT account_id) as accounts,
    ROUND(AVG(account_arr), 0) as avg_arr,
    ROUND(AVG(total_events), 0) as avg_events
FROM warehouse.fct_product_usage
WHERE account_arr IS NOT NULL AND account_arr > 0
GROUP BY account_segment, engagement_tier
ORDER BY account_segment, avg_arr DESC
```

<DataTable data={usage_vs_arr} rows=20>
    <Column id=account_segment/>
    <Column id=engagement_tier/>
    <Column id=accounts fmt='#,##0'/>
    <Column id=avg_arr fmt='$#,##0'/>
    <Column id=avg_events fmt='#,##0'/>
</DataTable>

## Top Accounts by Usage

```sql top_accounts
SELECT
    account_name,
    account_segment,
    account_arr,
    SUM(total_events) as total_events,
    MAX(active_users) as peak_users,
    ROUND(AVG(unique_features_used), 0) as avg_features,
    MAX(engagement_tier) as latest_tier
FROM warehouse.fct_product_usage
WHERE account_name IS NOT NULL
GROUP BY account_name, account_segment, account_arr
ORDER BY total_events DESC
LIMIT 25
```

<DataTable data={top_accounts} rows=25 search=true>
    <Column id=account_name/>
    <Column id=account_segment/>
    <Column id=account_arr fmt='$#,##0'/>
    <Column id=total_events fmt='#,##0'/>
    <Column id=peak_users fmt='#,##0'/>
    <Column id=avg_features fmt='#,##0'/>
    <Column id=latest_tier/>
</DataTable>
