import os
import pandas as pd
import sqlalchemy
from sqlalchemy import text
import sys
import numpy as np
import re
from pathlib import Path

path_to_raw_file = str(
    Path(__file__).parents[2]) + "/NEW_DOWNLOAD/pkl-20230103T192609Z-001/pkl/datakind.iccmview_assessment.pkl"
path_to_synch_files = str(
    Path(__file__).parents[2]) + "/synthetic_data/drive-download-20221222T135942Z-001"
path_to_dot_setup = "\\db\\dot_iccm_environment.sql"

def read_excel_file(file_path):
    print(f"Reading excel {file_path} pip3 install  ...")
    df = pd.read_excel(file_path)
    return df

def get_postgres_engine(server, port, user, password, database):
    engine = sqlalchemy.create_engine(f"postgresql://{user}:{password}@{server}:{port}/{database}")
    return engine

def strip_non_aphanumeric(text):
    return re.sub(r'\W+', '_', text).lower()


def add_to_dict(file):
    key = str(file).split(".")[0]
    value = pd.read_csv(file)
    return key, value


password = "secret"
user = "secret"
server = "secret"
port = "secret"
database = "secret"

if password == None:
    print("You need to set DB connection parameters as environment variables")
    print("Please see README for how")
    sys.exit()

os.chdir(path_to_synch_files)
# Read in all synthetic files, create DB table under public and insert values.
for file in os.listdir():
    print(f"Saving {add_to_dict(file)[0]} to the database ...")
    engine = get_postgres_engine(server, port, user, password, database)
    engine.execute(f'DROP TABLE IF EXISTS {add_to_dict(file)[0]} CASCADE;')
    add_to_dict(file)[1].to_sql(add_to_dict(file)[0], engine, if_exists='replace', index=False, schema='public')

# Read in raw assessment data
iccmview_assessment = pd.read_pickle(path_to_raw_file)

# Save iccm raw data to database
print("Saving raw data to the database ...")
engine = get_postgres_engine(server, port, user, password, database)
engine.execute('DROP TABLE IF EXISTS iccm_assessment_raw CASCADE;')
iccmview_assessment.to_sql('iccm_assessment_raw', engine, if_exists='replace', index=False, schema='public')

# Create DOT environment for iccm tests
#print("Creating DOT environment for iccm tests ...")
#engine = get_postgres_engine(server, port, user, password, database)
#with engine.connect() as con:
#    with open(path_to_dot_setup) as file:
#        query = text(file.read())
#        con.execute(query)

print("Done")
