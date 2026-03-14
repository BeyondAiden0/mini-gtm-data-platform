with source as (
    select * from {{ source('raw', 'contacts') }}
),

cleaned as (
    select
        contact_id,
        account_id,
        first_name,
        last_name,
        -- Only keep emails that contain @
        case
            when email like '%@%' then email
            else null
        end as email,
        phone,
        title,
        role,
        created_at
    from source
    where contact_id is not null
        and account_id is not null
)

select * from cleaned

