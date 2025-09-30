import duckdb
import logging
import os

#connect to DuckDB
db_path = os.path.join(os.getcwd(), "emissions.duckdb")
con = duckdb.connect(database=db_path, read_only=False)

#logger setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='clean.log'
)
logger = logging.getLogger(__name__)


#function to clean tables
def clean_table(table_name, pickup_col, dropoff_col):
    """Clean DuckDB tables"""
    logger.info(f"Starting cleaning for {table_name}")
    print(f"Cleaning table: {table_name}")

    #remove duplicates
    con.execute(f"""
        SELECT DISTINCT * FROM {table_name};
                                """)
    logger.info(f"Removed duplicates from {table_name}")

    #remove trips with 0 passengers (assuming passenger_count column exists)
    con.execute(f"""
        DELETE FROM {table_name}
        WHERE passenger_count = 0
    """)
    logger.info(f"Removed trips with 0 passengers from {table_name}")
    print("Removed trips with 0 passengers")

    #remove trips with 0 miles
    con.execute(f"""
        DELETE FROM {table_name}
        WHERE trip_distance = 0
    """)
    logger.info(f"Removed trips with 0 miles from {table_name}")
    print("Removed trips with 0 miles")

    #remove trips longer than 100 miles
    con.execute(f"""
        DELETE FROM {table_name}
        WHERE trip_distance > 100
    """)
    logger.info(f"Removed trips longer than 100 miles from {table_name}")
    print("Removed trips longer than 100 miles")

    #remove trips longer than 24 hours, date_diff means difference between two dates in specified unit (here, seconds)
    con.execute(f"""
        DELETE FROM {table_name}
        WHERE date_diff('second', {pickup_col}, {dropoff_col}) > 86400
    """)
    logger.info(f"Removed trips longer than 24 hours from {table_name}")
    print("Removed trips longer than 24 hours")

    #count rows after cleaning
    remaining_rows = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchall()
    print(remaining_rows)
    logger.info(f"Remaining rows in {table_name} after cleaning: {remaining_rows}") 
    print(f"Remaining rows in {table_name} after cleaning: {remaining_rows}")


#clean yellow table
clean_table("yellow", "pickup_datetime", "dropoff_datetime")

#clean green table
clean_table("green", "pickup_datetime", "dropoff_datetime")

#close connection
con.close()
logger.info("Database connection closed")
print("Done.")


