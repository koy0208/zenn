-- 値の照合（reconciliation）テスト。
--
-- 形のテスト（行数・主キー・NULL）は「重複を消す」修正で全部満たせてしまう。
-- このテストは出力の《値》を、モデルの計算経路を通らずにソースから独立に組み直して
-- 突き合わせる。行数と主キーが正しくても、値が別の行から拾われていればここで落ちる。
--
-- 仕様（marts.yml の description）:
--   supply_cost = その SKU を作るのに必要な副資材コストの合計
with

expected as (

    select
        product_id,
        sum(supply_cost) as supply_cost

    from {{ ref('stg_supplies') }}
    group by product_id

),

actual as (

    -- 同じ SKU なら supply_cost は必ず同じ値でなければならないので、
    -- min と max の両方を突き合わせる（SKU 内でブレていても落ちる）
    select
        product_id,
        min(supply_cost) as min_cost,
        max(supply_cost) as max_cost

    from {{ ref('fct_order_items') }}
    where product_id is not null
    group by product_id

)

select
    actual.product_id,
    actual.min_cost,
    actual.max_cost,
    expected.supply_cost as expected_cost

from actual
join expected
    on actual.product_id = expected.product_id

where abs(actual.min_cost - expected.supply_cost) > 0.001
   or abs(actual.max_cost - expected.supply_cost) > 0.001
