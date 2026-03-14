with source as (
    select * from {{ source('raw', 'product_events') }}
),

cleaned as (
    select
        event_id,
        product_user_id,
        account_id,
        feature,
        action,
        event_timestamp
    from source
    where event_id is not null
        and product_user_id is not null
        and event_timestamp <= current_timestamp
)

select * from cleaned
