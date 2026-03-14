-- Sales rep dimension derived from opportunity owners
-- Aggregates performance metrics per rep
with rep_names as (
    -- Map owner_id to rep names (mirrors the generator's REP_NAMES list)
    select 1 as owner_id, 'Sarah Chen' as rep_name union all
    select 2, 'Marcus Johnson' union all
    select 3, 'Emily Rodriguez' union all
    select 4, 'James Wilson' union all
    select 5, 'Priya Patel' union all
    select 6, 'David Kim' union all
    select 7, 'Rachel Martinez' union all
    select 8, 'Alex Thompson' union all
    select 9, 'Jordan Lee' union all
    select 10, 'Taylor Anderson' union all
    select 11, 'Casey Williams' union all
    select 12, 'Morgan Brown' union all
    select 13, 'Sam Davis' union all
    select 14, 'Jamie Garcia' union all
    select 15, 'Riley Taylor' union all
    select 16, 'Drew Miller'
),

opp_metrics as (
    select
        owner_id,
        count(*) as total_opportunities,
        count(case when is_closed = false then 1 end) as open_opportunities,
        count(case when is_won = true then 1 end) as won_deals,
        count(case when stage = 'Closed Lost' then 1 end) as lost_deals,
        sum(case when is_closed = false then amount else 0 end) as open_pipeline,
        sum(case when is_won = true then amount else 0 end) as closed_won_revenue,
        sum(case when forecast_category = 'Commit' then amount else 0 end) as commit_amount,
        sum(case when forecast_category = 'Best Case' then amount else 0 end) as best_case_amount,
        avg(case when is_won = true then amount end) as avg_deal_size,
        -- Win rate
        case
            when count(case when is_closed = true then 1 end) > 0
            then round(
                count(case when is_won = true then 1 end)::decimal
                / count(case when is_closed = true then 1 end), 3
            )
            else 0
        end as win_rate,
        count(distinct account_id) as accounts_worked
    from "data"."staging"."stg_opportunities"
    group by owner_id
),

call_metrics as (
    select
        owner_id,
        count(*) as total_calls,
        count(case when disposition = 'Completed' then 1 end) as completed_calls,
        avg(case when disposition = 'Completed' then duration_minutes end) as avg_call_duration,
        avg(case when disposition = 'Completed' then talk_ratio_rep end) as avg_talk_ratio,
        avg(case when disposition = 'Completed' then question_count end) as avg_questions_per_call
    from "data"."staging"."stg_calls"
    group by owner_id
)

select
    r.owner_id,
    r.rep_name,

    -- Pipeline metrics
    coalesce(o.total_opportunities, 0) as total_opportunities,
    coalesce(o.open_opportunities, 0) as open_opportunities,
    coalesce(o.won_deals, 0) as won_deals,
    coalesce(o.lost_deals, 0) as lost_deals,
    coalesce(o.open_pipeline, 0) as open_pipeline,
    coalesce(o.closed_won_revenue, 0) as closed_won_revenue,
    coalesce(o.commit_amount, 0) as commit_amount,
    coalesce(o.best_case_amount, 0) as best_case_amount,
    o.avg_deal_size,
    coalesce(o.win_rate, 0) as win_rate,
    coalesce(o.accounts_worked, 0) as accounts_worked,

    -- Call activity metrics
    coalesce(c.total_calls, 0) as total_calls,
    coalesce(c.completed_calls, 0) as completed_calls,
    c.avg_call_duration,
    c.avg_talk_ratio,
    c.avg_questions_per_call

from rep_names r
left join opp_metrics o on r.owner_id = o.owner_id
left join call_metrics c on r.owner_id = c.owner_id