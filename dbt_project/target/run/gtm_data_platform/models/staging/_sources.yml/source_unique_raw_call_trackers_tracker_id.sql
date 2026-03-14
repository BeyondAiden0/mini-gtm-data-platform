
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    tracker_id as unique_field,
    count(*) as n_records

from "data"."raw"."call_trackers"
where tracker_id is not null
group by tracker_id
having count(*) > 1



  
  
      
    ) dbt_internal_test