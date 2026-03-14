
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    stage_history_id as unique_field,
    count(*) as n_records

from "data"."raw"."stage_history"
where stage_history_id is not null
group by stage_history_id
having count(*) > 1



  
  
      
    ) dbt_internal_test