
    
    

with child as (
    select workbook_id as from_field
    from "data"."raw"."sigma_usage"
    where workbook_id is not null
),

parent as (
    select workbook_id as to_field
    from "data"."raw"."sigma_workbooks"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


