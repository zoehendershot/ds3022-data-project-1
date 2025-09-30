import duckdb
import matplotlib.pyplot as plt
import os
import logging

#logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='analysis.log',
    filemode='w'
)
logger = logging.getLogger(__name__)

#connect to duckdb database
db_path = os.path.join(os.getcwd(), "emissions.duckdb")
con = duckdb.connect(database=db_path, read_only=False)
logger.info("Connected to DuckDB database at %s", db_path)

#function to get largest CO2 producing trip for a given table
def largest_co2_trip(table_name):
    query = f"""
        SELECT pickup_datetime, dropoff_datetime, trip_co2_kgs
        FROM {table_name}
        ORDER BY trip_co2_kgs DESC
        LIMIT 1
    """
    result = con.execute(query).fetchone()
    logger.info("Largest CO2 trip for %s: %s", table_name, result)
    return result

#function to get average CO2 by a time unit
def avg_co2_by_unit(table_name, time_unit):
    query = f"""
        SELECT {time_unit}, AVG(trip_co2_kgs) AS avg_co2
        FROM {table_name}
        GROUP BY {time_unit}
        ORDER BY avg_co2 DESC
    """
    results = con.execute(query).fetchall()
    logger.info("Average CO2 by %s for %s calculated", time_unit, table_name)
    return results

#largest CO2 trips for both cab types 
for cab in ["yellow_trip_features", "green_trip_features"]:
    trip = largest_co2_trip(cab)
    print(f"Largest CO2 trip for {cab}: {trip}")

#most/least carbon-intensive units
time_units = ["hour_of_day", "day_of_week", "week_of_year", "month_of_year"]
for cab in ["yellow_trip_features", "green_trip_features"]:
    print(f"\n--- {cab.upper()} ---")
    for unit in time_units:
        results = avg_co2_by_unit(cab, unit)
        most = results[0]  # highest avg CO2
        least = results[-1]  # lowest avg CO2
        print(f"Most carbon-intensive {unit}: {most}")
        print(f"Least carbon-intensive {unit}: {least}")
        logger.info("%s - Most %s: %s", cab, unit, most)
        logger.info("%s - Least %s: %s", cab, unit, least)

#plot CO2 totals by month for both cab types
yellow_month = con.execute("""
    SELECT month_of_year, SUM(trip_co2_kgs) AS total_co2
    FROM yellow_trip_features
    GROUP BY month_of_year
    ORDER BY month_of_year
""").fetchdf()

green_month = con.execute("""
    SELECT month_of_year, SUM(trip_co2_kgs) AS total_co2
    FROM green_trip_features
    GROUP BY month_of_year
    ORDER BY month_of_year
""").fetchdf()

plt.figure(figsize=(10,6))
plt.plot(yellow_month['month_of_year'], yellow_month['total_co2'], marker='o', label='Yellow Taxi')
plt.plot(green_month['month_of_year'], green_month['total_co2'], marker='o', label='Green Taxi')
plt.xlabel('Month')
plt.ylabel('Total CO2 (kg)')
plt.title('Monthly CO2 Output by Taxi Type')
plt.xticks(range(1,13))
plt.legend()
plt.grid(True)
plt.tight_layout()

#save plot to file
plot_file = 'monthly_co2.png'
plt.savefig(plot_file)
logger.info("Monthly CO2 plot saved as %s", plot_file)
print(f"\nPlot saved as '{plot_file}'")

#close connection
con.close()
logger.info("Database connection closed")
