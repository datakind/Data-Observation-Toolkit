"""
This is a DAG for running the DOT!
It will:

    1. Loop through a list of Postgres objects (tables/views) in the data source
       database and copy them to the DOT database
    2. Run DOT
"""
import json
from os import system
from datetime import datetime
import pandas as pd
from airflow.models import DAG  # pylint: disable=import-error
from airflow.operators.python import PythonOperator  # pylint: disable=import-error
from airflow.operators.bash_operator import BashOperator  # pylint: disable=import-error
from airflow.hooks.postgres_hook import PostgresHook  # pylint: disable=import-error
from airflow.hooks.base import BaseHook  # pylint: disable=import-error
from airflow.models import Variable  # pylint: disable=import-error
from sqlalchemy import create_engine


def get_object(
        object_name_in,
        earliest_date_to_sync,
        date_field,
        source_conn_in,
        columns_to_exclude,
        source_schema_in,
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
        Date field on each record for this object. Set None if one wasn't provided for DB object
    source_conn_in: String
       Airflow connection ID where data lives.
       Note, the connection name must exactly equal the db name.
    columns_to_exclude: Array
        A list of names to exclude from the sync
    """

    connection = BaseHook.get_connection(source_conn_in)

    sql_stmt = (
            "SELECT * FROM "
            + source_schema_in
            + "."
            + object_name_in
    )
    if date_field != None:
        sql_stmt += (" WHERE "
                     + date_field
                     + " >= '"
                     + earliest_date_to_sync
                     + "'")
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
            + source_schema_in
            + "' "
            + " ORDER BY ordinal_position "
    )
    print(sql_stmt)
    pg_hook = PostgresHook(postgres_conn_id=source_conn_in, schema=source_conn_in)
    pg_conn = pg_hook.get_conn()
    cursor = pg_conn.cursor()
    cursor.execute(sql_stmt)
    columns = cursor.fetchall()

    # Fail back to views
    if len(columns) == 0:
        sql_stmt = (
                "SELECT a.attname as \"column_name\","
                + " pg_catalog.format_type(a.atttypid, a.atttypmod) as \"data_type\" "
                + " FROM pg_attribute a "
                + "  JOIN pg_class t on a.attrelid = t.oid "
                + "  JOIN pg_namespace s on t.relnamespace = s.oid "
                + " WHERE a.attnum > 0 "
                + "  AND NOT a.attisdropped "
                + " AND t.relname = '" + object_name_in + "' "
                + " AND s.nspname = '" + source_schema_in + "' "
                + " ORDER BY a.attnum; "
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

    # Remove any PII columns as set in JSON file 'columns_to_exclude' for the entity.
    data = pd.DataFrame(data=data, columns=column_list)
    data.drop(columns_to_exclude, inplace=True, axis=1)
    indices = []
    for i in range(0, len(column_list)):
        if column_list[i] in columns_to_exclude:
            indices.append(i)

    for i in reversed(indices):
        del column_list[i]
        del type_list[i]

    print(column_list)
    print(type_list)
    print(data)

    return data, column_list, type_list


def save_object(
        object_name_in, target_conn_in, data_in, column_list_in, type_list_in, source_db_in, source_schema_in,
        date_field=None, id_field=None
        ):
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
    source_schema_in: String
       Name of source schema
    """

    if date_field:
        MODE = "append"
    else:
        MODE = "replace"

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

    schema = "data_" + source_db_in.replace("-", "_") + '_' + source_schema_in.replace("-", "_")

    # Cascade drop target table if in replace mode.
    # This will also drop any DOT model views onto this data
    if MODE == "replace":
        with PostgresHook(
                postgres_conn_id=target_conn_in, schema=target_conn_in
        ).get_conn() as conn:
            cur = conn.cursor()
            query = f"DROP TABLE IF EXISTS {schema}.{object_name_in} CASCADE;"
            print(query)
            cur.execute(query)
    elif MODE == "append":
        with PostgresHook(
                postgres_conn_id=target_conn_in, schema=target_conn_in
        ).get_conn() as conn:
            cur = conn.cursor()
            # Check if target table exists first
            cur.execute(f"SELECT to_regclass('{schema}.{object_name_in}');")
            if cur.fetchone()[0] is not None:
                if id_field and not data_in.empty:
                    # Delete overlapping rows by ID before appending
                    ids = tuple(data_in[id_field].tolist())
                    if len(ids) > 0:
                        print(f"Deleting {len(ids)} overlapping rows from {schema}.{object_name_in}")
                        # Chunk the IDs to avoid hitting max parameters limit in Postgres
                        chunk_size = 1000
                        for i in range(0, len(ids), chunk_size):
                            chunk = ids[i:i + chunk_size]
                            if len(chunk) == 1:
                                query = f"DELETE FROM {schema}.{object_name_in} WHERE {id_field} = %s"
                                cur.execute(query, (chunk[0],))
                            else:
                                query = f"DELETE FROM {schema}.{object_name_in} WHERE {id_field} IN %s"
                                cur.execute(query, (chunk,))

    print(data_in.info())
    print(type_list_in)

    # Test to see if schema exists, if not, create
    with PostgresHook(
            postgres_conn_id=target_conn_in, schema=target_conn_in
    ).get_conn() as conn:
        cur = conn.cursor()
        query = f"CREATE SCHEMA IF NOT EXISTS {schema};"
        print(query)
        cur.execute(query)

    print("Saving data to: " + schema + "." + object_name_in)
    data_in.to_sql(
        object_name_in, engine, index=False, if_exists=MODE, schema=schema
    )

    for i in range(len(column_list_in)):
        col = column_list_in[i]
        type = type_list_in[i]
        using = f"USING {col}::{type}"
        query = f"ALTER TABLE {schema}.{object_name_in} ALTER COLUMN {col} TYPE {type} {using};"
        with PostgresHook(
                postgres_conn_id=target_conn_in, schema=target_conn_in
        ).get_conn() as conn:
            cur = conn.cursor()
            print(query)
            cur.execute(query)


def sync_object(
        object_name_in,
        earliest_date_to_sync,
        date_field,
        source_conn_in,
        target_conn_in,
        columns_to_exclude,
        source_schema_in,
        id_field=None,
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
    columns_to_exclude: Array
        A list of names to exclude from the sync
    """

    # Get the data
    data, column_list, type_list = get_object(
        object_name_in,
        earliest_date_to_sync,
        date_field,
        source_conn_in,
        columns_to_exclude,
        source_schema_in,
    )

    # Save the data
    save_object(
        object_name_in, target_conn_in, data, column_list, type_list, source_conn_in, source_schema_in,
        date_field=date_field, id_field=id_field
    )

def drop_tables_in_dot_tests_schema(target_conn_in, schema_to_drop_from):
    """
    Clear the DOT tests schema before syncing source data.

    New columns / column types can change on sync. Postgres blocks ALTER TABLE
    while dependent views exist, so this drops views first, then any leftover
    base tables. dbt recreates the views on the next DOT run.

    Input
    -----
    target_conn_in: Target database
    schema_to_drop_from: Schema to clear (e.g. data_dot_data_public_tests)

    Action
    ------
    1) Set search_path to the tests schema
    2) DROP VIEW for every view in that schema
    3) DROP TABLE for every BASE TABLE in that schema
    """

    with PostgresHook(
            postgres_conn_id=target_conn_in, schema=target_conn_in
    ).get_conn() as conn:
        cur = conn.cursor()
        cur.execute(f"SET search_path TO {schema_to_drop_from}")
        # information_schema.tables includes both views and base tables; use
        # the matching DROP statement for each object type.
        cur.execute(
            """
            DO $$
            DECLARE
                r RECORD;
            BEGIN
                FOR r IN (
                    SELECT table_name
                    FROM information_schema.views
                    WHERE table_schema = current_schema()
                )
                LOOP
                    EXECUTE 'DROP VIEW IF EXISTS '
                        || quote_ident(r.table_name)
                        || ' CASCADE';
                END LOOP;

                FOR r IN (
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = current_schema()
                      AND table_type = 'BASE TABLE'
                )
                LOOP
                    EXECUTE 'DROP TABLE IF EXISTS '
                        || quote_ident(r.table_name)
                        || ' CASCADE';
                END LOOP;
            END $$;
            """
        )

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
        source_schema = project.get("source_schema", "public")

        # Drop the tables in the DOT tests schema, so we can import new data, columns and types
        schema_to_drop_from = "data_" + source_conn.replace("-", "_") + "_" + source_schema.replace("-", "_") + "_tests"
        print(schema_to_drop_from)
        af_tasks.append(
            PythonOperator(
                task_id=f"drop_tables_from_schema_{project_id}_{schema_to_drop_from}",
                python_callable=drop_tables_in_dot_tests_schema,
                op_kwargs={
                    "target_conn_in": target_conn,
                    "schema_to_drop_from": schema_to_drop_from
                },
                dag=dag,
            )
        )

        # Sync data and link to dot.
        for i in range(len(objects_to_sync)):

            object_name = objects_to_sync[i]["object"]
            if "date_field" in objects_to_sync[i] and objects_to_sync[i]["date_field"] != "":
                date_field = objects_to_sync[i]["date_field"]
            else:
                date_field = None
            id_field = objects_to_sync[i]["id_field"]
            columns_to_exclude = (
                objects_to_sync[i]["columns_to_exclude"]
                if "columns_to_exclude" in objects_to_sync[i]
                else []
            )

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
                        "columns_to_exclude": columns_to_exclude,
                        "source_schema_in": source_schema,
                        "id_field": id_field,
                    },
                    dag=dag,
                )
            )

        af_tasks.append(
            BashOperator(
                task_id=f"run_dot_{project_id}",
                dag=dag,
                bash_command=f"cd /app/dot && python run_everything.py --project_id {project_id}",
            )
        )

    for i in range(len(af_tasks)):
        if i > 0:
            af_tasks[i - 1] >> af_tasks[i]
