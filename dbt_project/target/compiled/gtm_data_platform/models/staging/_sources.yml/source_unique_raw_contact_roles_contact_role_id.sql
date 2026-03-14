
    
    

select
    contact_role_id as unique_field,
    count(*) as n_records

from "data"."raw"."contact_roles"
where contact_role_id is not null
group by contact_role_id
having count(*) > 1


