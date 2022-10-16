import logging
import sys
import re
import os
import uuid
import json
import time
from subprocess import Popen, PIPE, STDOUT
from typing import Tuple
from itertools import chain
import psycopg2 as pg

import pandas as pd
from pandas import json_normalize
from utils.connection_utils import get_db_params_from_config, get_metadata
from utils.configuration_utils import DbParamsConfigFile, DbParamsConnection

dot_model_PREFIX = "dot_model__"


def setup_custom_logger(log_name, log_level, file_logger=False):
    """Sets up a custom logger which logs to file as well as console

    Parameters
    ----------
    log_name : str
        Location of log file, eg './logs/run_everything.log'
    log_level : logging level
        from logging module, eg logging.INFO, logging.DEBUG
    file_logger : Boolean
        Log to file as well as standard out

    Returns
    -------
    logger object
    the logger which can be used for output, eg logger.info('Hi')
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger(log_name)
    if file_logger == True:
        handler = logging.FileHandler(log_name)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger.setLevel(log_level)
    logger.addHandler(screen_handler)
    return logger


def log_subprocess_output(pipe, logger):
    """Runs a subprocess, but captures output to the logger

    Parameters
    ----------
    pipe : Popen pipe
        Subprocess POpen object, for example created with ..
        pipe = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True, cwd=dir)
    logger : logger object
        Logger object, used for logging output

    Returns
    -------
    Nothing
    """
    for line in iter(pipe.readline, b""):
        line = str(line).replace("\\n", "").replace("b'", "")
        logger.info("Subprocess output: %r", line)


def run_sub_process(cmd, directory, logger):
    """Helper to run sub-process, sending output to logger.

    Parameters
    ----------
    cmd : str
        Command to be run by subprocess, eg 'ls'
    dir : str
        Directory in which to run the sub-process

    Returns
    -------
    Exit code of running the sub-process
    """
    logger.info("Running command:\n" + cmd)
    process = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True, cwd=directory)
    with process.stdout:
        log_subprocess_output(process.stdout, logger)
    exitcode = process.wait()
    if exitcode != 0:
        # DBT can produce non-zero returns. TODO to remove these, but they are benign
        # enough for alpha release
        logger.error("...")
        # logger.error("Subprocess failed!")
        # TO DO, there is a (possibly) benign dbt error we need to address sys.exit()
    return exitcode


def get_short_test_name(node: dict) -> Tuple[str, str]:
    """Figures out a human readable test_name, and a shorten version that can become
    a view name

    Parameters
    ----------
    node : dict
        Dict from test result jdon file

    Returns
    -------
    Test name: str
        Test full name
    Test short name: str
        Test short name
    """
    model_name = node["name"]
    test_name = (
        node["original_file_path"].split("/")[-1].split(".")[0]
    )  # i.e. either the name or the yaml file
    # or the SQL test name
    if not node["original_file_path"].startswith("tests"):
        sub_test_name = node.get("test_metadata", {}).get("kwargs", {}).get("name")
        column_name = node.get("column_name")
        sub_test_label = node.get("test_metadata", {}).get("name")
        if sub_test_name is not None:
            test_name = "_".join([test_name, sub_test_name])
        elif (column_name is not None) and (sub_test_label is not None):
            test_name = "_".join([test_name, sub_test_label, column_name])
        elif sub_test_label is not None:
            test_name = "_".join([test_name, sub_test_label])
        else:
            # backup solution, but no result should go here
            test_name = model_name
            print("Short test name was not found in dbt file!!!")
            sys.exit()

    short_test_name = test_name
    if not short_test_name.startswith("tr_"):
        # when calling `dbt run -m test`, the objects already have the "tr_" prefix
        short_test_name = "tr_" + short_test_name

    while len(short_test_name) > 51:
        # test name is too big to become a ddbb object
        test_name_pieces = short_test_name.split("_")
        word_to_shorten = len(test_name_pieces) - max(
            [i for i, v in enumerate(test_name_pieces) if len(v) > 1]
        )
        short_test_name = "_".join(
            test_name_pieces[:-word_to_shorten]
            + [test_name_pieces[-word_to_shorten][0]]
        )
        if word_to_shorten > 1:
            short_test_name = "_".join(
                [short_test_name] + test_name_pieces[-word_to_shorten + 1 :]
            )

    return test_name, short_test_name


def get_test_id(
    test_type: str, entity_id: str, column: str, project_id: str, test_parameters: str
) -> str:
    """Generates test UUID based on configured_test fields by finding the corresponding
    record in dot.configured_tests

    Parameters
    ----------
    test_type : str
        Test type, aligns with column test_type on dot.configured_tests
        (eg not_null)
    entity_id : str
        Entity if available, primary table for custom SQL tests
    column : str
        Column if test has column
    project_id : str
        Project id for run, eg 'Muso'
    test_parameters : str
        Test parameters string, SQL for custom SQL tests

    Returns
    -------
    UUID: str
        UUID3 id read from dot.configured_tests
    """
    test_id = get_configured_tests_row(
        test_type, entity_id, column, project_id, test_parameters
    ).get("test_id")

    if test_id is None:
        raise ReferenceError(
            f"test_id not found in db with test_type {test_type}, entity_id {entity_id} "
            f"and test_parameters {test_parameters}"
        )

    return test_id


def get_configured_tests_row(
    test_type: str, entity_id: str, column: str, project_id: str, test_parameters: str
) -> dict:
    """Gets the full row of configured_tests fields by finding the corresponding
    record in dot.configured_tests

    Parameters
    ----------
    test_type : str
        Test type, aligns with column test_type on dot.configured_tests
        (eg not_null)
    entity_id : str
        Entity if available, primary table for custom SQL tests
    column : str
        Column if test has column
    project_id : str
        Project id for run, eg 'Muso'
    test_parameters : str
        Test parameters string, SQL for custom SQL tests

    Returns
    -------
    row: dict
        dictionary with all the row attributes
    """

    # TODO REALLY we should have id's in the generated test files, where they propagate
    #  through dbt and ge.

    test_parameters = json.dumps(test_parameters)

    # else is a bit of a hack. Unfortunately this might not be supported by dbt and ge
    schema_dot, _, conn_dot = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"], DbParamsConnection["dot"], project_id
    )

    # Massage test_parameters into same form as created by regexp_replace in Postgres
    test_parameters = re.sub("\n", "", test_parameters, re.M)
    test_parameters = re.sub(r"\W+", "", test_parameters)
    if column is None:
        column = ""

    prefix = "query" if test_type == "custom_sql" else ""

    # This whole function must go away, we need to pass test_ids through dbt and ge. Below is
    # temporary.
    test_params_clause = ""
    if test_parameters != "":
        test_params_clause = f""" AND regexp_replace(LOWER(CAST(test_parameters AS VARCHAR)), '\W+', '', 'g') =
                             '{prefix}{test_parameters.lower()}';"""

    # Generate a query that will match our test details and return test_id
    query = f"""
                    SELECT
                        *
                    FROM
                        {schema_dot}.configured_tests
                    WHERE
                        test_type = '{test_type}' AND
                        entity_id = '{entity_id}' AND
                        column_name = '{column}'
                        {test_params_clause}
                """
    # print(query)

    test_row = pd.read_sql(query, conn_dot)
    if test_row.empty:
        raise ReferenceError(f"test_id not found in db with query {query}")
    return test_row.iloc[0].to_dict()


def save_tests_to_db(
    test_rows: pd.DataFrame,
    test_summary: pd.DataFrame,
    project_id: str,
    logger: logging.Logger,
):
    """Saves test results to the DOT DB into dot.test_results.

    Parameters
    ----------
    test_rows : Pandas dataframe
        Dataframe of test results, one row per row of data tested for each run
    test_summary : Pandas dataframe
        Dataframe of test results summary, one row per test_id in
        dot.configured_tests for each run
    project_id : str
        Project id for run, eg 'Muso'
    logger: Logging object
        Custom logging object
    """
    logger.info("Uploading test_results to dot DB ...")
    schema_dot, engine_dot, _ = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"], DbParamsConnection["dot"], project_id
    )

    test_rows.to_sql(
        "test_results", engine_dot, index=False, if_exists="append", schema=schema_dot
    )

    # get current columns from metadata - schema could have less columns than results
    test_results_summary_columns = [
        c.name
        for c in get_metadata().tables.get(f"{schema_dot}.test_results_summary").columns
    ]
    test_summary.loc[:, test_results_summary_columns].to_sql(
        "test_results_summary",
        engine_dot,
        index=False,
        if_exists="append",
        schema=schema_dot,
    )


def generate_row_results_df(
    id_column_values: list,
    run_id: str,
    test_id: str,
    entity_name: str,
    entity_id: str,
    status: str,
    view_name: str,
    id_column_name: str,
):
    """Generates a test_results dataframe, one row per row of data tested

    Parameters
    ----------
    id_column_values : list
        List of values for id_column in the test results view (or entity for
        passing rows not in this view)
    run_id: str
        ID of the current run, as found in dot.run_status
    test_id: str
        ID of the tests, as found in dot.configured_tests
    entity_name: str
        Entity view of data tested, or the name of the primary table for custom
        sql tests
    entity_id: str
        Entity id
    status: str
        Test status, being pass/fail/error
    view_name: str
        Name of the failed tests view in the DB
    id_column_name
        Name of the unique id column in the test_view_name

    Returns
    -------
    row_level_results_df: Pandas dataframe
        Dataframe of test results, one row per row of data tested

    """

    # Generate a new uuid base on the unique field. Note that the set is because some
    # tests, eg duplicate forms, will duplicate the 'unique' field.
    uuid_str = (
        str(run_id) + entity_name + view_name + id_column_name + str(time.time_ns())
    )
    id_column_values = list(set(id_column_values))
    uuid_list_uid = [
        uuid.uuid3(uuid.NAMESPACE_OID, str(el) + uuid_str) for el in id_column_values
    ]

    row_level_results_df = pd.DataFrame(uuid_list_uid, columns=["test_result_id"])
    row_level_results_df["run_id"] = run_id
    row_level_results_df["test_id"] = test_id
    row_level_results_df["entity_id"] = entity_id
    row_level_results_df["status"] = status
    row_level_results_df["view_name"] = view_name
    row_level_results_df["id_column_name"] = id_column_name
    row_level_results_df["id_column_value"] = id_column_values

    return row_level_results_df


def generate_failing_passing_dfs(
    failing_ids: list,
    passing_ids: list,
    run_id: str,
    test_id: str,
    entity_name: str,
    entity_id: str,
    view_name: str,
    id_column_name: str,
):
    """Generates a test_results dataframe, one row per row of data tested

    Parameters
    ----------
    failing_ids : list
        List of unique ids in entity db view that failed the test
    passing_ids: str
        List of unique ids in entity db view that passed the test
    run_id: str
        Current run ID, as found in dot.run_log
    test_id: str
        ID of the tests, as found in dot.configured_tests
    entity_name: str
        Entity view of data tested, or the name of the primary table for custom
        sql tests
    entity_id: str
        Entity id
    view_name: str
        Name of the failed tests view in the DB
    id_column_name
        Name of the unique id column in the test_view_name

    Returns
    -------
    test_failing_rows: Pandas dataframe
        Dataframe of failed test results, one row per row of data tested
    test_passing_rows: Pandas dataframe
        Dataframe of passed test results, one row per row of data tested
    """
    test_failing_rows = generate_row_results_df(
        failing_ids,
        run_id,
        test_id,
        entity_name,
        entity_id,
        "fail",
        view_name,
        id_column_name,
    )
    test_passing_rows = generate_row_results_df(
        passing_ids,
        run_id,
        test_id,
        entity_name,
        entity_id,
        "pass",
        view_name,
        id_column_name,
    )

    return test_failing_rows, test_passing_rows


def get_test_rows(
    tests_summary: pd.DataFrame, run_id: str, project_id: str, logger: logging.Logger
) -> pd.DataFrame:
    """Generates a test_results dataframe using the test_summary dataframe and
    associated test results DB views

        Parameters
        ----------
        tests_summary : pandas dataframe
            Dataframe of test summaries, standard columns as populated by
            extract_df_from_dbt_test_results_json and
            extract_df_from_ge_test_results_csv
        run_id: str
            Current run ID, as found in dot.run_log
        logger: logging object
            Custom logger object

        Returns
        -------
        test_rows: Pandas dataframe
            Test results, one row per test. By default only failing rows,
            but passing rows can be included if
            $SAVE_PASSED_TESTS environment variable is set.
    """
    logger.info("Extracting test rows dataframe ...")

    schema_core, _, conn_core = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"],
        DbParamsConnection["project_core"],
        project_id,
    )
    schema_test, _, conn_test = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"],
        DbParamsConnection["project_test"],
        project_id,
    )

    entity_data = {}
    failing_rows = None
    passing_rows = None
    unique_column_name = None

    # ID columns in order of preference (don't change order). If these appear in test
    # result df, they determine ids
    id_col_names = ["uuid_list", "uuid", "index", "reported_by", "value_field"]

    for _, row in tests_summary.iterrows():
        failed_tests_view = row["failed_tests_view"]
        entity_id = row["entity_id"]
        entity_or_primary_table = get_entity_name_from_id(project_id, row["entity_id"])
        test_id = row["test_id"]
        test_type = row["test_type"]
        column_name = row["column_name"]
        test_status = row["test_status"]
        id_column_name = row.get("id_column_name")
        test_parameters = row["test_parameters"]

        # Get entity data from the DB
        if not entity_or_primary_table in entity_data:
            entity_or_primary_table = entity_or_primary_table.split("_id")[0]
            entity_data[entity_or_primary_table] = pd.read_sql(
                f"SELECT * FROM {schema_core}.{entity_or_primary_table}", conn_core
            )

        entity_df = entity_data[entity_or_primary_table]

        # Get failed tests view data from the DB
        if test_status == "fail":
            test_results_df = pd.read_sql(
                f"SELECT * FROM {schema_test}.{failed_tests_view}", conn_test
            )
            test_results_df_cols = list(test_results_df.columns)
            logger.info(
                "Failed tests for test type "
                + test_type
                + " on entity "
                + entity_or_primary_table
            )
        elif test_status == "error":
            logger.warning(
                "!!!! Test type "
                + test_type
                + " on entity "
                + entity_or_primary_table
                + " did not execute!"
            )
            continue
        else:
            # logger.info("All tests passed for test type " + test_type + " on entity
            # " + entity_or_primary_table)
            continue

        # Interrogate results dataframes to identify unique id field and failing rows
        # TODO: How can we simplify this logic, and better still include in the
        # DB somehow. What's here if not generic for all deployments
        unique_column_name = None
        for c in id_col_names:
            # Special handling for unique test type
            if test_type == "unique":
                unique_column_name = "unique_field"
                failing_ids = entity_df.loc[
                    entity_df[column_name].isin(test_results_df["unique_field"]),
                    # TODO Add 'primary_table_id_field' as a column in entity defintion and use that here
                    column_name,
                ].tolist()
                unique_column_name = column_name
                break
            if test_type == "expect_similar_means_across_reporters":
                tp = json.loads(test_parameters.replace("'", '"'))
                unique_column_name = tp["id_column"]
                failing_ids = entity_df.loc[
                    entity_df[unique_column_name].isin(test_results_df[tp["key"]]),
                    unique_column_name,
                ].tolist()
                break
            if c in test_results_df_cols:
                # If a list of ids, use those
                if c == "uuid_list":
                    if test_type == "custom_sql":
                        unique_column_name = str(
                            test_results_df["primary_table_id_field"].iloc[0]
                        )
                    else:
                        for c2 in id_col_names:
                            if c2 in entity_df.columns:
                                unique_column_name = c2
                                break
                    failing_ids = test_results_df["uuid_list"][0]
                    break
                # Map disallowed values back onto entity rows
                if test_type == "accepted_values":
                    for c2 in id_col_names:
                        if c2 in entity_df.columns:
                            unique_column_name = c2
                            break
                    failing_ids = entity_df.loc[
                        entity_df[column_name].isin(
                            test_results_df.value_field.unique()
                        ),
                        "uuid",
                    ].tolist()
                    break
                # Rest are basic id fields
                if c != column_name:
                    unique_column_name = c
                    failing_ids = test_results_df[unique_column_name].tolist()
                    break

        # Special handling for SQL, we'll use mandatory field 'primary_table_id_field' from query
        if test_type == "custom_sql":
            unique_column_name = str(test_results_df["primary_table_id_field"].iloc[0])
            failing_ids = test_results_df[unique_column_name].tolist()

        # last chance For any test type: if id_column name is set, then use it
        if unique_column_name is None:
            if id_column_name is not None and id_column_name != "":
                unique_column_name = id_column_name
                failing_ids = test_results_df[unique_column_name].tolist()

        # Catch gaps in logic
        if unique_column_name is None:
            logger.info("Unique column name: " + str(unique_column_name))
            logger.info(row)
            logger.info(test_results_df_cols)
            logger.error(
                "Unknown ID column for test_type "
                + test_type
                + " cannot be processed with entity "
                + entity_or_primary_table
                + " which has test view columns: "
                + str(test_results_df_cols)
            )
            sys.exit()

        logger.info(
            "  -- Test type "
            + test_type
            + " on entity "
            + entity_or_primary_table
            + " has id field "
            + unique_column_name
            + " test view:"
            + failed_tests_view
        )

        # Using our list of failing IDs, generate dataframe for failed_test_rows
        try:
            if not isinstance(failing_ids, list):
                failing_ids = [failing_ids]
            passing_ids = entity_df.loc[
                ~entity_df[unique_column_name].isin(failing_ids), unique_column_name
            ].to_list()
        except Exception as e:  # maybe KeyError
            logger.error(
                "Error when getting failing ids from entity_df; unique_column_name: "
                f"{unique_column_name}, "
                f"entity_df.columns: {entity_df.columns}",
                exc_info=True,
            )
            raise e

        test_failing_rows, test_passing_rows = generate_failing_passing_dfs(
            failing_ids,
            passing_ids,
            run_id,
            test_id,
            entity_or_primary_table,
            entity_id,
            failed_tests_view,
            unique_column_name,
        )

        if failing_rows is None:
            failing_rows = test_failing_rows
        else:
            failing_rows = pd.concat([failing_rows, test_failing_rows])

        if passing_rows is None:
            passing_rows = test_passing_rows
        else:
            passing_rows = pd.concat([passing_rows, test_passing_rows])

    # Decide whether to include passing rows
    if os.environ.get("SAVE_PASSED_TESTS") is not None:
        test_rows = pd.concat([passing_rows, failing_rows])
    else:
        test_rows = failing_rows

    return test_rows


def generate_dbt_test_coverage_report(project_id: str, logger: logging.Logger):
    """Generates test coverage report

    Parameters
    ----------
    logger : logger
        Logger
    project_id : str
        Project ID, eg 'Muso'. Must align with project_id in dot.projects

    Returns
    -------
    No variable returns, but does output a report to
    generated_files/{project_id}/dbt_test_coverage_report.txt

    """
    logger.info("======== Generate test coverage report ========")
    with open("dbt/target/run_results.json") as f:
        run_results = json.load(f)

    with open("dbt/target/manifest.json") as f:
        manifest = json.load(f)

    with open(f"generated_files/{project_id}/dbt_test_coverage_report.txt", "w") as f:
        results = json_normalize(run_results["results"])

        # Look for references in manifest
        results["node.refs"] = results.apply(
            lambda row: manifest["nodes"][row.unique_id]["refs"], axis=1
        )

        # Unravel nested list of refs and add tag columns
        results["node.refs.unpacked"] = (
            results["node.refs"].apply(chain.from_iterable).apply(list)
        )
        possible_refs = list(
            set(results["node.refs.unpacked"].apply(lambda x: pd.Series(x)).stack())
        )
        for i in possible_refs:
            results["tag_" + i] = results.apply(
                lambda x: int(i in x["node.refs.unpacked"]), axis=1
            )

        def print_test_results_for_df(df, title=""):
            return {
                "Data Source": title,
                "Total tests run": len(df),
                "Passed": len(df) - len(df.loc[df.status != "pass"]),
                "Failed": len(df.loc[df.status == "fail"]),
                "Warning": len(df.loc[df.status == "warn"]),
                "Error": len(df.loc[df.status == "error"]),
                "Skipped": len(df.loc[df.status == "skip"]),
                "DOT Records": pd.to_numeric(df["failures"], errors="coerce").sum(),
            }
            # "Error" state indicates a problem with the test itself, not that there
            #  were records that passed or failed

        f.write("\n")
        f.write("DOT TEST COVERAGE REPORT\n")
        f.write("\n")
        f.write("----- Summary ----- \n")
        summary = print_test_results_for_df(results)
        [
            f.write("{0}: {1} \n".format(i, summary[i]))
            for i in summary
            if i != "Data Source"
        ]
        f.write("\n")
        list_of_outputs = []
        for i in possible_refs:
            col = "tag_" + i
            list_of_outputs.append(
                print_test_results_for_df(results[results[col] == 1], title=i)
            )

        f.write("----- Details ----- \n")
        output = pd.DataFrame(list_of_outputs)
        output.set_index("Data Source", inplace=True)
        f.write(str(output.sort_values("Total tests run", ascending=False)))
        f.write("\n")

    with open(f"generated_files/{project_id}/dbt_test_coverage_report.txt", "r") as f:
        logger.info(f.read())


def set_summary_stats(
    tests_summary: pd.DataFrame, project_id: str, logger: logging.Logger
):
    """Generates tests summary stats for total, failed and passed test rows

    Parameters
    ----------
    tests_summary : pandas datafram
        Test summary standard dataframe
    project_id : str
        Project ID, eg 'Muso'. Must align with project_id in dot.projects
    logger : logger object
        The logger

    Returns
    -------
    tests_summary : pandas datafram
        Test summary standard dataframe with summary stats columns
    """
    schema_core, _, conn_data = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"],
        DbParamsConnection["project_core"],
        project_id,
    )
    schema_test, _, conn_test = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"],
        DbParamsConnection["project_test"],
        project_id,
    )

    entity_count_map = {}
    entity_count = []
    failed_count = []
    for i, row in tests_summary.iterrows():
        failed_tests_view = row["failed_tests_view"]
        entity_or_primary_table = get_entity_name_from_id(project_id, row["entity_id"])
        test_type = row["test_type"]
        test_status = row["test_status"]

        # Get entity row count
        if not entity_or_primary_table in entity_count_map:
            entity_or_primary_table = entity_or_primary_table.split("_id")[0]
            c = pd.read_sql(
                f"SELECT count(*) FROM {schema_core}.{entity_or_primary_table}",
                conn_data,
            )
            entity_count_map[entity_or_primary_table] = float(c.iloc[0, 0])
        c = entity_count_map[entity_or_primary_table]
        entity_count.append(c)

        # Get failed row count
        if test_status == "fail":
            df = pd.read_sql(
                f"SELECT * FROM {schema_test}.{failed_tests_view}", conn_test
            )
            # Some test views have one row, where they provide a list of failing uuids
            if "uuid_list" in df.columns.values and df.shape[0] == 1:
                c = len(list(df.iloc[0, 0]))
            else:
                c = df.shape[0]
        else:
            c = 0
        failed_count.append(c)

    tests_summary["rows_total"] = entity_count
    tests_summary["rows_failed"] = failed_count

    tests_summary["rows_passed"] = tests_summary.apply(
        lambda x: x["rows_total"] - x["rows_failed"]
        if x["test_status"] in ["fail", "pass"]
        else 0,
        axis=1,
    )

    return tests_summary


def get_entity_id_from_name(project_id: str, entity_name: str) -> str:
    """
    Gets entity name from entity_id

    Parameters
    ----------
    project_id

    entity_name e.g. dot_model__ancview_delivery

    Returns
    -------

    """
    schema_dot, _, conn_dot = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"], DbParamsConnection["dot"], project_id
    )

    query = f"""
        SELECT
            entity_id
        FROM
            {schema_dot}.configured_entities
        WHERE
            entity_name = '{entity_name.replace(dot_model_PREFIX, "")}'
    """
    return _get_entity(conn_dot, query)


def get_entity_name_from_id(project_id: str, entity_id: str) -> str:
    """
    Gets entity name from entity_id

    Parameters
    ----------
    project_id

    entity_name e.g. dot_model__ancview_delivery

    Returns
    -------

    """
    schema_dot, _, conn_dot = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"], DbParamsConnection["dot"], project_id
    )

    query = f"""
        SELECT
            entity_name
        FROM
            {schema_dot}.configured_entities
        WHERE
            entity_id = '{entity_id}'
    """
    return f"{dot_model_PREFIX}{_get_entity(conn_dot, query)}"


def _get_entity(conn_dot: pg.extensions.connection, query: str) -> str:
    """
    Gets entity name from entity_id

    Parameters
    ----------
    project_id

    entity_name e.g. dot_model__ancview_delivery

    Returns
    -------

    """
    entity_ids = pd.read_sql(query, conn_dot)
    if entity_ids.empty:
        raise ReferenceError(f"entity_ids not found in db with query {query}")
    if entity_ids.shape[0] != 1:
        raise ReferenceError(f"more than 1 entity_ids found in db with query {query}")
    return entity_ids.iloc[0, 0]
