with source as (
    select * from "data"."raw"."sigma_usage"
),

cleaned as (
    select
        event_id,
        sigma_user_id,
        user_name,
        user_role,
        user_team,
        workbook_id,
        workbook_name,
        workbook_category,
        action,
        -- Fix negative durations
        case
            when duration_seconds < 0 then abs(duration_seconds)
            else duration_seconds
        end as duration_seconds,
        queries_run,
        event_time
    from source
    where event_id is not null
        -- Filter out future timestamps
        and event_time <= current_timestamp
)

select * from cleaned