with source as (
    select * from "data"."raw"."slack_channels"
),

cleaned as (
    select
        channel_id,
        channel_name,
        opp_id,
        account_id,
        num_members,
        is_archived,
        created_at
    from source
    where channel_id is not null
        and channel_name is not null
)

select * from cleaned