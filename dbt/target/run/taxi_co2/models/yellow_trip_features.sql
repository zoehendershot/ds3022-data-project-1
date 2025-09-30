
  
  create view "emissions"."main"."yellow_trip_features__dbt_tmp" as (
    -- models/yellow_trip_features.sql

SELECT
    y.*,
    (y.trip_distance * ve.co2_grams_per_mile) / 1000 AS trip_co2_kgs,
    y.trip_distance / (EXTRACT(EPOCH FROM (y.dropoff_datetime - y.pickup_datetime)) / 3600.0) AS avg_mph,
    EXTRACT(HOUR FROM y.pickup_datetime) AS hour_of_day,
    EXTRACT(DOW FROM y.pickup_datetime) AS day_of_week,
    EXTRACT(WEEK FROM y.pickup_datetime) AS week_of_year,
    EXTRACT(MONTH FROM y.pickup_datetime) AS month_of_year
FROM "emissions"."main"."yellow" y
JOIN "emissions"."main"."vehicle_emissions" ve
    ON ve.vehicle_type = 'yellow_taxi'
  );
