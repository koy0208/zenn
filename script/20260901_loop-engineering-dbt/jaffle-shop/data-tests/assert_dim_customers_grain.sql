-- dim_customers は stg_customers と 1:1 でなければならない。
-- NULL を消すために inner join に変えると、このテストが落ちる。
with

staged as (
    select count(*) as n from {{ ref('stg_customers') }}
),

dim as (
    select count(*) as n from {{ ref('dim_customers') }}
)

select
    staged.n as staged_rows,
    dim.n as dim_rows
from staged
cross join dim
where staged.n != dim.n
