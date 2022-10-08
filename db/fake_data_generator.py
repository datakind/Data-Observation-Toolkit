import pandas as pd
from faker import Faker
from faker_airtravel import AirTravelProvider
from flatten_json import flatten
import numpy as np
from datetime import datetime
from datetime import timedelta
import random

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

flights_sql = '''
CREATE TABLE IF NOT EXISTS flight_data(
    departure_time DATETIME NULL,
    airline VARCHAR(200) NULL,
    origin_airport  VARCHAR(200) NULL,
    origin_iata  VARCHAR(200) NULL,
    destination_airport VARCHAR(200) NULL,
    destination_iata VARCHAR(200) NULL,
    stops INT NULL,
    price FLOAT NULL
);

'''
for index, r in flight_data.iterrows():
    flights_sql += f"INSERT INTO flight_data VALUES('{r['departure_time']}','{r['airline']}', '{r['origin_airport']}','{r['origin_iata']}'," \
          f"'{r['destination_airport']}', '{r['destination_iata']}', '{r['stops']}', {r['price']} );\n"

airports_sql = '''
CREATE TABLE IF NOT EXISTS airport_data(
    airport  VARCHAR(200) NULL,
    airport_iata  VARCHAR(200) NULL
);

'''
for index, r in airport_data.iterrows():
    airports_sql += f"INSERT INTO airport_data VALUES('{r['origin_airport']}','{r['origin_iata']}');\n"

with open('./dot/3-demo_data.sql', 'w') as f:
    f.write(airports_sql)
    f.write(flights_sql)

print("Done")