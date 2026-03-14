
  
  create view "data"."staging"."stg_lead_activities__dbt_tmp" as (
    with source as (
    select * from "data"."raw"."lead_activities"
),

cleaned as (
    select
        activity_id,
        lead_id,
        campaign_id,
        activity_type,
        activity_date,
        utm_source
    from source
    where activity_id is not null
        and lead_id is not null
        -- Filter out future timestamps
        and activity_date <= current_timestamp
)

select * from cleaned
  );
