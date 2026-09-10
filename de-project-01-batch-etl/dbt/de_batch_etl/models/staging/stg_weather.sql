{{
    config(
        materialized='view'
    )
}}

select 
    timestamp,
    temperature_c,
    latitude,
    longitude,
    loaded_at
from {{source('raw','weather')}}