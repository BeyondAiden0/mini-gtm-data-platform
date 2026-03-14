with source as (
    select * from "data"."raw"."campaigns"
),

cleaned as (
    select
        campaign_id,
        name,
        channel,
        type,
        status,
        -- Fix negative costs
        case
            when cost < 0 then abs(cost)
            else cost
        end as cost,
        start_date,
        end_date,
        created_at
    from source
    where campaign_id is not null
)

select * from cleaned