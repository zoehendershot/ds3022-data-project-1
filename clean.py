import duckdb
import logging
import os
db_path = os.path.join(os.getcwd(), "emissions.duckdb")
con = duckdb.connect(database=db_path, read_only=False)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='clean.log'
)
logger = logging.getLogger(__name__)


def clean_table(table_name, pickup_col, dropoff_col):
    """Clean a DuckDB table according to rules and return summary of removed rows."""
    
    # 1. Remove 0 passengers
    con.execute(f"""
        DELETE FROM {table_name}
        WHERE passenger_count = 0
    """)
    
    # 2. Remove 0 miles
    con.execute(f"""
        DELETE FROM {table_name}
        WHERE trip_distance = 0
    """)
    
    # 3. Remove trips > 100 miles
    con.execute(f"""
        DELETE FROM {table_name}
        WHERE trip_distance > 100
    """)
    
    # 4. Remove trips > 24 hours
    con.execute(f"""
        DELETE FROM {table_name}
        WHERE EXTRACT(EPOCH FROM ({dropoff_col} - {pickup_col})) > 86400
    """)  # subtracting timestamps gives interval, converting to seconds

    # Verification queries
    checks = {
    "zero_passengers": f"SELECT COUNT(*) FROM {table_name} WHERE passenger_count = 0",
    "zero_distance": f"SELECT COUNT(*) FROM {table_name} WHERE trip_distance = 0",
    "over_100_miles": f"SELECT COUNT(*) FROM {table_name} WHERE trip_distance > 100",
    "over_24h": f"SELECT COUNT(*) FROM {table_name} WHERE EXTRACT(EPOCH FROM {dropoff_col} - {pickup_col}) > 86400"
}


    results = {}
    for k, q in checks.items():
        results[k] = con.execute(q).fetchone()[0]
    
    # Output to screen
    print(f"=== {table_name} Cleaning Verification ===")
    for k, v in results.items():
        print(f"{k}: {v}")
    
    # Output to log
    logger.info(f"=== {table_name} Cleaning Verification ===")
    for k, v in results.items():
        logger.info(f"{k}: {v}")
    
    return results

# --- Clean Yellow Table ---
clean_table("yellow", "tpep_pickup_datetime", "tpep_dropoff_datetime")

# --- Clean Green Table ---
#clean_table("green", "lpep_pickup_datetime", "lpep_dropoff_datetime")
