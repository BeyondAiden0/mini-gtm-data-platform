
  
    
    

    create  table
      "data"."marts"."fct_opportunities__dbt_tmp"
  
    as (
      -- Denormalized opportunity facts with account, rep, call stats, and marketing context
-- Central fact table for pipeline and deal intelligence analysis
with opportunities as (
    select * from "data"."staging"."stg_opportunities"
),

accounts as (
    select * from "data"."staging"."stg_accounts"
),

-- Aggregate call stats per opportunity
opp_call_stats as (
    select
        opp_id,
        count(*) as total_calls,
        count(case when disposition = 'Completed' then 1 end) as completed_calls,
        sum(case when disposition = 'Completed' then duration_minutes else 0 end) as total_call_minutes,
        avg(case when disposition = 'Completed' then talk_ratio_rep end) as avg_talk_ratio,
        avg(case when disposition = 'Completed' then question_count end) as avg_questions_per_call,
        sum(case when next_steps_mentioned = true then 1 else 0 end) as calls_with_next_steps,
        min(call_date) as first_call_date,
        max(call_date) as last_call_date
    from "data"."staging"."stg_calls"
    group by opp_id
),

-- Count competitor mentions from call trackers per opportunity
opp_tracker_intelligence as (
    select
        c.opp_id,
        sum(case when ct.tracker_category = 'Competitor' then ct.mention_count else 0 end) as competitor_mentions,
        sum(case when ct.tracker_category in ('Pricing', 'Discount', 'Budget') then ct.mention_count else 0 end) as pricing_mentions,
        sum(case when ct.tracker_category = 'Risk' then ct.mention_count else 0 end) as risk_mentions,
        sum(case when ct.tracker_category = 'Buying Signal' then ct.mention_count else 0 end) as buying_signal_mentions,
        sum(case when ct.tracker_category = 'Objection' then ct.mention_count else 0 end) as objection_mentions,
        sum(case when ct.tracker_category = 'Security' then ct.mention_count else 0 end) as security_mentions,
        sum(case when ct.tracker_category = 'Technical' then ct.mention_count else 0 end) as technical_mentions
    from "data"."staging"."stg_calls" c
    inner join "data"."staging"."stg_call_trackers" ct on c.call_id = ct.call_id
    group by c.opp_id
),

-- Multi-threading: contact roles per opportunity
opp_stakeholders as (
    select
        opp_id,
        count(*) as stakeholder_count,
        count(case when role = 'Champion' then 1 end) as champion_count,
        count(case when role = 'Economic Buyer' then 1 end) as economic_buyer_count,
        count(case when role = 'Technical Evaluator' then 1 end) as technical_evaluator_count,
        count(case when role = 'Executive Sponsor' then 1 end) as executive_sponsor_count,
        count(case when role = 'Blocker' then 1 end) as blocker_count,
        count(case when is_primary then 1 end) as primary_contact_count
    from "data"."staging"."stg_contact_roles"
    group by opp_id
),

-- Lead source attribution (first lead that converted to this opp)
lead_attribution as (
    select
        converted_opp_id as opp_id,
        min(lead_id) as attributed_lead_id,
        min(source) as attributed_lead_source
    from "data"."staging"."stg_leads"
    where converted_opp_id is not null
    group by converted_opp_id
)

select
    o.opp_id,
    o.name as opp_name,
    o.stage,
    o.amount,
    o.close_date,
    o.created_date,
    o.lead_source,
    o.forecast_category,
    o.is_won,
    o.is_closed,
    o.competitor,
    o.loss_reason,
    o.days_in_stage,
    o.next_step,
    o.opportunity_type,

    -- Account info
    o.account_id,
    a.name as account_name,
    a.industry,
    a.employee_count,
    a.arr as account_arr,
    a.region,
    case
        when a.employee_count <= 200 then 'SMB'
        when a.employee_count <= 2000 then 'Mid-Market'
        else 'Enterprise'
    end as account_segment,

    -- Rep info
    o.owner_id,

    -- Call engagement stats
    coalesce(cs.total_calls, 0) as total_calls,
    coalesce(cs.completed_calls, 0) as completed_calls,
    coalesce(cs.total_call_minutes, 0) as total_call_minutes,
    cs.avg_talk_ratio,
    cs.avg_questions_per_call,
    coalesce(cs.calls_with_next_steps, 0) as calls_with_next_steps,
    cs.first_call_date,
    cs.last_call_date,

    -- Call intelligence
    coalesce(ti.competitor_mentions, 0) as competitor_mentions,
    coalesce(ti.pricing_mentions, 0) as pricing_mentions,
    coalesce(ti.risk_mentions, 0) as risk_mentions,
    coalesce(ti.buying_signal_mentions, 0) as buying_signal_mentions,
    coalesce(ti.objection_mentions, 0) as objection_mentions,
    coalesce(ti.security_mentions, 0) as security_mentions,
    coalesce(ti.technical_mentions, 0) as technical_mentions,

    -- Multi-threading
    coalesce(os.stakeholder_count, 0) as stakeholder_count,
    coalesce(os.champion_count, 0) as champion_count,
    coalesce(os.economic_buyer_count, 0) as economic_buyer_count,
    coalesce(os.technical_evaluator_count, 0) as technical_evaluator_count,
    coalesce(os.executive_sponsor_count, 0) as executive_sponsor_count,
    coalesce(os.blocker_count, 0) as blocker_count,
    coalesce(os.primary_contact_count, 0) as primary_contact_count,

    -- Lead attribution
    la.attributed_lead_id,
    la.attributed_lead_source,

    -- Calculated fields
    case
        when o.is_closed then datediff('day', o.created_date::date, o.close_date::date)
        else datediff('day', o.created_date::date, current_date)
    end as cycle_days,

    o.created_at

from opportunities o
left join accounts a on o.account_id = a.account_id
left join opp_call_stats cs on o.opp_id = cs.opp_id
left join opp_tracker_intelligence ti on o.opp_id = ti.opp_id
left join opp_stakeholders os on o.opp_id = os.opp_id
left join lead_attribution la on o.opp_id = la.opp_id
    );
  
  