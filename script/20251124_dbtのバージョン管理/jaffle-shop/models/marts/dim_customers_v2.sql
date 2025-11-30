with src as (
select 
    customer_id,
    customer_name,
    floor(random() * 60) + 20 as age
from {{ ref('stg_customers') }}
)
select 
    customer_id,
    -- customer_name,
    age,
    case
        when age < 30 then 'young'
        when age between 30 and 50 then 'middle'
        else 'senior'
    end as age_group
from src