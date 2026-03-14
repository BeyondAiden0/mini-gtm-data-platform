
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select call_id
from "data"."raw"."calls"
where call_id is null



  
  
      
    ) dbt_internal_test