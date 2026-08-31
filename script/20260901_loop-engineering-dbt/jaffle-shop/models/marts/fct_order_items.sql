with

order_items as (

    select * from {{ ref('stg_order_items') }}

),

products as (

    select * from {{ ref('stg_products') }}

),

supply_cost_per_product as (

    -- 副資材は SKU ごとに複数行ある。join してから畳むのでは遅い（行が増えてしまう）。
    -- join する前に SKU 粒度へ畳んでおく。
    select
        product_id,
        sum(supply_cost) as supply_cost

    from {{ ref('stg_supplies') }}
    group by product_id

),

joined as (

    select
        order_items.order_item_id,
        order_items.order_id,
        order_items.product_id,
        products.product_name,
        products.product_type,
        products.product_price,
        supply_cost_per_product.supply_cost

    from order_items

    left join products
        on order_items.product_id = products.product_id

    left join supply_cost_per_product
        on products.product_id = supply_cost_per_product.product_id

)

select * from joined
