
  
  create view "data"."staging"."stg_accounts__dbt_tmp" as (
    with source as (
    select * from "data"."raw"."accounts"
),

cleaned as (
    select
        account_id,
        name,
        industry,
        -- Fix negative employee counts
        case
            when employee_count < 0 then abs(employee_count)
            else employee_count
        end as employee_count,
        -- Fix negative ARR
        case
            when arr < 0 then abs(arr)
            else arr
        end as arr,
        region,
        owner_id,
        created_at
    from source
    where account_id is not null
)

select * from cleaned
  );
