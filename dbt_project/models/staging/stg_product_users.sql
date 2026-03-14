with source as (
    select * from {{ source('raw', 'product_users') }}
),

cleaned as (
    select
        product_user_id,
        account_id,
        case
            when email like '%@%' then email
            else null
        end as email,
        role,
        plan_tier,
        signup_date,
        last_active_date,
        is_active
    from source
    where product_user_id is not null
        and account_id is not null
    qualify row_number() over (partition by product_user_id order by signup_date desc) = 1
)

select * from cleaned
