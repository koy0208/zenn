with

source as (

    select * from {{ source('ecom', 'raw_orders') }}

),

renamed as (

    select
        id as order_id,
        customer as customer_id,
        store_id as location_id,
        ordered_at,
        {{ cents_to_dollars('subtotal') }} as subtotal,
        {{ cents_to_dollars('tax_paid') }} as tax_paid,
        {{ cents_to_dollars('order_total') }} as order_total

    from source

)

select * from renamed
