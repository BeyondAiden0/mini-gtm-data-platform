
    
    

with child as (
    select channel_id as from_field
    from "data"."raw"."slack_messages"
    where channel_id is not null
),

parent as (
    select channel_id as to_field
    from "data"."raw"."slack_channels"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


