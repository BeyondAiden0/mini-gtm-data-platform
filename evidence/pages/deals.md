---
title: Deal Intelligence
---

# Deal Intelligence

Win/loss analysis, competitive intelligence from sales calls, and deal inspection.

## Win/Loss Summary

```sql win_loss
SELECT
    CASE
        WHEN is_won = true THEN 'Won'
        WHEN stage = 'Closed Lost' THEN 'Lost'
        ELSE 'Open'
    END as outcome,
    COUNT(DISTINCT opp_id) as deal_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_deal_size,
    AVG(cycle_days) as avg_cycle_days,
    AVG(total_calls) as avg_calls_per_deal
FROM warehouse.fct_opportunities
GROUP BY outcome
ORDER BY total_amount DESC
```

<DataTable data={win_loss}>
    <Column id=outcome/>
    <Column id=deal_count fmt='#,##0'/>
    <Column id=total_amount fmt='$#,##0'/>
    <Column id=avg_deal_size fmt='$#,##0'/>
    <Column id=avg_cycle_days fmt='#,##0'/>
    <Column id=avg_calls_per_deal fmt='#,##0.0'/>
</DataTable>

## Win Rate by Segment

```sql win_rate_segment
SELECT
    account_segment,
    COUNT(DISTINCT CASE WHEN is_won = true THEN opp_id END) as won,
    COUNT(DISTINCT CASE WHEN stage = 'Closed Lost' THEN opp_id END) as lost,
    COUNT(DISTINCT CASE WHEN is_closed = true THEN opp_id END) as total_closed,
    COUNT(DISTINCT CASE WHEN is_won = true THEN opp_id END)::DECIMAL
        / NULLIF(COUNT(DISTINCT CASE WHEN is_closed = true THEN opp_id END), 0)
    as win_rate_pct
FROM warehouse.fct_opportunities
GROUP BY account_segment
ORDER BY win_rate_pct DESC
```

<BarChart
    data={win_rate_segment}
    x=account_segment
    y=win_rate_pct
    title="Win Rate by Account Segment (%)"
    yFmt='#,##0.0'
/>

## Loss Reasons

```sql loss_reasons
SELECT
    loss_reason,
    COUNT(*) as deal_count,
    SUM(amount) as total_amount_lost,
    AVG(amount) as avg_deal_size
FROM warehouse.fct_opportunities
WHERE stage = 'Closed Lost'
    AND loss_reason IS NOT NULL
GROUP BY loss_reason
ORDER BY deal_count DESC
```

<BarChart
    data={loss_reasons}
    x=loss_reason
    y=deal_count
    title="Top Loss Reasons"
/>

<DataTable data={loss_reasons}>
    <Column id=loss_reason/>
    <Column id=deal_count fmt='#,##0'/>
    <Column id=total_amount_lost fmt='$#,##0'/>
    <Column id=avg_deal_size fmt='$#,##0'/>
</DataTable>

## Competitive Intel from Call Trackers

```sql competitor_analysis
SELECT
    competitor,
    COUNT(DISTINCT opp_id) as deals,
    COUNT(DISTINCT CASE WHEN is_won = true THEN opp_id END) as won,
    COUNT(DISTINCT CASE WHEN stage = 'Closed Lost' THEN opp_id END) as lost,
    COUNT(DISTINCT CASE WHEN is_won = true THEN opp_id END)::DECIMAL
        / NULLIF(COUNT(DISTINCT CASE WHEN is_closed = true THEN opp_id END), 0)
    as win_rate_pct,
    AVG(competitor_mentions) as avg_competitor_mentions
FROM warehouse.fct_opportunities
WHERE competitor IS NOT NULL
GROUP BY competitor
ORDER BY deals DESC
```

<BarChart
    data={competitor_analysis}
    x=competitor
    y=win_rate_pct
    title="Win Rate Against Competitors (%)"
/>

<DataTable data={competitor_analysis}>
    <Column id=competitor/>
    <Column id=deals fmt='#,##0'/>
    <Column id=won fmt='#,##0'/>
    <Column id=lost fmt='#,##0'/>
    <Column id=win_rate_pct fmt='#,##0.0'/>
    <Column id=avg_competitor_mentions fmt='#,##0.0'/>
</DataTable>

## Call Insights - Won vs Lost Deals

```sql call_insights
SELECT
    CASE WHEN is_won = true THEN 'Won' ELSE 'Lost' END as outcome,
    AVG(total_calls) as avg_calls,
    AVG(total_call_minutes) as avg_total_minutes,
    AVG(avg_talk_ratio) as avg_rep_talk_ratio,
    AVG(avg_questions_per_call) as avg_questions,
    AVG(calls_with_next_steps) as avg_next_steps_calls,
    AVG(competitor_mentions) as avg_competitor_mentions,
    AVG(pricing_mentions) as avg_pricing_mentions,
    AVG(risk_mentions) as avg_risk_mentions
FROM warehouse.fct_opportunities
WHERE is_closed = true
GROUP BY outcome
```

<DataTable data={call_insights} rows=10>
    <Column id=outcome/>
    <Column id=avg_calls fmt='#,##0.1'/>
    <Column id=avg_total_minutes fmt='#,##0'/>
    <Column id=avg_rep_talk_ratio fmt='#,##0.0%'/>
    <Column id=avg_questions fmt='#,##0.1'/>
    <Column id=avg_next_steps_calls fmt='#,##0.1'/>
    <Column id=avg_competitor_mentions fmt='#,##0.1'/>
    <Column id=avg_pricing_mentions fmt='#,##0.1'/>
    <Column id=avg_risk_mentions fmt='#,##0.1'/>
</DataTable>

## Stage Conversion Rates

```sql stage_conversion
SELECT
    sh.stage,
    COUNT(DISTINCT sh.opp_id) as total_deals,
    COUNT(DISTINCT CASE WHEN o.is_won = true THEN sh.opp_id END) as eventually_won,
    COUNT(DISTINCT CASE WHEN o.is_won = true THEN sh.opp_id END)::DECIMAL
        / NULLIF(COUNT(DISTINCT sh.opp_id), 0)
    as pct_eventually_won
FROM warehouse.stg_stage_history sh
INNER JOIN warehouse.stg_opportunities o ON sh.opp_id = o.opp_id
WHERE sh.stage NOT IN ('Closed Won', 'Closed Lost')
GROUP BY sh.stage
ORDER BY
    CASE sh.stage
        WHEN 'Prospecting' THEN 1
        WHEN 'Discovery' THEN 2
        WHEN 'Qualification' THEN 3
        WHEN 'Proposal' THEN 4
        WHEN 'Negotiation' THEN 5
    END
```

<BarChart
    data={stage_conversion}
    x=stage
    y=pct_eventually_won
    title="Win Rate by Stage Reached (%)"
    yFmt='#,##0.0%'
/>

## Deal Segment Filter

<Dropdown name=segment>
    <DropdownOption value=% valueLabel="All Segments"/>
    <DropdownOption value="SMB"/>
    <DropdownOption value="Mid-Market"/>
    <DropdownOption value="Enterprise"/>
</Dropdown>

```sql filtered_deals
SELECT
    opp_name,
    account_name,
    account_segment,
    stage,
    amount,
    close_date,
    total_calls,
    competitor,
    cycle_days
FROM warehouse.fct_opportunities
WHERE account_segment LIKE '${inputs.segment.value}'
ORDER BY amount DESC
LIMIT 50
```

<DataTable data={filtered_deals} rows=20 search=true>
    <Column id=opp_name/>
    <Column id=account_name/>
    <Column id=account_segment/>
    <Column id=stage/>
    <Column id=amount fmt='$#,##0'/>
    <Column id=close_date/>
    <Column id=total_calls fmt='#,##0'/>
    <Column id=competitor/>
    <Column id=cycle_days fmt='#,##0'/>
</DataTable>

