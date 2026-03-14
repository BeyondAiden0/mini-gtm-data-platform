
  
  create view "data"."staging"."stg_opportunities__dbt_tmp" as (
    with source as (
    select * from "data"."raw"."opportunities"
),

cleaned as (
    select
        opp_id,
        account_id,
        owner_id,
        name,
        stage,
        case
            when amount < 0 then abs(amount)
            else amount
        end as amount,
        close_date,
        created_date,
        lead_source,
        forecast_category,
        is_won,
        is_closed,
        competitor,
        loss_reason,
        case
            when days_in_stage < 0 then 0
            when days_in_stage > 365 then 365
            else days_in_stage
        end as days_in_stage,
        next_step,
        opportunity_type,
        created_at
    from source
    where opp_id is not null
        and account_id is not null
        and close_date >= created_date
    qualify row_number() over (partition by opp_id order by created_at desc) = 1
)

select * from cleaned
  );
