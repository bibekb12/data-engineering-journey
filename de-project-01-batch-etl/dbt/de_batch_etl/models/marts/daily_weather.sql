{{
    config(
        materialized='table'
    )
}}

select
    date(timestamp) as weather_date,
    latitude,
    longitude,
    round(avg(temperature_c)::numeric, 2) as avg_temperature_c,
    round(min(temperature_c)::numeric, 2) as min_temperature_c,
    round(max(temperature_c)::numeric, 2) as max_temperature_c,
    count(*) as observation_count
from {{ ref('stg_weather') }}
group by
    date(timestamp),
    latitude,
    longitude
order by
    weather_date
