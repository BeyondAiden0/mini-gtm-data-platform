
  
    
    

    create  table
      "data"."marts"."fct_sigma_usage__dbt_tmp"
  
    as (
      -- Sigma Computing usage analytics — measures data adoption across the GTM org
-- Tracks who views which dashboards, how often, and how deeply they engage
with usage as (
    select * from "data"."staging"."stg_sigma_usage"
),

workbooks as (
    select * from "data"."staging"."stg_sigma_workbooks"
),

-- Monthly user-workbook aggregation
user_workbook_monthly as (
    select
        sigma_user_id,
        user_name,
        user_role,
        user_team,
        workbook_id,
        date_trunc('month', event_time::timestamp) as usage_month,
        count(*) as total_events,
        count(case when action = 'view' then 1 end) as views,
        count(case when action = 'explore' then 1 end) as explores,
        count(case when action = 'export' then 1 end) as exports,
        count(case when action = 'schedule' then 1 end) as schedules,
        count(case when action = 'embed_view' then 1 end) as embed_views,
        coalesce(sum(duration_seconds), 0) as total_duration_seconds,
        coalesce(avg(duration_seconds), 0) as avg_duration_seconds,
        coalesce(sum(queries_run), 0) as total_queries_run
    from usage
    group by
        sigma_user_id, user_name, user_role, user_team,
        workbook_id, date_trunc('month', event_time::timestamp)
)

select
    uwm.sigma_user_id,
    uwm.user_name,
    uwm.user_role,
    uwm.user_team,
    uwm.workbook_id,
    w.name as workbook_name,
    w.category as workbook_category,
    w.type as workbook_type,
    uwm.usage_month,
    uwm.total_events,
    uwm.views,
    uwm.explores,
    uwm.exports,
    uwm.schedules,
    uwm.embed_views,
    uwm.total_duration_seconds,
    round(uwm.total_duration_seconds / 60.0, 1) as total_duration_minutes,
    round(uwm.avg_duration_seconds, 1) as avg_duration_seconds,
    uwm.total_queries_run,

    -- Engagement tier
    case
        when uwm.total_events >= 20 then 'Power User'
        when uwm.total_events >= 10 then 'Regular'
        when uwm.total_events >= 3 then 'Occasional'
        else 'Rare'
    end as engagement_tier

from user_workbook_monthly uwm
left join workbooks w on uwm.workbook_id = w.workbook_id
    );
  
  