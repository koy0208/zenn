with

order_items as (

    select * from {{ ref('stg_order_items') }}

),

products as (

    select * from {{ ref('stg_products') }}

),

supplies as (

    select * from {{ ref('stg_supplies') }}

),

joined as (

    select
        order_items.order_item_id,
        order_items.order_id,
        order_items.product_id,
        products.product_name,
        products.product_type,
        products.product_price,
        supplies.supply_cost

    from order_items

    left join products
        on order_items.product_id = products.product_id

    left join supplies
        on products.product_id = supplies.product_id

)

select * from joined
