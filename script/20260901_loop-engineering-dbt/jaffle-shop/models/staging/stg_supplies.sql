with

source as (

    select * from {{ source('ecom', 'raw_supplies') }}

),

renamed as (

    select
        -- supply の id は SKU 間で使い回されるため、単体では一意にならない
        md5(id || '-' || sku) as supply_id,
        sku as product_id,
        name as supply_name,
        {{ cents_to_dollars('cost') }} as supply_cost,
        perishable as is_perishable_supply

    from source

)

select * from renamed
