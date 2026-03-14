
    
    

select
    tracker_id as unique_field,
    count(*) as n_records

from "data"."raw"."call_trackers"
where tracker_id is not null
group by tracker_id
having count(*) > 1


