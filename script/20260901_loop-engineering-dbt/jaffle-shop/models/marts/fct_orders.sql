with

orders as (

    select * from {{ ref('stg_orders') }}

),

locations as (

    select * from {{ ref('stg_stores') }}

),

order_items as (

    select * from {{ ref('fct_order_items') }}

),

order_item_summary as (

    select
        order_id,
        count(*) as count_order_items,
        sum(supply_cost) as order_cost

    from order_items
    group by order_id

),

joined as (

    select
        orders.order_id,
        orders.customer_id,
        orders.location_id,
        locations.location_name,
        orders.ordered_at,
        orders.subtotal,
        orders.tax_paid,
        orders.order_total,
        order_item_summary.count_order_items,
        order_item_summary.order_cost

    from orders

    left join locations
        on orders.location_id = locations.location_id

    left join order_item_summary
        on orders.order_id = order_item_summary.order_id

)

select * from joined
