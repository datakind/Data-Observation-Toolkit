import logging
import json
import ast
import traceback
import great_expectations as ge
import pandas as pd
import yaml

from utils.utils import get_test_id, get_entity_id_from_name
from utils.connection_utils import (
    update_db_config_from_os,
    get_db_params_from_config,
    remove_ge_schema_parameters,
)
from utils.configuration_utils import (
    DbParamsConfigFile,
    DbParamsConnection,
    GE_GREAT_EXPECTATIONS_FINAL_FILENAME,
    GE_BATCH_CONFIG_FINAL_FILENAME,
)
from psycopg2 import sql
from pandas import json_normalize


class GEException(Exception):
    """Exception in great expectations"""


def run_ge_tests(project_id: str, logger: logging.Logger):
    """Runs Great Expectations tests

    Parameters
    ----------
    logger : logger
        Logger
    project_id : str
        Project ID, eg 'Muso'. Must align with project_id in dot.projects
    """
    logger.info("======== Running Great Expectations tests ========")

    with open(GE_BATCH_CONFIG_FINAL_FILENAME, "r") as opened:
        config = json.load(opened)

    with open(GE_GREAT_EXPECTATIONS_FINAL_FILENAME, "r") as opened:
        ge_config = yaml.safe_load(opened)
        db_config_path = "great_expectations/" + ge_config["config_variables_file_path"]

    with open(
        db_config_path, "r"
    ) as opened:  # Assumes the credentials are stored in a local file
        db_config = yaml.safe_load(opened)[config["datasource_name"]]

    db_config = update_db_config_from_os(db_config.copy())

    # The batch_config json file specifies three things:
    # 1. The datasource, as configured in great_expectations.yml
    # 2. The name of the expectation suite that holds the expectations
    # 3. A table you want as an entry point for generating a dataset,
    #    or a query for ganerating that same dataset
    # Note: Ideally, our expectations would take in a table name as an argument
    # and would not rely on the table/query chosen here. Great Expectations,
    # however,always genarates a dataset, since the class we are using for our
    # custom validations extends from `SqlAlchemyDataset`

    # Uses configuration to create a validation batch and runs an expectation
    # suite on it
    context = ge.data_context.DataContext()
    batch_kwargs = {
        "query": config["query"],
        "datasource": config["datasource_name"],
    }
    batch = context.get_batch(batch_kwargs, config["expectation_suite_name"])

    # TODO use checkpoint instead of validation_operator to adapt to GE 0.13
    # result: CheckpointResult = context.run_checkpoint(
    #     checkpoint_name="dot_checkpoint",
    #     batch_request=None,
    #     run_name=None,
    # )
    results = context.run_validation_operator(
        "action_list_operator",
        assets_to_validate=[batch],
    )

    results = parse_results(results)
    view_sql = create_views(project_id, results, db_config)
    if view_sql:
        results["failed_tests_view_sql"] = view_sql
    results.to_csv(f"generated_files/{project_id}/ge_clean_results.csv", index=False)


def parse_unexpected_list(unexpected):
    """Converts a pandas Series or a string representation into a list, or pass on the
    list if it already was one. This is to make sure we can read the results from both
    a file or in-memory directly from Great Expectations.

    Parameters
    ----------
        unexpected: Pandas series or string
           Input series or string to convert
    Return
    ------
        values: list
           List of values
    """

    if isinstance(unexpected, str):
        values = ast.literal_eval(unexpected)
    elif isinstance(unexpected, list):
        values = unexpected
    elif isinstance(unexpected, pd.Series):
        values = unexpected.to_list()
    else:
        values = []
    return values


def create_views(project_id, results, db_config):
    """Creates a failed tests view for Great Expectations tests

    Parameters
    ----------
        project_id: str
           Current run project ID
        results: Pandas series or string
           Great expectations results dataframe
        db_config: dict
           enum for dbt_project.yml config file
    Return
    ------
        view_sql: str
           SQL for the view
    Will also create a DB view
    """
    schema_test, _, connection = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"],
        DbParamsConnection["project_test"],
        project_id,
    )
    schema_core, _, _ = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"],
        DbParamsConnection["project_core"],
        project_id,
    )

    cursor = connection.cursor()

    view_sql = []

    for _, result in results.iterrows():
        try:
            if result["error"]:
                print(
                    f"Failed to execute {result['expectation_config.expectation_type']}"
                )
                print(result["exception_info.exception_message"])
                continue
            if result["fail"]:
                source_table = result["result.table"]
                source_column = result["result.id_column"]
                if result["result.short_name"].startswith("chv_"):
                    name = f"chv_tr_{result['result.short_name'][4:]}"
                else:
                    name = f"tr_{result['result.short_name']}"

                raw_values = result["result.unexpected_list"]
                values = parse_unexpected_list(raw_values)

                # Weird super slowdown if using "create or replace view" as opposing
                # to dropping view first
                query_drop = sql.SQL("drop view if exists {name}").format(
                    name=sql.Identifier(schema_test, name)
                )
                cursor.execute(query_drop)
                connection.commit()

                query_create = sql.SQL(
                    "create view {name} as select * from {source_table} "
                    "inner join unnest(%s) as failed "
                    "on failed={source_table}.{source_column}"
                ).format(
                    name=sql.Identifier(schema_test, name),
                    source_table=sql.Identifier(schema_core, source_table),
                    source_column=sql.Identifier(source_column),
                )
                cursor.execute(query_create, (values,))
                connection.commit()
                print(f"Created view at {name} with {len(values)} rows")
                view_sql.append(query_create)
        except GEException:
            traceback.print_exc()
            continue

    connection.close()
    return view_sql


def parse_results(results):
    """Creates a csv file parsed from great expectations results json object

    Parameters
    ----------
       results: Pandas dataframe

    Returns
    -------
       results: Pandas dataframe
    """

    for key in results["run_results"]:
        actual_results = results["run_results"][key]["validation_result"]["results"]

    results = [result.to_json_dict() for result in actual_results]

    test_params = []
    for r in results:
        t = r["expectation_config"]["kwargs"]
        del t["result_format"]
        test_params.append(t)

    results = json_normalize(results)

    results["fail"] = ~results["success"]
    results["error"] = results["exception_info.raised_exception"]
    results["status"] = (
        results["result.unexpected_list"].apply(lambda x: len(parse_unexpected_list(x)))
        if "result.unexpected_list" in results.columns
        else "pass"
    )
    results["warn"] = False  # because we don't have that concept yet
    results["skip"] = False  # we also don't ever skip expectations yet
    results["test_parameters"] = [
        str(item) for item in remove_ge_schema_parameters(test_params)
    ]

    return results


def extract_df_from_ge_test_results_csv(run_id, project_id, logger):
    """Function to parse GE csv results file (that was created by parse_results) to
    form a test_summaries standard dataframe.

       Parameters
       ----------
          run_id: str
             Current run ID as found in dot.run_log
          project_id: str
             Current run project ID
          logger: Logging object
             Custom logging object

       Returns
       -------
          ge_tests_summary: Pandas dataframe
             Standard tests summary dataframe, same columns as returned by
             extract_df_from_dbt_test_results_json

    """

    logger.info("Extracting GE test summary dataframe ...")

    ge_tests_summary = pd.read_csv(f"generated_files/{project_id}/ge_clean_results.csv")
    ge_tests_summary["run_id"] = run_id
    ge_tests_summary.rename(
        columns={"expectation_config.kwargs.quantity": "column_name"}, inplace=True
    )
    ge_tests_summary.rename(
        columns={"expectation_config.expectation_type": "test_type"}, inplace=True
    )
    ge_tests_summary.rename(
        columns={"expectation_config.kwargs.data_table": "entity"}, inplace=True
    )
    ge_tests_summary.rename(
        columns={"exception_info.exception_message": "test_status_message"},
        inplace=True,
    )
    ge_tests_summary["entity_id"] = ge_tests_summary.apply(
        lambda x: get_entity_id_from_name(project_id, x["entity"]),
        axis=1,
    )
    ge_tests_summary["test_id"] = ge_tests_summary.apply(
        lambda x: get_test_id(
            x["test_type"],
            x["entity_id"],
            x["column_name"],
            project_id,
            x["test_parameters"],
        ),
        axis=1,
    )
    ge_tests_summary["test_status"] = ge_tests_summary["fail"].apply(
        lambda x: "fail" if x is True else "pass"
    )
    ge_tests_summary["test_status"] = ge_tests_summary.apply(
        lambda x: "error" if x["error"] is True else x["test_status"], axis=1
    )
    ge_tests_summary.rename(
        columns={"result.short_name": "failed_tests_view"}, inplace=True
    )
    if "failed_tests_view" in ge_tests_summary.columns:
        ge_tests_summary["failed_tests_view"] = ge_tests_summary[
            "failed_tests_view"
        ].apply(lambda x: f"chv_tr_{x[4:]}" if x.startswith("chv_") else x)
    else:
        ge_tests_summary["failed_tests_view"] = None

    ge_tests_summary = ge_tests_summary[
        [
            "run_id",
            "test_id",
            "entity_id",
            "test_type",
            "column_name",
            "test_status",
            "test_status_message",
            "test_parameters",
            "failed_tests_view",
        ]
    ]
    ge_tests_summary.set_index("test_id")

    return ge_tests_summary
