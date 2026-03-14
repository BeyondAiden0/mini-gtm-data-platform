
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select contact_id
from "data"."raw"."contacts"
where contact_id is null



  
  
      
    ) dbt_internal_test