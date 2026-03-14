
  
  create view "data"."staging"."stg_slack_messages__dbt_tmp" as (
    with source as (
    select * from "data"."raw"."slack_messages"
),

cleaned as (
    select
        message_id,
        channel_id,
        sender,
        message_type,
        word_count,
        -- Fix negative response times
        case
            when response_time_minutes < 0 then abs(response_time_minutes)
            else response_time_minutes
        end as response_time_minutes,
        has_mention,
        has_emoji_reaction,
        sent_at
    from source
    where message_id is not null
        and channel_id is not null
        -- Filter out future timestamps
        and sent_at <= current_timestamp
)

select * from cleaned
  );
