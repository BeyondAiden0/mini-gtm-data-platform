
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select product_user_id
from "data"."raw"."product_users"
where product_user_id is null



  
  
      
    ) dbt_internal_test