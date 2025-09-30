import duckdb
import logging
import os

# Path to your existing database
db_path = os.path.join(os.getcwd(), "emissions.duckdb")
con = duckdb.connect(database=db_path, read_only=False)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='transform.log'
)
logger = logging.getLogger(__name__)    

def add_trip_features(table_name, pickup_col, dropoff_col):
    """
    Add derived columns to the given trip table.
    - vehicle_type: 'yellow' or 'green'
    - trip_co2_kgs: trip_distance * vehicle_emissions.co2_grams_per_mile / 1000
    - avg_mph: miles per hour
    - hour_of_day, day_of_week, week_of_year, month_of_year
    """

    # 1. Total CO2 (kg) using real-time lookup from vehicle_emissions
    con.execute(f"""
        ALTER TABLE {table_name}
        ADD COLUMN IF NOT EXISTS trip_co2_kgs DOUBLE;
    """)
    con.execute(f"""
        UPDATE {table_name} t
        SET trip_co2_kgs = (
            t.trip_distance *
            (SELECT v.co2_grams_per_mile
             FROM vehicle_emissions v
             WHERE v.vehicle_type = t.vehicle_type) / 1000.0
        );
    """)

    # 2. Average miles per hour
    con.execute(f"""
        ALTER TABLE {table_name}
        ADD COLUMN IF NOT EXISTS avg_mph DOUBLE;
    """)
    con.execute(f"""
        UPDATE {table_name}
        SET avg_mph = CASE
            WHEN EXTRACT(EPOCH FROM ({dropoff_col} - {pickup_col})) = 0
                THEN NULL
            ELSE trip_distance /
                 (EXTRACT(EPOCH FROM ({dropoff_col} - {pickup_col})) / 3600.0)
        END;
    """)

    # 3–6. Time-based columns
    con.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS hour_of_day   INTEGER;")
    con.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS day_of_week   INTEGER;")
    con.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS week_of_year  INTEGER;")
    con.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS month_of_year INTEGER;")

    con.execute(f"""
        UPDATE {table_name}
        SET hour_of_day   = EXTRACT(HOUR    FROM {pickup_col}),
            day_of_week   = EXTRACT(DOW     FROM {pickup_col}),  -- 0=Sunday
            week_of_year  = EXTRACT(WEEK    FROM {pickup_col}),
            month_of_year = EXTRACT(MONTH   FROM {pickup_col});
    """)

    print(f"Transformations complete for {table_name}")

# Apply to both cleaned tables
add_trip_features("yellow", "tpep_pickup_datetime", "tpep_dropoff_datetime")
#add_trip_features("green",  "lpep_pickup_datetime", "lpep_dropoff_datetime")

con.close()
