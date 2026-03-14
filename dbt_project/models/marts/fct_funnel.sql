-- Lead-to-opportunity-to-close funnel with marketing attribution
-- Combines lead lifecycle with opportunity outcomes for full-funnel analysis
with leads as (
    select * from {{ ref('stg_leads') }}
),

lead_activity_stats as (
    select
        lead_id,
        count(*) as total_activities,
        count(distinct campaign_id) as campaigns_touched,
        min(activity_date) as first_activity_date,
        max(activity_date) as last_activity_date,
        count(case when activity_type = 'Form Fill' then 1 end) as form_fills,
        count(case when activity_type = 'Email Click' then 1 end) as email_clicks,
        count(case when activity_type = 'Webinar Attended' then 1 end) as webinars_attended,
        count(case when activity_type = 'Content Download' then 1 end) as content_downloads
    from {{ ref('stg_lead_activities') }}
    group by lead_id
),

-- Get campaign details for the first campaign a lead touched
first_campaign as (
    select distinct on (la.lead_id)
        la.lead_id,
        la.campaign_id as first_campaign_id,
        c.name as first_campaign_name,
        c.channel as first_campaign_channel,
        c.type as first_campaign_type,
        c.cost as first_campaign_cost
    from {{ ref('stg_lead_activities') }} la
    inner join {{ ref('stg_campaigns') }} c on la.campaign_id = c.campaign_id
    where la.campaign_id is not null
    order by la.lead_id, la.activity_date
),

-- Get opportunity outcome if lead converted
opp_outcome as (
    select
        opp_id,
        stage,
        amount,
        is_won,
        is_closed,
        close_date,
        created_date as opp_created_date
    from {{ ref('stg_opportunities') }}
)

select
    l.lead_id,
    l.first_name,
    l.last_name,
    l.email,
    l.company,
    l.source as lead_source,
    l.status as lead_status,
    l.score as lead_score,
    l.created_at as lead_created_at,

    -- Conversion info
    l.converted_opp_id,
    l.converted_account_id,
    l.converted_date,
    case when l.converted_opp_id is not null then true else false end as is_converted,

    -- Activity engagement
    coalesce(la.total_activities, 0) as total_activities,
    coalesce(la.campaigns_touched, 0) as campaigns_touched,
    la.first_activity_date,
    la.last_activity_date,
    coalesce(la.form_fills, 0) as form_fills,
    coalesce(la.email_clicks, 0) as email_clicks,
    coalesce(la.webinars_attended, 0) as webinars_attended,
    coalesce(la.content_downloads, 0) as content_downloads,

    -- First touch campaign attribution
    fc.first_campaign_id,
    fc.first_campaign_name,
    fc.first_campaign_channel,
    fc.first_campaign_type,
    fc.first_campaign_cost,

    -- Opportunity outcome (if converted)
    oo.stage as opp_stage,
    oo.amount as opp_amount,
    oo.is_won as opp_is_won,
    oo.is_closed as opp_is_closed,
    oo.close_date as opp_close_date,
    oo.opp_created_date,

    -- Funnel stage flags
    case when l.status in ('MQL', 'SQL', 'Converted') then true else false end as reached_mql,
    case when l.status in ('SQL', 'Converted') then true else false end as reached_sql,
    case when l.converted_opp_id is not null then true else false end as reached_opportunity,
    case when oo.is_won = true then true else false end as reached_closed_won

from leads l
left join lead_activity_stats la on l.lead_id = la.lead_id
left join first_campaign fc on l.lead_id = fc.lead_id
left join opp_outcome oo on l.converted_opp_id = oo.opp_id

