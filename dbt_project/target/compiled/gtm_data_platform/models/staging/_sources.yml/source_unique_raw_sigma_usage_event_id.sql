
    
    

select
    event_id as unique_field,
    count(*) as n_records

from "data"."raw"."sigma_usage"
where event_id is not null
group by event_id
having count(*) > 1


