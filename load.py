import duckdb
import logging
import os
db_path = os.path.join(os.getcwd(), "emissions.duckdb")
con = duckdb.connect(database=db_path, read_only=False)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='load.log'
)
logger = logging.getLogger(__name__)

base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"
year = 2024
urls = []
yellow_urls = [f"{base_url}/yellow_tripdata_2024-{m:02d}.parquet" for m in range(1, 13)]


def load_parquet_files():

    con = None
    try:
        # Connect to DuckDB
        con = duckdb.connect(database="emissions.duckdb", read_only=False)
        logger.info("Connected to DuckDB instance")

        # Drop if exists to avoid conflicts
        con.execute("DROP TABLE IF EXISTS yellow")

        # Loop over all URLs and append to table
        first = True
        for url in yellow_urls:
            if first:
                con.execute(f"""
                    CREATE TABLE yellow AS
                    SELECT passenger_count, trip_distance, tpep_pickup_datetime, tpep_dropoff_datetime
                    FROM read_parquet('{url}')
                """)
                first = False
            else:
                con.execute(f"""
                    INSERT INTO yellow
                    SELECT passenger_count, trip_distance, tpep_pickup_datetime, tpep_dropoff_datetime
                    FROM read_parquet('{url}')
                """)
        logger.info("Finished loading all parquet files")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")

    finally:
        if con:
            con.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    load_parquet_files()


try:
    count = con.execute("SELECT COUNT(*) FROM yellow").fetchone()[0]
    print(f"Table 'yellow': {count} rows")
except duckdb.CatalogException:
    print("Table 'yellow' does not exist in the database.")

# Close connection
con.close()