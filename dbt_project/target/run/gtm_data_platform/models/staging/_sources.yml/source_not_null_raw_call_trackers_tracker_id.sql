
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select tracker_id
from "data"."raw"."call_trackers"
where tracker_id is null



  
  
      
    ) dbt_internal_test