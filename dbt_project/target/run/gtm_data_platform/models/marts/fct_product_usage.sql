
  
    
    

    create  table
      "data"."marts"."fct_product_usage__dbt_tmp"
  
    as (
      -- Account-level monthly product usage aggregation
-- Enables health scoring, expansion signals, and churn prediction
with events as (
    select * from "data"."staging"."stg_product_events"
),

users as (
    select * from "data"."staging"."stg_product_users"
),

accounts as (
    select * from "data"."staging"."stg_accounts"
),

monthly_usage as (
    select
        e.account_id,
        date_trunc('month', e.event_timestamp::date) as usage_month,
        count(distinct e.product_user_id) as active_users,
        count(*) as total_events,
        count(distinct e.feature) as unique_features_used,
        count(case when e.feature = 'API' then 1 end) as api_events,
        count(case when e.feature = 'Reports' then 1 end) as report_events,
        count(case when e.feature = 'Dashboard Builder' then 1 end) as dashboard_events,
        count(case when e.feature = 'Integrations' then 1 end) as integration_events,
        count(case when e.feature = 'Workflow Automation' then 1 end) as automation_events,
        count(case when e.feature = 'Data Export' then 1 end) as export_events,
        count(case when e.action = 'create' then 1 end) as create_actions,
        count(case when e.action = 'view' then 1 end) as view_actions
    from events e
    group by e.account_id, date_trunc('month', e.event_timestamp::date)
),

with_trends as (
    select
        mu.*,
        lag(mu.total_events) over (
            partition by mu.account_id order by mu.usage_month
        ) as prev_month_events,
        case
            when lag(mu.total_events) over (partition by mu.account_id order by mu.usage_month) is null then null
            when lag(mu.total_events) over (partition by mu.account_id order by mu.usage_month) = 0 then null
            else (mu.total_events - lag(mu.total_events) over (partition by mu.account_id order by mu.usage_month))::decimal
                / lag(mu.total_events) over (partition by mu.account_id order by mu.usage_month)
        end as usage_trend_pct
    from monthly_usage mu
)

select
    t.account_id,
    a.name as account_name,
    a.industry,
    a.arr as account_arr,
    case
        when a.employee_count <= 200 then 'SMB'
        when a.employee_count <= 2000 then 'Mid-Market'
        else 'Enterprise'
    end as account_segment,
    t.usage_month,
    t.active_users,
    t.total_events,
    t.unique_features_used,
    t.api_events,
    t.report_events,
    t.dashboard_events,
    t.integration_events,
    t.automation_events,
    t.export_events,
    t.create_actions,
    t.view_actions,
    t.prev_month_events,
    t.usage_trend_pct,
    case
        when t.total_events >= 100 and t.unique_features_used >= 5 then 'Power User'
        when t.total_events >= 30 then 'Regular'
        when t.total_events >= 5 then 'Occasional'
        else 'Rare'
    end as engagement_tier

from with_trends t
left join accounts a on t.account_id = a.account_id
    );
  
  