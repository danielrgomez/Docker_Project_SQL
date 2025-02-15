# TLC Trip Record Data Extraction Project

## Project Description
This project extracts and processes data from the [TLC Trip Record Data website](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). The dataset includes yellow and green taxi trip records, capturing information such as:

- Pick-up and drop-off dates/times
- Pick-up and drop-off locations
- Trip distances
- Itemized fares
- Rate types
- Payment types
- Driver-reported passenger counts

The data is collected and provided to the NYC Taxi and Limousine Commission (TLC) by authorized technology providers. Note that the TLC does not create the data and makes no representations regarding its accuracy.

## Docker Configuration
The extraction process is configured using a Docker Compose file (`docker-compose.yml`) to set up the following services:

### Postgres
- Image: `postgres:13`
- Environment variables:
  - `POSTGRES_USER=root`
  - `POSTGRES_PASSWORD=root`
  - `POSTGRES_DB=ny_taxi`
- Ports: `5432:5432`

### PgAdmin
- Username: `admin@admin.com`
- Password: `root`
- Ports: `8080:80`

The Docker Compose file is built using the Windows Subsystem for Linux terminal.

## Data Ingestion
The `ingest_data.py` script ingests data into the PostgreSQL database using the following Python libraries:
- Pandas
- SQLAlchemy
- PyArrow
- Argparse

### Parameters
The script parses the following parameters:
- User: `root`
- Password: `root`
- Host: `pg-database`
- Port: `5432`
- Database: `ny_taxi`
- Table name: `yellow_taxi_trips`
- URL: `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet`

### Process
1. Creates the SQLAlchemy engine: `postgresql://root:root@pg-database:5432/ny_taxi`
2. Reads the Parquet file into a Pandas DataFrame using the PyArrow engine
3. Defines the schema and names it `yellow_taxi_data`
4. Transforms date fields (`tpep_pickup_datetime` and `tpep_dropoff_datetime`) to datetimestamps using the `to_datetime()` function
5. Creates the table in PostgreSQL, replacing any existing table with the same name
6. Defines a `create_batches` function to loop through the DataFrame and create batches of 100,000 rows
7. Uses a for loop to append each batch to PostgreSQL using `to_sql()` with `if_exists='append'`

The database is populated with all extracted data for January 2021 from the TLC Trip Record Data.

## Power BI Dashboard
While Docker runs PostgreSQL in the background, Power BI is used to create a dashboard connecting to the PostgreSQL database. The dashboard includes the following graphs:

1. Total Amount paid in fares by Borough in New York
2. Total Amount paid in fares by Service Zone
3. Total Amount paid in fares by day of the week
4. Total Amount paid in fares by hour of the day

These graphs provide insights into the optimal locations, days, and times for yellow taxis to maximize earnings in January 2021.

## Conclusion
This project demonstrates how to extract, transform, and visualize TLC Trip Record Data using Docker, PostgreSQL, Python, and Power BI. The resulting dashboard provides valuable insights into taxi fare patterns in New York City.

