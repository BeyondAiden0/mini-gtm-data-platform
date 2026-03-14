
    
    

select
    channel_id as unique_field,
    count(*) as n_records

from "data"."raw"."slack_channels"
where channel_id is not null
group by channel_id
having count(*) > 1


