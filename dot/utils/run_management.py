"""Package to contain helper functions for running the DOT Pipeline. Includes logging
   and catching exceptions.
   mjh.
"""
import sys
import os
import traceback
import datetime
import pandas as pd
from utils.connection_utils import create_sqlalchemy_engine
from utils.configuration_management import (
    generate_tests_from_db,
    generate_master_config_files,
    create_project_directories,
)
from utils.utils import (
    save_tests_to_db,
    get_test_rows,
    generate_dbt_test_coverage_report,
    set_summary_stats,
)
from utils.dbt import (
    run_dbt_core,
    archive_previous_dbt_results,
    create_failed_dbt_test_models,
    run_dbt_test,
    extract_df_from_dbt_test_results_json,
)
from utils.great_expectations import run_ge_tests, extract_df_from_ge_test_results_csv
from utils.configuration_utils import load_credentials, DbParamsConnection


def run_dot_stages(project_id, logger, run_id):
    """Runs the full pipeline of DOT:
    - dbt tests
    - great expectation tests
    - report generation and save of results to the database

    Parameters
    ----------
    project_id : str
        Project ID, eg 'Muso'. Must align with project_id in dot.projects
    logger : logger object
        The logger
    run_id: UUID
         Run ID, as provided by run_everything.py, set with ...
         run_id = run_id = uuid.uuid4()
         This UUID links results in dot.test_results with dot.run_log

    Also note that if environment variable DISABLE_TEST_GENERATION is set,
    the pipeline will not generate test files based on the contents of
    dot.configured_tests.
    This env variable is for testing purposes only, if using it you'll need to
    make sure test files exist in the correct places (see
    configuration_management.py for more details).

    Returns
    -------
    No variables returned, but does update the run status in dot.run_log
    """

    dbt_test_summary = pd.DataFrame()
    dbt_test_rows = pd.DataFrame()
    ge_test_summary = pd.DataFrame()
    ge_test_rows = pd.DataFrame()

    # Create any directories dot needs for outputs and configuration files
    create_project_directories(project_id, logger=logger)

    # Generate master config files
    generate_master_config_files(project_id, logger=logger)

    # Generate config files from DB
    if (
        "DISABLE_TEST_GENERATION" not in os.environ
    ):  # TODO if set, `dot_tests` will not exist and the rest will fail
        dot_tests = generate_tests_from_db(project_id=project_id, logger=logger)

    # ========================= preparation ============================
    if not os.path.isdir(f"generated_files/{project_id}"):
        os.makedirs(f"generated_files/{project_id}")

    # ========================== DBT tests =============================
    if "dbt" in list(dot_tests["library"]):
        run_dbt_core(project_id, logger)
        generate_dbt_test_coverage_report(project_id, logger)
        archive_previous_dbt_results(logger)
        create_failed_dbt_test_models(project_id, logger, "view")
        run_dbt_test(project_id, logger)
        # dbt.run_dbt_chv_tests(logger)

    # =========================== GE tests =============================
    if "great_expectations" in list(dot_tests["library"]):
        run_ge_tests(project_id, logger)

    # ================= Extract tests from results files ===============
    if "dbt" in list(dot_tests["library"]):
        dbt_test_summary = extract_df_from_dbt_test_results_json(
            run_id, project_id, logger
        )
        dbt_test_rows = get_test_rows(dbt_test_summary, run_id, project_id, logger)

    if "great_expectations" in list(dot_tests["library"]):
        ge_test_summary = extract_df_from_ge_test_results_csv(
            run_id, project_id, logger
        )
        ge_test_rows = get_test_rows(ge_test_summary, run_id, project_id, logger)

    all_tests_summary = pd.concat([dbt_test_summary, ge_test_summary])
    all_tests_rows = pd.concat([dbt_test_rows, ge_test_rows])

    if all_tests_summary.shape[0] > 0:

        # ===== Populate summary stats for rows total, passed, failed =====
        all_tests_summary = set_summary_stats(all_tests_summary, project_id, logger)

        # ========================= Save results  =========================
        # To flat file, useful for debugging
        all_tests_summary.to_excel(f"./generated_files/{project_id}/all_tests_summary.xlsx")
        all_tests_rows.to_excel(f"./generated_files/{project_id}/all_tests_rows.xlsx")

        # To DB
        save_tests_to_db(all_tests_rows, all_tests_summary, project_id, logger)

        logger.info(
            "Ping!!! ... DOT run "
            + str(run_id)
            + " complete for project "
            + str(project_id)
            + ". 😊"
        )
    else:
        logger.info(
            "Ooops!!! ... DOT run "
            + str(run_id)
            + " or project "
            + str(project_id)
            + " has no test results."
        )


def run_dot_tests(project_id, logger, run_id):
    """Wrapper around the DOT pipeline which will set status, start and end
    times in dot.run_log. Also catches exception and updates dot.run_log
    to set status='Failed'

       Parameters
       ----------
       project_id : str
           Project ID, eg 'Muso'. Must align with project_id in dot.projects
       logger : logger object
           The logger
       run_id: UUID
            The UUID for the current run, generated by the driver script. This UUID
            will be stored in dot.run_log as well as dot.test_results.

       Returns
       -------
       Nothing
    """
    db_credentials = load_credentials(project_id, DbParamsConnection["dot"])
    schema_dot = db_credentials["schema"]
    engine = create_sqlalchemy_engine(db_credentials)

    # Create our index
    run_start = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Initialize our row of data to be input into status table
    status = pd.DataFrame(
        {
            "run_id": run_id,
            "project_id": project_id,
            "run_start": run_start,
            "run_finish": None,
            "run_status": "Running",
            "run_error": None,
        },
        index=[0],
    )
    logger.info(status)
    status.to_sql("run_log", engine, index=False, if_exists="append", schema=schema_dot)

    # Attempts the main function
    try:
        logger.info("Running tests for project_id: %s", project_id)

        # Run the dot_pipeline
        run_dot_stages(project_id, logger, run_id)

        # If no errors occur updates SQL table to say completed
        run_finish = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sql = (
            "UPDATE "
            + schema_dot
            + ".run_log SET run_status = 'Finished', run_finish = '"
            + run_finish
            + "' WHERE run_id = '"
            + str(run_id)
            + "'"
        )
        logger.info(sql)
        with engine.begin() as conn:
            conn.execute(sql)

    except Exception as e:
        # Make sure we get them logged
        err_block = "+++++++++++++++++++++++++++++++++ ERROR ++++++++++++++++++++++++++"
        logger.error(err_block)
        logger.error(sys.exc_info())
        logger.error(err_block)

        error_string = str(sys.exc_info())

        tb = sys.exc_info()[2]
        tb = traceback.format_tb(tb)
        for t in tb:
            logger.error(t)
            tb_str = t + "\n\n"
        error_string = error_string + tb_str

        error_string = error_string.replace('"', '""').replace("'", "''")

        # Run failed
        run_finish = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sql = (
            "UPDATE "
            + schema_dot
            + ".run_log SET run_status = 'Failed', run_finish = '"
            + run_finish
            + "', run_error='"
            + error_string
            + "' WHERE run_id = '"
            + str(run_id)
            + "'"
        )
        logger.info(sql)
        with engine.begin() as conn:
            conn.execute(sql)

        logger.info("Setting Feed_Status to ERROR")
        raise e
