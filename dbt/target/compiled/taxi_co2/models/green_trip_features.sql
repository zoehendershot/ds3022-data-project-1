-- models/green_trip_features.sql

SELECT
    g.*,
    (g.trip_distance * ve.co2_grams_per_mile) / 1000 AS trip_co2_kgs,
    g.trip_distance / (EXTRACT(EPOCH FROM (g.dropoff_datetime - g.pickup_datetime)) / 3600.0) AS avg_mph,
    EXTRACT(HOUR FROM g.pickup_datetime) AS hour_of_day,
    EXTRACT(DOW FROM g.pickup_datetime) AS day_of_week,
    EXTRACT(WEEK FROM g.pickup_datetime) AS week_of_year,
    EXTRACT(MONTH FROM g.pickup_datetime) AS month_of_year
FROM "emissions"."main"."green" g
JOIN "emissions"."main"."vehicle_emissions" ve
    ON ve.vehicle_type = 'green_taxi'