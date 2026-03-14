with source as (
    select * from {{ source('raw', 'call_trackers') }}
),

cleaned as (
    select
        tracker_id,
        call_id,
        tracker_name,
        tracker_category,
        case
            when mention_count < 0 then abs(mention_count)
            else mention_count
        end as mention_count
    from source
    where tracker_id is not null
        and call_id is not null
        and tracker_name is not null
)

select * from cleaned

