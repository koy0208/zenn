-- fct_order_items は stg_order_items と 1:1 でなければならない。
-- join のファンアウトで行が増えても、DISTINCT で行を捨てても、このテストは落ちる。
with

staged as (
    select count(*) as n from {{ ref('stg_order_items') }}
),

fact as (
    select count(*) as n from {{ ref('fct_order_items') }}
)

select
    staged.n as staged_rows,
    fact.n as fact_rows
from staged
cross join fact
where staged.n != fact.n
