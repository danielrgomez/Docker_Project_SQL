import os
import pandas as pd
#Open source SQL toolkit and object relational mapper for Python
from sqlalchemy import create_engine
from time import time
import argparse

def main(params):
    #Sets paramters parsed through the function
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    print('working....')

    #Sets the CSV Name = 'yellow_tripdata_2021-01.csv.gzip'
    csv_name = 'yellow_tripdata_2021-01.csv.gzip'
    #Runs the os function called system and gets the data from the url
    os.system(f"wget {url} -0 {csv_name}")

    #Creating the engine postgressql://username:password@host:port/db_name
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    #Will read the csv file in batches as opposed to the entire 1million rows
    df_iter = pd.read_csv(csv_name,iterator=True,chunksize=100000,compression= 'gzip')

    #Next iteration
    df = next(df_iter)


    #Parse tpep_pickup_datetime and tpep_dropoff_datetime to datetimestamps
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    #Will create the table in postgres with only field names. Name = yellow_taxi_data, Engine is the postgres database, if_exists = 'replace' if a table already exists with this name it will replace it
    df.head(n=0).to_sql(name=table_name,con=engine,if_exists='replace')

    #Will append the table in postgres with the data. Name = yellow_taxi_data, Engine is the postgres database, if_exists = 'replace' if a table already exists with this name it will replace it
    df.to_sql(name='yellow_taxi_data',con=engine,if_exists='append')


    #While loop used to append batches of the data to the postgresql database
    while True:
        #Takes the time at the beginning of the loop
        t_start = time()
        
        #Next iteration
        df = next(df_iter)
        
        #Parses the datetimestamps
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        
        #Appends the next iteration to the postgres database
        df.to_sql(name=table_name,con=engine,if_exists='append')

        #Takes the time at the end of the loop
        t_end = time()
        
        print('inserted another chunk..., took %.3f second' %(t_end - t_start))




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')
    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')
    parser.add_argument('--url', required=True, help='url of the csv file')

    args = parser.parse_args()
    main(args)
    #print(args.accumulate(args.integers))




