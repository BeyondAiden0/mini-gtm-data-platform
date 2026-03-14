
    
    

select
    workbook_id as unique_field,
    count(*) as n_records

from "data"."raw"."sigma_workbooks"
where workbook_id is not null
group by workbook_id
having count(*) > 1


