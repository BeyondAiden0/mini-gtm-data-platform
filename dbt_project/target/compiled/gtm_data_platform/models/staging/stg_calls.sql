with source as (
    select * from "data"."raw"."calls"
),

cleaned as (
    select
        call_id,
        opp_id,
        owner_id,
        call_date,
        -- Fix negative durations
        case
            when duration_minutes < 0 then abs(duration_minutes)
            else duration_minutes
        end as duration_minutes,
        direction,
        call_type,
        disposition,
        num_participants,
        -- Cap talk ratio at 1.0
        case
            when talk_ratio_rep > 1.0 then 1.0
            when talk_ratio_rep < 0 then 0
            else talk_ratio_rep
        end as talk_ratio_rep,
        -- Fix negative monologue durations
        case
            when longest_monologue_sec < 0 then abs(longest_monologue_sec)
            else longest_monologue_sec
        end as longest_monologue_sec,
        question_count,
        next_steps_mentioned
    from source
    where call_id is not null
        -- Filter out future timestamps
        and call_date <= current_timestamp
)

select * from cleaned