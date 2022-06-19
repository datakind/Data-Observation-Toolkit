"""Contains code to generate .yml, .sql and .json configuration files for dbt
and great expectations, using data stored in database table dot.configured_tests
"""
#%%
import json
import os
import logging
import yaml
import pandas as pd
from utils.connection_utils import add_ge_schema_parameters, get_db_params_from_config
from utils.configuration_utils import (
    load_credentials,
    DbParamsConfigFile,
    DbParamsConnection,
    create_profiles_yaml,
    create_dbt_project_yaml,
    create_great_expectations_yaml,
    create_batch_config_json,
    create_config_variables_yaml,
    get_dbt_config_model_paths,
    get_dbt_config_test_paths,
    DBT_PROJECT_FINAL_FILENAME,
    GE_BATCH_CONFIG_FINAL_FILENAME,
)
from utils.dbt import create_core_entities
from utils.utils import get_entity_name_from_id

# %%


def generate_tests_from_db(project_id, logger=logging.Logger):
    """Function to generate dbt test yml files and Great Expectation .json files based
    on the contents of database table dot.configured_tests.

      Parameters
      ----------
      project_id : str
          Project id as found in dot.project_id, eg 'Muso'
      logger: Logger object
          Used for passing in logger object

      Returns
      -------
      tests : dataframe
          The tests configured for the project being run, as found in
          dot.configured_tests

      Will also output files as following:
      - dbt: ./models/core/*.yml; ./tests/*.sql
      - Great expectations: ./great_expectations/expectations/*.json
    """
    # ======================== Set config & output directories =========================
    # read dot_config for project credentials
    db_credentials_project = load_credentials(project_id, DbParamsConnection["project"])

    create_dbt_project_yaml(project_id)
    create_profiles_yaml(project_id, db_credentials_project)
    create_great_expectations_yaml(project_id)
    create_batch_config_json(project_id)
    create_config_variables_yaml(project_id, db_credentials_project)

    # dbt setup project-dependent "dbt_project.yml"
    with open(DBT_PROJECT_FINAL_FILENAME) as f:
        dbt_config = yaml.load(f, Loader=yaml.FullLoader)

    # dbt directories
    model_dir = f"./dbt/{get_dbt_config_model_paths(dbt_config)}/core"
    tests_dir = f"./dbt/{get_dbt_config_test_paths(dbt_config)}"
    fail_tests_dir = f"./dbt/{get_dbt_config_model_paths(dbt_config)}/test"

    # GE batch config
    with open(GE_BATCH_CONFIG_FINAL_FILENAME) as f:
        ge_batch_config = json.load(f)

    # G GE directories
    ge_dir = f"./great_expectations/expectations/{project_id}"
    ge_test_suite_name = ge_batch_config["expectation_suite_name"]

    # create any missing folder
    for d in [model_dir, tests_dir, fail_tests_dir, ge_dir]:
        if not os.path.exists(d):
            os.makedirs(d)

    # connections & schemas
    schema_dot, _, conn_dot = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"],
        DbParamsConnection["dot"],
        project_id,
    )
    schema_project, _, _ = get_db_params_from_config(
        DbParamsConfigFile["dot_config.yml"],
        DbParamsConnection["project"],
        project_id,
    )

    # put SQL of entities into project-dependent path
    create_core_entities(
        schema_dot=schema_dot,
        conn=conn_dot,
        schema_project=schema_project,
        output_path=model_dir,
        logger=logger,
    )

    # GE additional setup
    ge_test_suite_file = os.path.join(ge_dir, ge_test_suite_name + ".json")

    # =========================== Extract tests configured in DB =======================
    query = """
                SELECT
                    tt.library,
                    ct.*
                FROM
                    {schema}.configured_tests ct,
                    {schema}.test_types tt
                WHERE
                    test_activated=TRUE AND
                    project_id='{project_id}' AND
                    ct.test_type = tt.test_type
            """.format(
        schema=schema_dot, project_id=project_id
    )
    dot_tests = pd.read_sql(query, conn_dot)

    # ========================== Generate schema test yaml files =======================

    # Dictionary we will build in yaml format
    config_options = {}

    dbt_schema_tests = dot_tests.loc[
        (dot_tests["test_type"] != "custom_sql") & (dot_tests["library"] == "dbt")
    ]
    dbt_non_schema_tests = dot_tests.loc[
        (dot_tests["test_type"] == "custom_sql") & (dot_tests["library"] == "dbt")
    ]
    ge_schema_tests = dot_tests.loc[dot_tests["library"] == "great_expectations"]

    # Parse schema tests to generate yaml format
    logger.info("Generating schema DBT test files ...")
    for entity_id in dbt_schema_tests["entity_id"].unique():
        entity_name = get_entity_name_from_id(project_id, entity_id)
        if (
            entity_name not in config_options.keys()
        ):  # pylint: disable=consider-iterating-dictionary
            config_options[entity_id] = {"name": entity_name, "columns": {}}

        # Loop through tests for this entity
        df = dbt_schema_tests.loc[dot_tests["entity_id"] == entity_id]
        for index, row in df.iterrows():
            column_name = row["column_name"]
            description = row["description"]
            test_type = row["test_type"]
            test_parameters = row["test_parameters"]

            # if test_parameters != None:
            #    test_parameters = "| ".join([f"{k}={test_parameters[k]}" for k in test_parameters])
            # else:
            #    test_parameters = ""

            # Update 'tests' node for this entity with non column-specific tests
            if column_name in (None, ""):
                if "tests" not in config_options[entity_id]:
                    config_options[entity_id]["tests"] = []
                if test_parameters not in ("", None):
                    test = {test_type: test_parameters}
                    config_options[entity_id]["tests"].append(test)

            # Update 'columns' node for this entity with column-specific tests
            else:
                if column_name not in config_options[entity_id]["columns"]:
                    config_options[entity_id]["columns"][column_name] = {
                        "name": column_name
                    }
                if description != "":
                    config_options[entity_id]["columns"][column_name][
                        "description"
                    ] = description
                if "tests" not in config_options[entity_id]["columns"][column_name]:
                    config_options[entity_id]["columns"][column_name]["tests"] = []
                if test_parameters not in ("", None):
                    test = {test_type: test_parameters}
                    config_options[entity_id]["columns"][column_name]["tests"].append(
                        test
                    )
                else:
                    config_options[entity_id]["columns"][column_name]["tests"].append(
                        test_type
                    )

        # Convert columns dictionary to a list so dbt is happy
        cols = config_options[entity_id]["columns"]
        config_options[entity_id]["columns"] = []
        for c in cols:
            config_options[entity_id]["columns"].append(cols[c])

    # print(yaml.safe_dump(config_options, default_flow_style=False, sort_keys=False,
    # indent=4))

    # Using our dictionary, dump to individual yaml files in DBT format
    for f in os.listdir(model_dir):
        if ".yml" in f:
            os.remove(os.path.join(model_dir, f))

    for entity_id in dbt_schema_tests["entity_id"].unique():
        cfg = {"version": 2, "models": []}
        cfg["models"].append(config_options[entity_id])
        yaml_content = yaml.safe_dump(
            cfg, default_flow_style=False, sort_keys=False, indent=4
        )
        entity_name = get_entity_name_from_id(project_id, entity_id)
        output_file = model_dir + "/" + entity_name + ".yml"
        logger.info("Writing schema test file: " + output_file)
        with open(output_file, "w") as f:
            f.write(yaml_content)

    # ================= Generate non-schema test custom SQL files for DBT===============

    # Now, let's generate the non-schema custom_sql test files
    logger.info("Generating non-schema custom sql DBT test files ...")
    for f in os.listdir(tests_dir):
        if ".sql" in f:
            os.remove(os.path.join(tests_dir, f))

    for entity_id in dbt_non_schema_tests["entity_id"].unique():
        df = dbt_non_schema_tests.loc[dot_tests["entity_id"] == entity_id]
        for index, row in df.iterrows():
            test_type = row["test_type"]
            custom_sql = row["test_parameters"]["query"]
            entity_name = get_entity_name_from_id(project_id, entity_id)
            output_file = tests_dir + "/" + entity_name + "_id" + str(index) + ".sql"
            logger.info("Writing custom sql test file: " + output_file)
            with open(output_file, "w") as f:
                f.write(custom_sql)

    # ================= Generate GE files ============================
    logger.info("Generating Great Expectations test files ...")

    ge_test_file = {
        "data_asset_type": "CustomSqlAlchemyDataset",
        "expectation_suite_name": ge_test_suite_name,
        "expectations": [],
        # Note that here a version is pinned, it is also pinned in ge_test.json, so it will have to be updated if the
        # version changes
        "meta": {"great_expectations.__version__": "0.10.12"},
    }

    # Loop through tests for GE
    for entity_id in ge_schema_tests["entity_id"].unique():

        # Loop through tests for this entity
        df = ge_schema_tests.loc[dot_tests["entity_id"] == entity_id]
        for index, row in df.iterrows():
            expectation = {
                "expectation_type": row["test_type"],
                # additional parameters to expectations, not controlled by test config
                # "kwargs": add_ge_schema_parameters(
                #    json.loads(row["test_parameters"]), project_id
                # ),
                "kwargs": add_ge_schema_parameters(row["test_parameters"], project_id),
                "meta": {},
            }

            ge_test_file["expectations"].append(expectation)

    for f in os.listdir(ge_dir):
        if ".json" in f:
            os.remove(os.path.join(ge_dir, f))

    logger.info("Writing GE test suite: " + ge_test_suite_name)
    with open(ge_test_suite_file, "w") as f:
        json.dump(ge_test_file, f, indent=2)

    return dot_tests
