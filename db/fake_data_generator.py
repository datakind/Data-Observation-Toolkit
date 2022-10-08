"""
This script will generate fake data which can be used to demo DOT. See below
for code to generate each test type scenario. Script saves a sql file in ./dot which
will be included as part of Docker build.
"""
import pandas as pd
from faker import Faker
from faker_airtravel import AirTravelProvider
from flatten_json import flatten
import numpy as np
from datetime import datetime
from datetime import timedelta
import random
import uuid

NUMBER_OF_FLIGHTS = 100

np.random.seed(seed=12345)
Faker.seed(0)
fake = Faker()
# this is to seed the custom provider of airports for deterministic results
random.seed(10)

start_time = '01/01/2022 11:13:08.230010'
date_format_str = '%d/%m/%Y %H:%M:%S.%f'
flight_time = datetime.strptime(start_time, date_format_str)

fake.add_provider(AirTravelProvider)

flight_data = []
airport_data = []

# Generate data
for i in range(NUMBER_OF_FLIGHTS ):
    flight_time = flight_time + timedelta(seconds=i*10)
    f = flatten(fake.flight())
    f['departure_time'] = flight_time
    flight_data.append(f)
flight_data = pd.DataFrame(flight_data)

# Make SQL friendly
flight_data = flight_data.replace("'","''", regex=True)
airport_data = flight_data[['origin_airport', 'origin_iata']].drop_duplicates()

print("Adding test fail scenarios to generated data ...")
print("Adding a broken relationship ...")
# Remove a row from airports so there isn't a relationship to it from flights
airport_data = airport_data.drop(3)

print("Adding unique value exception ...")
duplicate = airport_data.iloc[4]
airport_data=airport_data.append(duplicate)

print("Adding not negative exception ...")
flight_data.loc[2,"price"] = -100
airport_data = airport_data.append(duplicate)

print("Adding null values, and associated values not null, exceptions ...")
nan_mat = np.random.random(flight_data.shape) < 0.05
flight_data = flight_data.mask(nan_mat)

print("Adding accepted values exceptions ...")
flight_data.loc[6,"stops"] = 97

print("Adding duplicate forms (records) ...")
duplicate = flight_data.iloc[4]
flight_data = flight_data.append(duplicate)

print("Expect similar means across reporters (airlines) ...")
duplicate = flight_data.iloc[4]
flight_data.loc[flight_data["airline"]=="British Airways","price"] = 0.1*flight_data.loc[flight_data["airline"]=="British Airways","price"]

flight_data = flight_data.reset_index()
airport_data = airport_data.reset_index()

flights_sql = '''
CREATE TABLE IF NOT EXISTS flight_data(
    uuid UUID PRIMARY KEY,
    departure_time TIMESTAMP WITH TIME ZONE NULL,
    airline VARCHAR(200) NULL,
    origin_airport  VARCHAR(200) NULL,
    origin_iata  VARCHAR(200) NULL,
    destination_airport VARCHAR(200) NULL,
    destination_iata VARCHAR(200) NULL,
    stops VARCHAR(30) NULL,
    price FLOAT NULL
);

'''
for index, r in flight_data.iterrows():
    uuid_str = uuid.uuid3(uuid.NAMESPACE_OID, str(r['origin_airport'])+str(r['departure_time'])+str(index))
    flights_sql += f"INSERT INTO flight_data VALUES('{uuid_str}', '{r['departure_time']}','{r['airline']}', '{r['origin_airport']}','{r['origin_iata']}'," \
          f"'{r['destination_airport']}', '{r['destination_iata']}', '{r['stops']}', {r['price']} );\n"

airports_sql = '''
CREATE TABLE IF NOT EXISTS airport_data(
    uuid UUID PRIMARY KEY,
    airport  VARCHAR(200) NULL,
    airport_iata  VARCHAR(200) NULL
);

'''
for index, r in airport_data.iterrows():
    uuid_str = uuid.uuid3(uuid.NAMESPACE_OID, r['origin_airport']+str(index))
    airports_sql += f"INSERT INTO airport_data VALUES('{uuid_str}','{r['origin_airport']}','{r['origin_iata']}');\n"

airports_sql = airports_sql.replace("'nan'", "NULL").replace("'NaT'", "NULL")
flights_sql = flights_sql.replace("'nan'", "NULL").replace("'NaT'", "NULL")
flights_sql = flights_sql.replace("nan", "NULL")

with open('./dot/3-demo_data.sql', 'w') as f:
    f.write(airports_sql)
    f.write(flights_sql)

print("Done")