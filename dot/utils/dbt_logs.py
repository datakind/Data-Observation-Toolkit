"""
Utility functions for dbt that read results from logs (i.e. dbt `target`
 directory) thus may have to be changed when upgrading dbt versions
"""
import json
from dataclasses import dataclass
from utils.configuration_utils import (
    _get_filename_safely,
)
from utils.configuration_utils import (
    get_dbt_config_test_paths,
)
from utils.utils import (
    get_short_test_name,
)


@dataclass
class DbtOutputProcessedRow:
    unique_id: str
    test_type: str
    test_status: str
    test_message: str
    column_name: str
    entity_name: str
    test_parameters: str
    short_test_name: str


def read_dbt_output_files(target_path: str, suffix: str = "archive") -> dict:
    """
    Read generated json files. Assumes the cleanup has run and most recent
    results are in _archive files
    TODO maybe dbt output _test.json is not needed

    Parameters
    ----------
    target_path: str
        path of the dbt output dir (called target)
    suffix: str
        suffix to the dbt output files ("archive", copy of these files in a prev step)

    Returns
    -------
      json
         the structure corresponds to dbt logs
    """
    filename = _get_filename_safely(f"{target_path}/run_results_{suffix}.json")
    with open(filename) as f:
        dbt_results = json.load(f)
    # Manifest, see https://docs.getdbt.com/reference/artifacts/manifest-json
    filename = _get_filename_safely(f"{target_path}/manifest_{suffix}.json")
    with open(filename) as f:
        manifest = json.load(f)
    return [
        {**i, **{"node": manifest["nodes"][i["unique_id"]]}}
        for i in dbt_results["results"]
    ]


def get_test_parameters(node: dict, test_type: str) -> str:
    """
    Figures out test parameters from the dbt logs

    Parameters
    ----------
    node: dict
        json from dbt manifest corresponding to a test
    test_type: str
        test type e.g. "not_null", "custom_sql"

    Returns
    -------
      str
         string for the structure of test parameters
    """
    if test_type == "custom_sql":
        # Custom sql (dbt/tests/*.sql) tests do not have the same structure
        # and we have to get SQL from file
        with open("dbt/" + node["original_file_path"]) as f:
            return f.read()

    test_parameters = node.get("test_metadata", {}).get("kwargs", {})

    # TODO figure out why and for which test types this is needed
    if "model" in test_parameters:
        del test_parameters["model"]
    if "column_name" in test_parameters:
        del test_parameters["column_name"]

    # Where clauses live under the config node
    where_clause = node.get("config", {}).get("where", {})
    if where_clause is not None:
        test_parameters["where"] = where_clause

    return str(test_parameters)


def get_test_type(node):
    """
    Figures out test type from the dbt logs

    Parameters
    ----------
    node: dict
        json from dbt manifest corresponding to a test

    Returns
    -------
      str
         string for the test type
    """
    test_type = node.get("test_metadata", {}).get("name")
    if test_type is None:
        # Custom sql (dbt/tests/*.sql) tests do not have the same structure
        if f"{get_dbt_config_test_paths()}/" in node.get("original_file_path", ""):
            test_type = "custom_sql"
    return test_type


def process_dbt_result_row(row: dict) -> dict:
    """
    Figures out parameters from each of the tests of the dbt output rows

    Parameters
    ----------
    row: dict
        json from dbt logs & manifest corresponding to a test

    Returns
    -------
      str
         string for the test type
    """
    unique_id = row["unique_id"]
    node = row["node"]
    test_type = get_test_type(node)
    test_status = row["status"].lower()
    test_message = row["message"].lower() if row["message"] else ""

    column_name = node.get("column_name")
    entity_name = node["original_file_path"].split("/")[-1].split(".")[0]

    test_parameters = get_test_parameters(node, test_type)

    # For custom sql tests the view name has "id_XX" at the end, needs to be stripped
    entity_name = entity_name.split("_id")[0]

    _, short_test_name = get_short_test_name(node)

    return DbtOutputProcessedRow(
        unique_id,
        test_type,
        test_status,
        test_message,
        column_name,
        entity_name,
        test_parameters,
        short_test_name,
    )
