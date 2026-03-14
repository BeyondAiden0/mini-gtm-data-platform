
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    activity_id as unique_field,
    count(*) as n_records

from "data"."raw"."lead_activities"
where activity_id is not null
group by activity_id
having count(*) > 1



  
  
      
    ) dbt_internal_test