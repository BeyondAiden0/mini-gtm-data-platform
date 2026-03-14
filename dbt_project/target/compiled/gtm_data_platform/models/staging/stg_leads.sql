with source as (
    select * from "data"."raw"."leads"
),

cleaned as (
    select
        lead_id,
        first_name,
        last_name,
        -- Only keep emails that contain @
        case
            when email like '%@%' then email
            else null
        end as email,
        company,
        source,
        status,
        -- Fix negative scores
        case
            when score < 0 then abs(score)
            else score
        end as score,
        converted_opp_id,
        converted_account_id,
        converted_date,
        created_at
    from source
    where lead_id is not null
)

select * from cleaned