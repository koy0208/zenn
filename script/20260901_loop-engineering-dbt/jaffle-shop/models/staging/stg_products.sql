with

source as (

    select * from {{ source('ecom', 'raw_products') }}

),

renamed as (

    select
        sku as product_id,
        name as product_name,
        type as product_type,
        {{ cents_to_dollars('product_price') }} as product_price,
        description as product_description

    from source

)

select * from renamed
