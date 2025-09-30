import duckdb
import logging
import os
import time

# set up global duckdb connection
db_path = os.path.join(os.getcwd(), "emissions.duckdb") #path to local duckdb database
con = duckdb.connect(database=db_path, read_only=False) #open db and allow writing

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='load.log' #save logs to file
)
logger = logging.getLogger(__name__) #create logger object

# Years and URLs for 2015–2024 trip data
years = list(range(2015, 2025))
base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"
#create list of URLS for yellow and green trips for all months from 2015 to 2024
yellow_urls = [f"{base_url}/yellow_tripdata_{year}-{month:02d}.parquet" for year in years for month in range(1, 13)]
green_urls = [f"{base_url}/green_tripdata_{year}-{month:02d}.parquet" for year in years for month in range(1, 13)]

#function to load parquet files into duckdb
def load_parquet_files():
    global con
    try:
        logger.info("Starting data load...") #log start of data load

        #drop tables if they exist
        con.execute("DROP TABLE IF EXISTS yellow")
        con.execute("DROP TABLE IF EXISTS green")
        con.execute("DROP TABLE IF EXISTS vehicle_emissions")
        logger.info("Dropped existing tables if they existed")

        #load yellow trips
        first = True
        for url in yellow_urls:
            try:
                if first:
                #create table if first file
                    con.execute(f"""
                        CREATE TABLE yellow AS
                        SELECT
                            passenger_count,
                            trip_distance,
                            tpep_pickup_datetime AS pickup_datetime,
                            tpep_dropoff_datetime AS dropoff_datetime
                        FROM read_parquet('{url}')
                    """)
                    first = False #set first to false after creating table
                else:
                    #append to table if not first file
                    con.execute(f"""
                        INSERT INTO yellow
                        SELECT
                            passenger_count,
                            trip_distance,
                            tpep_pickup_datetime AS pickup_datetime,
                            tpep_dropoff_datetime AS dropoff_datetime
                        FROM read_parquet('{url}')
                    """)
                logger.info(f"Loaded {url}") #log successful load
                time.sleep(30)  # pause to avoid overwhelming server
            except Exception as e:
                logger.error(f"Failed to load {url}: {e}") #log any errors

        logger.info("Finished loading all yellow trip files") #log completion of yellow trip loading

        #Load green trips
        first = True 
        for url in green_urls:
            try:
                if first:
                #create table if first file
                    con.execute(f"""
                        CREATE TABLE green AS
                        SELECT
                            passenger_count,
                            trip_distance,
                            lpep_pickup_datetime AS pickup_datetime,
                            lpep_dropoff_datetime AS dropoff_datetime
                        FROM read_parquet('{url}')
                    """)
                    first = False
                else:
                    #append to table if not first file
                    con.execute(f"""
                        INSERT INTO green
                        SELECT
                            passenger_count,
                            trip_distance,
                            lpep_pickup_datetime AS pickup_datetime,
                            lpep_dropoff_datetime AS dropoff_datetime
                        FROM read_parquet('{url}')
                    """)
                logger.info(f"Loaded {url}") #log successful load
                time.sleep(30) # pause to avoid overwhelming server
            except Exception as e:
                logger.error(f"Failed to load {url}: {e}") #log any errors

        logger.info("Finished loading all green trip files") #log completion of green trip loading

        #load vehicle emissions CSV
        csv_file = os.path.join(os.getcwd(), "data", "vehicle_emissions.csv") #path to local csv file
        if os.path.exists(csv_file):
            con.execute(f"""
                CREATE TABLE vehicle_emissions AS
                SELECT
                    vehicle_type,
                    co2_grams_per_mile
                FROM read_csv_auto('{csv_file}')
            """)
            logger.info("Imported vehicle_emissions CSV") #log successful import
        else:
            logger.warning(f"{csv_file} not found, skipping vehicle_emissions table creation") #log if csv not found

        logger.info("Data load complete!") #log completion of data load

    except Exception as e:
        print(f"An error occurred: {e}") #print any errors
        logger.error(f"An error occurred: {e}") #log any errors

#function to summarize tables
def summarize_table(table_name):
    query = f"""
        SELECT
            COUNT(*) AS row_count,
            AVG(passenger_count) AS avg_passenger_count,
            AVG(trip_distance) AS avg_trip_distance,
            MIN(pickup_datetime) AS min_pickup_datetime,
            MAX(dropoff_datetime) AS max_dropoff_datetime
        FROM {table_name}
    """
    return con.execute(query).fetchdf() #return results as dataframe

#main execution
if __name__ == "__main__":
    load_parquet_files() #call function to load data

        #check table row counts
    for table in ["yellow", "green", "vehicle_emissions"]:
        try:
            count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"Table '{table}': {count} rows") #print row count
        except duckdb.CatalogException:
            print(f"Table '{table}' does not exist in the database.") #handle case where table doesn't exist

    #generate summaries
    summary_yellow = summarize_table("yellow")
    summary_green = summarize_table("green")

    #print summaries
    print("\nYellow table summary:")
    print(summary_yellow.to_string(index=False))
    print("\nGreen table summary:")
    print(summary_green.to_string(index=False))

    #log summaries
    logger.info("Yellow table summary:\n%s", summary_yellow.to_string(index=False))
    logger.info("Green table summary:\n%s", summary_green.to_string(index=False))

    #close connection
    con.close()
    logger.info("Database connection closed")
    print("\nDone.")
