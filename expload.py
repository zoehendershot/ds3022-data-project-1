import duckdb
con = duckdb.connect()
con.execute("""
    CREATE TABLE test AS
    SELECT passenger_count FROM read_parquet('https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet')
""")
print(con.execute("SELECT COUNT(*) FROM test").fetchall())

