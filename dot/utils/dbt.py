""" dbt utility functions """

import logging
import os
import json
import re
import pandas as pd
import psycopg2.extensions
from psycopg2 import sql

from utils.utils import (
    get_short_test_name,
    get_configured_tests_row,
    run_sub_process,
    get_entity_id_from_name,
    dot_model_PREFIX,
)
from utils.connection_utils import get_db_params_from_config
from utils.configuration_utils import (
    DbParamsConfigFile,
    DbParamsConnection,
    get_dbt_config_model_paths,
    adapt_core_entities,
)
from utils.dbt_logs import (
    read_dbt_logs,
    process_dbt_logs_row,
)


def run_dbt_core(project_id: str, logger: logging.Logger) -> None:
    """Runs the main set of dbt tests as defined (generated from db) in dbt/core/*.yml

    Parameters
    ----------
    logger : logger
        Logger
    project_id : str
        Project ID, eg 'Muso'. Must align with project_id in dot.projects
    """
    logger.info("======== Running dbt tests ========")
    if not os.path.isdir("./dbt/dbt_packages"):
        run_sub_process("dbt deps", "./dbt", logger)
    run_sub_process("dbt run -m core ", "./dbt", logger)
    run_sub_process("dbt test -m core ", "./dbt", logger)
    # Stores fails to schema, but changes dbt json files so breaks everything
    # run_sub_process('dbt test -m core --store-failures', './dbt', logger)


def create_failed_dbt_test_models(
    project_id: str, logger: logging.Logger, output_type: str = "view"
) -> None:
    """Generates custom dbt models

    Parameters
    ----------
    project_id : str
        Project id for run, eg 'Muso'
    logger : logger
        Logger
    output_type : str
        type of db objects for failing tests, could be view or table, used by DBT Jinja

    Returns
    -------
    test_df : Pandas dataframe
        List of tests
    Outputs sql model files
    Also outputs a tests csv file, though TODO this should be retired
    """

    logger.info("======== Create failed DBT test models  ========")

    # Purge old tests
    os.makedirs(os.path.dirname(f"dbt/{get_dbt_config_model_paths()}/test/test.txt"), exist_ok=True)
    for i in os.listdir(f"dbt/{get_dbt_config_model_paths()}/test/"):
        if i.endswith("sql"):
            os.remove(f"dbt/{get_dbt_config_model_paths()}/test/" + i)

    # Note that this uses the archived results so that
    # it can be rerun independent of the most recently run
    # test suite. It will only pick up changes when run_results.json
    # is archived, either manually or via run_everything.sh

    with open("dbt/target/run_results_archive.json") as f:
        run_results = json.load(f)

    with open("dbt/target/manifest_archive.json") as f:
        manifest = json.load(f)

    for i in run_results["results"]:
        # Only create models for tests that have failed
        if i["status"] != "pass":

            node = manifest["nodes"][i["unique_id"]]
            _, test_name = get_short_test_name(node)

            full_query_path = "/".join(
                ["dbt/target/run", node["package_name"], node["original_file_path"]]
            )
            full_query_path = (
                full_query_path
                if full_query_path.endswith(".sql")
                else "/".join([full_query_path, node["path"]])
            )
            with open(full_query_path) as f:
                full_query = f.read()
            query = full_query[
                full_query.find("from (") + 7 : full_query.find(") dbt_internal_test")
            ]

            # Modify queries to return full rows instead of counts
            query = re.sub(r"select\s+count\(\*\)\s+", "select * ", query)

            # Find/replace absolute table references with models
            # to preserve DBT's DAG awareness
            for model_label in re.findall(r'\s"\w+"\."\w+"\."\w+"', query):
                new_label = model_label.split(".")[-1].replace('"', "")
                query = query.replace(model_label, " {{ ref('" + new_label + "') }}")

            output_filename = f"dbt/{get_dbt_config_model_paths()}/test/{test_name}.sql"
            if os.path.exists(output_filename):
                raise Exception(
                    f"file {get_dbt_config_model_paths()}/test/{test_name}.sql' "
                    f"already exists! review that test names are unique in "
                    f"{node['original_file_path']}"
                )

            with open(output_filename, "w") as f:
                f.write(
                    "{{{{ config(materialized='{0}') }}}} \n\n".format(output_type)
                    + query
                )


def archive_previous_dbt_results(logger):
    """Archived previous dbt results

    Parameters
    ----------
    logger : logger
        Logger

    """
    logger.info("======== Archiving previous DBT results ========")
    cmd = """
            cp ./target/run_results.json ./target/run_results_archive.json
            cp ./target/manifest.json ./target/manifest_archive.json
    """
    run_sub_process(cmd, "./dbt", logger)


def run_dbt_test(project_id, logger):
    """Runs dbt custom sql tests

    Parameters
    ----------
    logger : logger
        Logger

    """
    cmd = """
            dbt run -m test
            cp ./target/run_results.json ./target/run_results_test.json
            cp ./target/manifest.json ./target/manifest_test.json
        """.format(
        project_id=project_id
    )
    run_sub_process(cmd, "./dbt", logger)


def run_dbt_chv_tests(logger):
    """Runs chv-specific tests

    TODO: Needs more work, chv tests were important in previous projects.
    Check run_everything as this function might be commented out.

    Parameters
    ----------
    logger : logger
        Logger

    """
    cmd = """
            dbt run -m chv_level_dot
            cp ./target/run_results.json ./target/run_results_chv_level.json
    """
    run_sub_process(cmd, "./dbt", logger)


def get_view_definition(project_id: str, short_test_name: str) -> str:
    """
    Figures out the view definition of a failing test
    Parameters
    ----------
    project_id: str
        e.g. Muso, for obtaining credentials
    short_test_name: str
        short name of the test (will correspond to the name of the view too)

    Returns
    -------
      str
         SQL for the view definition
    """
    schema_test, engine_test, conn_test = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"],
        DbParamsConnection["project_test"],
        project_id,
    )
    q = f"select pg_get_viewdef('{schema_test}.{short_test_name}', true)"
    view_definition = pd.read_sql(q, conn_test)
    return str(view_definition.iloc[0, 0])


def extract_df_from_dbt_test_results_json(
    run_id: str,
    project_id: str,
    logger: logging.Logger,
    target_path: str = "dbt/target",
) -> pd.DataFrame:
    """Function to parse GE csv results file (that was created by parse_results) to
    form a test_summaries standard
    dataframe.

       Parameters
       ----------
          run_id: str
             Current run ID as found in dot.run_log
          project_id: str
             Current run project ID
          logger: Logging object
             Custom logging object
          target_path: str
             Target path for test results, defaults to "dbt/target"
             Modified within tests only

       Returns
       -------
          dbt_tests_summary: Pandas dataframe
             Standard tests summary dataframe, same columns as returned by
             extract_df_from_ge_test_results_csv

    """

    logger.info("Extracting DBT test summary dataframe ...")

    dbt_results = read_dbt_logs(target_path)

    # Extract test results and save to dataframe
    dbt_tests_summary = {}
    for row in dbt_results:
        processed_row = process_dbt_logs_row(row)

        entity_id = get_entity_id_from_name(project_id, processed_row.entity_name)
        configured_test_row = get_configured_tests_row(
            processed_row.test_type,
            entity_id,
            processed_row.column_name,
            project_id,
            processed_row.test_parameters,
        )
        test_id = configured_test_row["test_id"]
        id_column_name = configured_test_row.get("id_column_name")

        # Get result view SQL definition
        failed_tests_view = ""
        view_definition = ""
        if processed_row.test_status == "fail":
            view_definition = get_view_definition(
                project_id, processed_row.short_test_name
            )
            failed_tests_view = processed_row.short_test_name

        dbt_tests_summary[processed_row.unique_id] = {
            "run_id": run_id,
            "test_id": test_id,
            "entity_id": entity_id,
            "test_type": processed_row.test_type,
            "column_name": processed_row.column_name,
            "id_column_name": id_column_name,
            "test_parameters": processed_row.test_parameters,
            "test_status": processed_row.test_status,
            "test_status_message": processed_row.test_message,
            "failed_tests_view": failed_tests_view,
            "failed_tests_view_sql": view_definition,
        }
    dbt_tests_summary = (
        pd.DataFrame(dbt_tests_summary)
        .transpose()
        .sort_values(by=["test_type", "entity_id"])
    )
    dbt_tests_summary.set_index("test_id")

    return dbt_tests_summary


def create_core_entities(
    schema_dot: str,
    conn: psycopg2.extensions.connection,
    schema_project: str,
    project_id: str,
    output_path: str,
    logger: logging.Logger,
) -> None:
    """
    Reads configured_entities from the DOT schema and writes them as sql files for dbt

    Parameters
    ----------
    schema_dot: str
        DOT schema
    conn: psycopg2.extensions.connection
        db connection
    schema_project: str
        project schema
    project_id: str
        project_id
    output_path: str
        output path for the files
    logger: logging.Logger
        logger object
    """

    query = sql.SQL(
        f"select * from {schema_dot}.configured_entities where project_id='{project_id}'"
    )

    configured_entities = pd.read_sql(query, conn)
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    logger.info("Generating DBT core entities' files ...")

    # Remove existing files so entities can be deactivated
    for f in os.listdir(output_path):
        if ".yml" in f:
            os.remove(os.path.join(output_path, f))

    for i, row in configured_entities.iterrows():
        filename = os.path.join(
            output_path, f"{dot_model_PREFIX}{row['entity_name']}.sql"
        )
        logger.info(f"Writing core entity file: {filename}")
        with open(filename, "w") as f:
            for line in adapt_core_entities(schema_project, row["entity_definition"]):
                f.write(line)
