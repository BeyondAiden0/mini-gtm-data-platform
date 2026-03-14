with source as (
    select * from {{ source('raw', 'contact_roles') }}
),

cleaned as (
    select
        contact_role_id,
        contact_id,
        opp_id,
        role,
        is_primary
    from source
    where contact_role_id is not null
        and contact_id is not null
        and opp_id is not null
    qualify row_number() over (partition by contact_id, opp_id order by contact_role_id) = 1
)

select * from cleaned
