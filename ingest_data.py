#import os
import pandas as pd
#Open source SQL toolkit and object relational mapper for Python
from sqlalchemy import create_engine
from time import time
import argparse
import pyarrow.parquet as pq

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    # Get the name of the file from url
    file_name = url.rsplit('/', 1)[-1].strip()
    print(f'Getting file from {url}')
    print(f'Downloading {file_name} ...')
    

    #Creating the engine postgressql://username:password@host:port/db_name
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    #Read file parquet file into pandas dataframe using the pyarrow engine
    df = pd.read_parquet(url, engine='pyarrow')

    #Defines a schema, names it to yellow_taxi_data, and then assigns it to postgres
    print(pd.io.sql.get_schema(df,name='yellow_taxi_data',con=engine))


    #Parse tpep_pickup_datetime and tpep_dropoff_datetime to datetimestamps
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    #Creates the table in postgres with only the field names. Name = yellow_taxi_data, Engine is the postgres database, if_exists = 'replace' if a table already exists with this name it will replace it
    df.head(n=0).to_sql(name=table_name,con=engine,if_exists='replace')
       

    # Define a function to create batches so that when the script appends them into the sql database there are smaller chunks of data
    # The function runs a for loop that yields a the different items in the dataframe
    def create_batches(dataframe, batch_size):
        for start in range(0, len(dataframe), batch_size):
            yield dataframe.iloc[start:start + batch_size]

    # Specify the desired batch size
    batch_size = 100000  # For example, 100 rows per batch

    # Creates the batches
    batches = list(create_batches(df, batch_size))

    # Display the first batch (for demonstration purposes)
    print(batches[0])

    #For loop used to append batches of the data to the postgresql database
    t_start = time()
    count = 0
    
    #For loop that takes each batch of data and appends it to the postgres database
    for batch in batches:
        #Takes the time at the beginning of the loop
        count += 1
        
        #Appends the batch to the database in postgres
        b_start = time()
        batch.to_sql(name=table_name, con=engine, if_exists='append')
        b_end = time()
        print(f'inserted! time taken {b_end-b_start:10.3f} seconds.\n')

        
        t_end = time()
        
        print('inserted another chunk..., took %.3f second' %(t_end - t_start))
    t_end = time()   
    print(f'Completed! Total time taken was {t_end-t_start:10.3f} seconds for {count} batches.')   


#Main function where the script begins
if __name__ == '__main__':
    #Parses the username, password, host, port, database, table name and url via the argparse function
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')
    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')
    parser.add_argument('--url', required=True, help='url of the csv file')

    args = parser.parse_args()
    #Call the main function and parses through the arguments
    main(args)
    