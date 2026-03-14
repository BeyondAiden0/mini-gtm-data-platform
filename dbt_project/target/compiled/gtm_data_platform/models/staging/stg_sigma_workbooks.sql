with source as (
    select * from "data"."raw"."sigma_workbooks"
),

cleaned as (
    select
        workbook_id,
        name,
        category,
        type
    from source
    where workbook_id is not null
)

select * from cleaned