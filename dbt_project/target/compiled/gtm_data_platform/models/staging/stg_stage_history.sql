with source as (
    select * from "data"."raw"."stage_history"
),

cleaned as (
    select
        stage_history_id,
        opp_id,
        stage,
        entered_at::timestamp as entered_at,
        exited_at::timestamp as exited_at,
        case
            when days_in_stage < 0 then 0
            else days_in_stage
        end as days_in_stage
    from source
    where stage_history_id is not null
        and opp_id is not null
        and stage is not null
)

select * from cleaned