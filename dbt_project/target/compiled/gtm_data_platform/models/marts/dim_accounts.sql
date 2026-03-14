-- Account dimension enriched with opportunity summary stats
-- Provides a single view of each account with pipeline and revenue metrics
with accounts as (
    select * from "data"."staging"."stg_accounts"
),

opp_stats as (
    select
        account_id,
        count(*) as total_opportunities,
        count(case when is_closed = false then 1 end) as open_opportunities,
        count(case when is_won = true then 1 end) as won_opportunities,
        count(case when stage = 'Closed Lost' then 1 end) as lost_opportunities,
        sum(case when is_closed = false then amount else 0 end) as open_pipeline,
        sum(case when is_won = true then amount else 0 end) as closed_won_revenue,
        avg(case when is_won = true then amount end) as avg_won_deal_size,
        min(created_date) as first_opp_date,
        max(created_date) as last_opp_date
    from "data"."staging"."stg_opportunities"
    group by account_id
),

contact_stats as (
    select
        account_id,
        count(*) as contact_count,
        count(case when role = 'Champion' then 1 end) as champion_count,
        count(case when role = 'Economic Buyer' then 1 end) as economic_buyer_count
    from "data"."staging"."stg_contacts"
    group by account_id
)

select
    a.account_id,
    a.name,
    a.industry,
    a.employee_count,
    a.arr,
    a.region,
    a.owner_id,
    a.created_at,

    -- Opportunity metrics
    coalesce(o.total_opportunities, 0) as total_opportunities,
    coalesce(o.open_opportunities, 0) as open_opportunities,
    coalesce(o.won_opportunities, 0) as won_opportunities,
    coalesce(o.lost_opportunities, 0) as lost_opportunities,
    coalesce(o.open_pipeline, 0) as open_pipeline,
    coalesce(o.closed_won_revenue, 0) as closed_won_revenue,
    o.avg_won_deal_size,
    o.first_opp_date,
    o.last_opp_date,

    -- Contact metrics
    coalesce(c.contact_count, 0) as contact_count,
    coalesce(c.champion_count, 0) as champion_count,
    coalesce(c.economic_buyer_count, 0) as economic_buyer_count,

    -- Derived fields
    case
        when a.employee_count <= 200 then 'SMB'
        when a.employee_count <= 2000 then 'Mid-Market'
        else 'Enterprise'
    end as segment

from accounts a
left join opp_stats o on a.account_id = o.account_id
left join contact_stats c on a.account_id = c.account_id