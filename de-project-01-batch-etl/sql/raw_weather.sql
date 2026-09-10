create schema if not exists raw;

create table if not exists raw.weather(
    timestamp TIMESTAMP not null,
    temperature_c DOUBLE precision,
    latitude DOUBLE precision not null,
    longitude DOUBLE precision not null,
    loaded_at TIMESTAMP not null DEFAULT current_timestamp
);

