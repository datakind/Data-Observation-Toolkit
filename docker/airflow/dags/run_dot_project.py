"""
This is a DAG for running the DOT. It will:

    1. Loop through a list of Postgres objects (tables/views) in the data source
       database and copy them to the DOT database
    2. Run DOT
"""
import json
from os import system
from datetime import datetime
import pandas as pd
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from sqlalchemy import create_engine


def get_object(object_name_in, earliest_date_to_sync, date_field, source_conn_in):
    """

    Extracts data from object in source Postgres DB and saves to target DOT database in data schema.

    Parameters
    ----------
    object_name_in: String
       The Postgres db object to sync to DOT DB
    earliest_date_to_sync: String
        Only sync data after this date
    date_field: String
        Date field on each record for this object
    source_conn_in: String
       Airflow connection ID where data lives.
       Note, the connection name must exactly equal the db name.

    """

    connection = BaseHook.get_connection(source_conn_in)

    sql_stmt = (
        "SELECT * FROM "
        + connection.schema
        + "."
        + object_name_in
        + " WHERE "
        + date_field
        + " >= '"
        + earliest_date_to_sync
        + "'"
    )
    print(sql_stmt)
    pg_hook = PostgresHook(postgres_conn_id=source_conn_in, schema=source_conn_in)
    pg_conn = pg_hook.get_conn()
    cursor = pg_conn.cursor()
    cursor.execute(sql_stmt)
    data = cursor.fetchall()

    sql_stmt = (
        "SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '"
        + object_name_in
        + "'"
        + "AND table_schema = '"
        + connection.schema
        + "' "
        + " ORDER BY ordinal_position "
    )
    print(sql_stmt)
    pg_hook = PostgresHook(postgres_conn_id=source_conn_in, schema=source_conn_in)
    pg_conn = pg_hook.get_conn()
    cursor = pg_conn.cursor()
    cursor.execute(sql_stmt)
    columns = cursor.fetchall()

    # Convert to a clean list (Tuples are duplicated)
    column_list = []
    cols = [a[0] for a in columns]
    for col in list(cols):
        if "(" not in col:
            column_list.append(col)

    type_list = []
    types = [a[1] for a in columns]
    for type in list(types):
        if "(" not in col:
            type_list.append(type)

    return data, column_list, type_list


def save_object(object_name_in, target_conn_in, data_in, column_list_in, type_list_in, source_db_in):
    """

    Saves data to target DOT database in data schema.

    Parameters
    ----------
    object_name_in: String
       The Postgres db object to sync to DOT DB
    target_conn_in: String
       ID of Airflow connection
    data_in: Dataframe
       Data being saved to target table
    column_list_in: List
       List of table columns for target table
    type_list_in: List
       List of table column types for target table
    source_db_in: String
       Name of source database (same as source connid string)

    """

    # Temporary, replace existing data. TODO support delta loads
    MODE = "replace"

    data = pd.DataFrame(data=data_in, columns=column_list_in)

    connection = BaseHook.get_connection(target_conn_in)
    connection_string = (
        "postgresql://"
        + str(connection.login)
        + ":"
        + str(connection.password)
        + "@"
        + str(connection.host)
        + ":"
        + str(connection.port)
        + "/"
        + target_conn_in
    )

    engine = create_engine(
        connection_string,
        paramstyle="format",
        executemany_mode="values",
        executemany_values_page_size=1000,
        executemany_batch_page_size=200,
    )

    schema = "data_" + source_db_in.replace("-", "_")

    # Cascade drop target table if in replace mode.
    # This will also drop any DOT model views onto this data
    if MODE == "replace":
        with PostgresHook(
            postgres_conn_id=target_conn_in, schema=target_conn_in
        ).get_conn() as conn:
            cur = conn.cursor()
            query = "DROP TABLE IF EXISTS {} CASCADE;".format(
                schema + "." + object_name_in
            )
            print(query)
            cur.execute(query)

    print(data.info())
    print(type_list_in)

    # Test to see if schema exists, if not, create
    with PostgresHook(
        postgres_conn_id=target_conn_in, schema=target_conn_in
    ).get_conn() as conn:
        cur = conn.cursor()
        query = "CREATE SCHEMA IF NOT EXISTS {};".format(schema)
        print(query)
        cur.execute(query)

    print("Saving data to: " + schema + "." + object_name_in)
    data.to_sql(object_name_in, engine, index=False, if_exists="replace", schema=schema)

    for i in range(len(column_list_in)):
        col = column_list_in[i]
        type = type_list_in[i]
        using = f'USING {col}::{type}'
        query = f'ALTER TABLE {schema}.{object_name_in} ALTER COLUMN {col} TYPE {type} {using};'
        with PostgresHook(
            postgres_conn_id=target_conn_in, schema=target_conn_in
        ).get_conn() as conn:
            cur = conn.cursor()
            print(query)
            cur.execute(query)

def sync_object(
    object_name_in, earliest_date_to_sync, date_field, source_conn_in, target_conn_in
):
    """

    Extracts data from object in source Postgres DB and saves to target DOT database in data schema.

    Parameters
    ----------
    object_name_in: String
       The Postgres db object to sync to DOT DB
    earliest_date_to_sync: String
        Only sync data after this date
    date_field: String
        Date field on each record for this object
    source_conn_in: String
       Airflow connection ID where data lives, must be same as name of DB
    target_conn_in: String
       ID of Airflow connection, must same as name of DB

    """

    # Get the data
    data, column_list, type_list = get_object(
        object_name_in, earliest_date_to_sync, date_field, source_conn_in
    )

    # Save the data
    save_object(object_name_in, target_conn_in, data, column_list, type_list, source_conn_in)

def drop_dot_tests_schema(target_conn_in, schema_to_drop):
    """

        We are syncing new data where new columns and columns types might change. Postgres will prevent ALTER TABLE
        if any views exist, so we will drop the dot test schema which contains these. These will be recreated in the
        dot run. This assumes the dot tests schema is <data schema>_tests.

        Input
        -----
        target_conn_in: Target database
        schema_to_drop: Schema to, err, drop

        Action
        ------

        dot tests schema is dropped from the database.

    """

    # Test to see if schema exists, if not, create
    with PostgresHook(
            postgres_conn_id=target_conn_in, schema=target_conn_in
    ).get_conn() as conn:
        cur = conn.cursor()
        query = f'DROP SCHEMA IF EXISTS {schema_to_drop} CASCADE;'
        print(query)
        cur.execute(query)

def run_dot_app(project_id_in):
    """
    Method to run the DOT.
    """
    print("Running DOT")
    system("cd /app/dot && python run_everything.py --project_id " + project_id_in)


def default_config():
    """

    Sets configuration to determine how the DAG will run from Airflow config.
    Used if called didn't provide configuration. Returns file handle.

    Input
    -----
    Default json configuration file, in same directory as this script.

    Output
    ------

    config: File handle
       Configuration file handle of json file for what projects to run and tables to sync

    """

    # All files will be relative to $AIRFLOW_HOME
    file = open("./dags/dot_projects.json")
    return file

with DAG(
    dag_id="run_dot_project",
    schedule_interval="@weekly",
    start_date=datetime(year=2022, month=3, day=1),
    catchup=False,
) as dag:

    config = json.loads(Variable.get("dot_config", default_var=default_config().read()))

    """
    target_conn - Airflow connection name for target connection and schema
    """

    target_conn = config["target_connid"]

    af_tasks = []

    for project in config["dot_projects"]:

        """
        project_id  - Project ID, as found in dot.projects table
        objects_to_sync - List of objects to sync, each one with definition 
            of unique field and date field
        earliest_date_to_sync - Only sync data after this date for project
        source_conn - Airflow connection to define where source data is
        source_db   - Source database name
        """
        project_id = project["project_id"]
        objects_to_sync = project["objects"]
        earliest_date_to_sync = project["earliest_date_to_sync"]
        source_conn = project["source_connid"]

        # Drop the DOT tests schema so we can import new data, columns and types
        schema_to_drop = "data_" + source_conn.replace("-", "_") + "_tests"
        af_tasks.append(
            PythonOperator(
                task_id=f'drop_schema__{schema_to_drop}',
                python_callable=drop_dot_tests_schema,
                op_kwargs={
                    "target_conn_in": target_conn,
                    "schema_to_drop": schema_to_drop
                },
                dag=dag,
            )
        )

        # Sync data and link to dot.
        for i in range(len(objects_to_sync)):

            object_name = objects_to_sync[i]["object"]
            date_field = objects_to_sync[i]["date_field"]
            id_field = objects_to_sync[i]["id_field"]

            # Get the data from a object in Postgres and copy to target DB
            af_tasks.append(
                PythonOperator(
                    task_id=f"sync_object_{project_id}_{object_name}",
                    python_callable=sync_object,
                    op_kwargs={
                        "object_name_in": object_name,
                        "earliest_date_to_sync": earliest_date_to_sync,
                        "date_field": date_field,
                        "source_conn_in": source_conn,
                        "target_conn_in": target_conn,
                    },
                    dag=dag,
                )
            )

        af_tasks.append(BashOperator(
            task_id=f"run_dot_{project_id}",
            dag=dag,
            bash_command=f"cd /app/dot && python run_everything.py --project_id {project_id}",
        ))

    for i in range(len(af_tasks)):
        if i > 0:
            af_tasks[i - 1] >> af_tasks[i]