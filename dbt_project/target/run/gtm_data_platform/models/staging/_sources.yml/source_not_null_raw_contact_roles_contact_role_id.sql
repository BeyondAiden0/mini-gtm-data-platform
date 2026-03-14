
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select contact_role_id
from "data"."raw"."contact_roles"
where contact_role_id is null



  
  
      
    ) dbt_internal_test