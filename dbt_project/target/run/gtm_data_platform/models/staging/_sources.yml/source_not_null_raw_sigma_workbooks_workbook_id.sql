
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select workbook_id
from "data"."raw"."sigma_workbooks"
where workbook_id is null



  
  
      
    ) dbt_internal_test