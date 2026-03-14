
    
    

with child as (
    select call_id as from_field
    from "data"."raw"."call_trackers"
    where call_id is not null
),

parent as (
    select call_id as to_field
    from "data"."raw"."calls"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


