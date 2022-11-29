"""
This script will generate fake, chw specific data which can be used to demo DOT. See below
for code to generate each test type scenario. Script saves a sql file in ./dot which
will be included as part of Docker build. ToDo: Include created sql file in docker build command either in readme or in code

Assumptions:
- A patient can be assessed in different regions and different CHWs
- The number of visits per person is automatically derived from number of patients and number of records by random picking
- If there are danger signs or a positive malaria test, a follow up visit has to be conducted!
- In case of a positive malaria test, treatment has to be administered
- Tests for broken thermometer do NOT need a big sample size to work (no check for distribution), but simply detect outliers
"""
import datetime
import pandas as pd
import numpy as np
from faker import Faker
import random

number_of_chws = 10
number_of_patiens = 50
number_of_records = 50
number_of_data_issues = 150

"""The script should generate random data, but have a seed set so if run twice we get the same data. """
np.random.seed(seed=12345)
Faker.seed(0)
fake = Faker()
random.seed(10)

# Create a table for community health workers (chw) incl. location
chw_sql = """
CREATE TABLE IF NOT EXISTS public.chw_chw(
    chw_uuid UUID PRIMARY KEY,
    region VARCHAR(200) NULL
);
"""

# Create regions
region_data = []

for _ in range(number_of_chws):
    region = fake.bothify(text='Region ?', letters='ABCDEFG')
    region_data.append(region)

# Create CHWs
chw_uuids = []

for _ in range(number_of_chws):
    chw = fake.md5(raw_output=False)
    chw_uuids.append(chw)

# Create DataFrame for easier manipulation and population of SQL table
chw_data = pd.DataFrame(list(zip(chw_uuids, region_data)), columns=["chw_uuid", "region"])
chw_data.drop_duplicates(inplace=True)

# Enter some null values for region
chw_data["region"][-3:] = "NULL"

for index, r in chw_data.iterrows():
    if r['region'] == "NULL":
        chw_sql += (
            f"INSERT INTO public.chw_chw VALUES('{r['chw_uuid']}', {r['region']});\n"
        )
    else:
        chw_sql += (
            f"INSERT INTO public.chw_chw VALUES('{r['chw_uuid']}', '{r['region']}');\n"
        )

# Create a table for patients
patient_sql = """
CREATE TABLE IF NOT EXISTS public.chw_patient(
    record_id UUID PRIMARY KEY,
    patient_uuid UUID NULL
);
"""

# Create patients
patient_uuids = []
record_ids = []

for _ in range(number_of_patiens):
    record_id = fake.md5(raw_output=False)
    record_ids.append(record_id)
    patient = fake.md5(raw_output=False)
    patient_uuids.append(patient)

# Create DataFrame for easier manipulation and population of SQL table
patient_data = pd.DataFrame(list(zip(record_ids, patient_uuids)), columns=["record_id", "patient_uuid"])
patient_data.drop_duplicates(inplace=True)

# Add some duplicates in the patient data
# Note: Duplicates are dropped earlier to create a more controlled environment
patient_data["patient_uuid"].iloc[-2:] = patient_data["patient_uuid"].iloc[-4:-2]

for index, r in patient_data.iterrows():
    patient_sql += (
        f"INSERT INTO public.chw_patient VALUES('{r['record_id']}','{r['patient_uuid']}');\n"
    )

# Create a table for assessments incl. uuid, date, chw (uuid), patient (uuid), patient temperature, malaria test
# result and any treatments administered
assessment_sql = """
CREATE TABLE IF NOT EXISTS public.chw_patient_assessment(
    assessment_id UUID PRIMARY KEY, 
    date DATE NULL,
    chw_id VARCHAR(200) NULL,
    patient_uuid VARCHAR(200) NULL,
    patient_temperature DOUBLE PRECISION NULL,
    danger_signs BOOLEAN NULL,
    malaria_test_result BOOLEAN NULL,
    malaria_treatment_given BOOLEAN NULL
);
"""

assessment_id, assessment_date, assessment_chw, assessment_patient, assessment_temperature, assessment_danger_sign, assessment_malaria_test, assessment_malaria_treatment = (
    [] for i in range(8))


# Assumption: Whenever a malaria test is positive, treatment is given
def treatment(test_result):
    if test_result:
        treatment = True
    else:
        treatment = False

    return treatment

#Create assessment data
for _ in range(number_of_records):
    assessment_id.append(fake.md5(raw_output=False))
    date = fake.date_this_century()
    assessment_date.append(date)
    assessment_chw.append(fake.random.choice(chw_uuids))
    assessment_patient.append(fake.random.choice(patient_uuids))
    assessment_temperature.append(round(fake.pyfloat(min_value=36.5, max_value=37.5), 2))
    assessment_danger_sign.append(fake.pybool())
    malaria_test = fake.boolean(chance_of_getting_true=20)
    assessment_malaria_test.append(malaria_test)
    assessment_malaria_treatment.append(treatment(malaria_test))

# Create DataFrame for easier manipulation and population of SQL table
assessment_data = pd.DataFrame(
    list(zip(assessment_id, assessment_date, assessment_chw, assessment_patient, assessment_temperature,
             assessment_danger_sign, assessment_malaria_test, assessment_malaria_treatment)),
    columns=["assessment_id", "date", "chw_id", "patient_uuid", "patient_temperature",
             "danger_signs", "malaria_test_result", "malaria_treatment_given"])

# Adjust the average temperature of one CHW to be 1C lower than the rest
chw_equipment_failure = fake.random.choice(chw_uuids)
print(chw_equipment_failure)
assessment_data.loc[assessment_data["chw_id"] == chw_equipment_failure, "patient_temperature"] = round(
    fake.pyfloat(min_value=35.5, max_value=36.5), 2)

# Add some cases where a patient was diagnosed with malaria but had not follow-up treatment
# Add some cases where an initial visit showed danger signs, but there were no follow-up visits

def next_appointment(initial_assessment):
    follow_ups = initial_assessment
    for index, r in follow_ups.iterrows():
        follow_ups.at[index, "assessment_id"] = fake.md5(raw_output=False)
        follow_ups.at[index, "date"] = r["date"] + datetime.timedelta(14)
        follow_ups.at[index, "danger_signs"] = False
        follow_ups.at[index, "malaria_test_result"] = False
        follow_ups.at[index, "malaria_treatment_given"] = False
    return follow_ups

follow_ups_danger_sign = next_appointment(assessment_data[assessment_data.danger_signs][-3:])
follow_ups_treatment = next_appointment(assessment_data[assessment_data.malaria_test_result][-3:])

# Create some duplicate records for follow-up visits
follow_ups_treatment[["date", "danger_signs", "malaria_test_result", "malaria_treatment_given"]].iloc[-2:] = follow_ups_treatment[["date", "danger_signs", "malaria_test_result", "malaria_treatment_given"]].iloc[-4:-2]

assessment_data = pd.concat([assessment_data, follow_ups_danger_sign, follow_ups_treatment])

for index, r in assessment_data.iterrows():
    assessment_sql += (
        f"INSERT INTO public.chw_patient_assessment VALUES('{r['assessment_id']}','{r['date']}','{r['chw_id']}',"
        f"'{r['patient_uuid']}','{r['patient_temperature']}','{r['danger_signs']}','{r['malaria_test_result']}','{r['malaria_treatment_given']}');\n"
    )

# Save CHW demo data
with open("./dot/5-demo_data_chw.sql", "w") as f:
    f.write(chw_sql)
    f.write(patient_sql)
    f.write(assessment_sql)
