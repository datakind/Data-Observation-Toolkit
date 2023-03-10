import os
import pandas as pd
import re
from sqlalchemy import create_engine
import argparse

def read_csv_file(file_path):
    print(f"Reading csv {file_path} ...")
    df = pd.read_csv(file_path)
    return df

def get_postgres_engine(connection_string):
    print(connection_string)
    engine = create_engine(connection_string)
    return engine

def get_table_name(file_name):
    # Strip non-alphanumeric characters from the filename
    table_name = re.sub(r'\W+', '_', os.path.splitext(file_name)[0]).lower()
    return table_name

parser = argparse.ArgumentParser(description="Specify arguments")
parser.add_argument(
    "--connection_string",
    action="store",
    required=True,
    help="Connection to airflow target_conn",
)

connection_string = parser.parse_args().connection_string

engine = get_postgres_engine(connection_string)

for file_name in os.listdir("./local_files"):
    # Check if the file is an Excel file
    if file_name.endswith(".csv"):
            print(f"Saving {file_name} to the database ...")
            # Create a database engine

            with engine.connect() as conn:
                # Drop the table if it already exists
                table_name = get_table_name(file_name)
                engine.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE;')
                # Read the file and save it to the database
                df = read_csv_file(f"./local_files/{file_name}")
                #ToDo: populate schema from target_conn instead of hard coded!
                df.to_sql(name=table_name, con=engine, schema='public', if_exists='replace', index=False)
