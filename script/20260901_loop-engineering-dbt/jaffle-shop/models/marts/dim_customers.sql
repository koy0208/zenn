with

customers as (

    select * from {{ ref('stg_customers') }}

),

orders as (

    select * from {{ ref('fct_orders') }}

),

customer_orders as (

    select
        customer_id,
        count(*) as count_lifetime_orders,
        sum(order_total) as lifetime_spend,
        min(ordered_at) as first_ordered_at,
        max(ordered_at) as last_ordered_at

    from orders
    group by customer_id

),

joined as (

    select
        customers.customer_id,
        customers.customer_name,
        -- 注文実績のない顧客も 1 行として残すため、集計値は 0 で埋める
        coalesce(customer_orders.count_lifetime_orders, 0) as count_lifetime_orders,
        coalesce(customer_orders.lifetime_spend, 0) as lifetime_spend,
        customer_orders.first_ordered_at,
        customer_orders.last_ordered_at

    from customers

    left join customer_orders
        on customers.customer_id = customer_orders.customer_id

)

select * from joined
