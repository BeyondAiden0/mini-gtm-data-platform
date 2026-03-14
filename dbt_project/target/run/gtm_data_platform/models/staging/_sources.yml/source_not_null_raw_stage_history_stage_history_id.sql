
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select stage_history_id
from "data"."raw"."stage_history"
where stage_history_id is null



  
  
      
    ) dbt_internal_test