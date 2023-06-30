"""
This is a DAG to populate the DOT database with data from the source database.
It has to be run manually the first time once the project has been set up, so that
the entity_preview works

The DAG loops through a list of Postgres objects (tables/views) in the data source
       database and copy them to the DOT database
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
from run_dot_project import get_object, save_object, sync_object, default_config

with DAG(
        dag_id="first_synchronization",
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
                    },
                    dag=dag,
                )
            )

    for i in range(len(af_tasks)):
        if i > 0:
            af_tasks[i - 1] >> af_tasks[i]
