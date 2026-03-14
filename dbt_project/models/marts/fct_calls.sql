-- Call facts joined with opportunity and account context
-- Includes tracker topic summaries for deal intelligence
with calls as (
    select * from {{ ref('stg_calls') }}
),

opportunities as (
    select * from {{ ref('stg_opportunities') }}
),

accounts as (
    select * from {{ ref('stg_accounts') }}
),

-- Aggregate trackers per call into topic counts
call_tracker_summary as (
    select
        call_id,
        count(distinct tracker_name) as unique_topics,
        count(distinct tracker_category) as unique_categories,
        sum(mention_count) as total_mentions,
        sum(case when tracker_category = 'Competitor' then mention_count else 0 end) as competitor_mentions,
        sum(case when tracker_category in ('Pricing', 'Discount', 'Budget') then mention_count else 0 end) as pricing_mentions,
        sum(case when tracker_category = 'Risk' then mention_count else 0 end) as risk_mentions,
        sum(case when tracker_category = 'Security' then mention_count else 0 end) as security_mentions,
        sum(case when tracker_category = 'Buying Signal' then mention_count else 0 end) as buying_signal_mentions,
        sum(case when tracker_category = 'Objection' then mention_count else 0 end) as objection_mentions,
        sum(case when tracker_category = 'Technical' then mention_count else 0 end) as technical_mentions
    from {{ ref('stg_call_trackers') }}
    group by call_id
)

select
    c.call_id,
    c.call_date,
    c.duration_minutes,
    c.direction,
    c.call_type,
    c.disposition,
    c.num_participants,
    c.talk_ratio_rep,
    c.longest_monologue_sec,
    c.question_count,
    c.next_steps_mentioned,

    -- Opportunity context
    c.opp_id,
    o.name as opp_name,
    o.stage as opp_stage,
    o.amount as opp_amount,
    o.forecast_category,

    -- Account context
    o.account_id,
    a.name as account_name,
    a.industry,
    a.region,

    -- Rep
    c.owner_id,

    -- Tracker intelligence
    coalesce(t.unique_topics, 0) as unique_topics,
    coalesce(t.unique_categories, 0) as unique_categories,
    coalesce(t.total_mentions, 0) as total_mentions,
    coalesce(t.competitor_mentions, 0) as competitor_mentions,
    coalesce(t.pricing_mentions, 0) as pricing_mentions,
    coalesce(t.risk_mentions, 0) as risk_mentions,
    coalesce(t.security_mentions, 0) as security_mentions,
    coalesce(t.buying_signal_mentions, 0) as buying_signal_mentions,
    coalesce(t.objection_mentions, 0) as objection_mentions,
    coalesce(t.technical_mentions, 0) as technical_mentions

from calls c
left join opportunities o on c.opp_id = o.opp_id
left join accounts a on o.account_id = a.account_id
left join call_tracker_summary t on c.call_id = t.call_id

