"""Contains code to generate .yml, .sql and .json configuration files for dbt
and great expectations, using data stored in database table dot.configured_tests
"""
#%%
import json
import os
import logging
import re
import yaml
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from utils.connection_utils import add_ge_schema_parameters, get_db_params_from_config
from utils.configuration_utils import (
    DbParamsConfigFile,
    DbParamsConnection,
    get_dbt_config_model_paths,
    get_dbt_config_test_paths,
    DBT_PROJECT_FINAL_FILENAME,
    GE_BATCH_CONFIG_FINAL_FILENAME,
    dot_config_FILENAME,
    DBT_PROFILES_FINAL_FILENAME,
    GE_GREAT_EXPECTATIONS_FINAL_FILENAME,
    GE_CONFIG_VARIABLES_FINAL_FILENAME,
)
from utils.dbt import create_core_entities
from utils.utils import get_entity_name_from_id

# %%


def create_project_directories(project_id, logger=logging.Logger):
    """Function to generate project_directories if they don't exist. Creates ...

     |dot
      | | config
      | | |<project_id>
      | | | | dbt
      | | | | ge
      | |dbt
      | | |models
      | | | |<project_id>
      | | | | |core
      | | | | |test
      | | |tests
      | | | |<project_id>
      | |great_expectations
      | | |expectations
      | | | |<project_id>

    Parameters
    ----------
    project_id : str
        Project id as found in dot.project_id, eg 'Muso'
    logger: Logger object
        Used for passing in logger object

    """

    dirs = [
        f"./config/{project_id}",
        f"./config/{project_id}/dbt",
        f"./config/{project_id}/ge",
        "./dbt/core/models",
        f"./dbt/core/models/{project_id}",
        f"./dbt/core/models/{project_id}/core",
        f"./dbt/core/models/{project_id}/test",
        "./dbt/core/tests",
        f"./dbt/core/tests/{project_id}",
        "./great_expectations/expectations",
        f"./great_expectations/expectations/{project_id}",
    ]

    # Create any missing folder
    for d in dirs:
        if not os.path.exists(d):
            logger.info(f"Creating project directory {d}")
            os.makedirs(d)


def extract_dbt_config_env_variable(dbt_setting: dict) -> str:
    """Takes a dbt config file and replaces any environment variable syntax with the
    environment variable. Syntax looks like this ...

    pass: "{{ env_var('POSTGRES_PASSWORD') }}"

     Parameters
     ----------
     dbt_setting : dict
         credentials dictionary
     Returns
     -------
     val : str
         The environment variable value

    """
    val = dbt_setting
    if "env_var" in dbt_setting:
        env_variable = re.search(r"env_var\(\'(.*?)\'\)", dbt_setting).group(1)
        return os.getenv(env_variable)
    return val


def write_config_from_template(
    environment, template_name, output_file, logger, **kwargs
):
    """
    Writes a config file from a template
    """
    logger.info(
        f"Using template {template_name} and writing to config file {output_file} ..."
    )
    template = environment.get_template(template_name)
    content = template.render(**kwargs)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, mode="w", encoding="utf-8") as f:
        f.write(content)
        logger.info(f"   Wrote {output_file}")

def generate_master_config_files(project_id, logger=logging.Logger):

    """Function to generate master configuration files using the entries in
     config/dot_config.yml and also to set up required output directories (per project)

    Parameters
    ----------
    project_id : str
        Project id as found in dot.project_id, eg 'Muso'
    logger: Logger object
        Used for passing in logger object

    Returns
    -------

     no function returns but will output config files as follows:

     |____config
          | |____<project_name>
          | | |____dbt
          | | | |____profiles.yml
          | | | |____dbt_project.yml
          | | |____ge
          | | | |____great_expectations.yml
          | | | |____config_variables.yml
          | | | |____batch_config.json
    """

    with open(dot_config_FILENAME) as f:
        dot_config = yaml.load(f, Loader=yaml.FullLoader)
        output_schema_suffix = dot_config.get("dot", {}).get("output_schema_suffix")

    with open(dot_config_FILENAME) as f:
        project_db_config = yaml.load(f, Loader=yaml.FullLoader)
        project_db_config = project_db_config[f"{project_id}_db"]

    # Load Jinja configuration file templates
    environment = Environment(loader=FileSystemLoader("./config/templates/"))

    # DBT: Create DBT Project yaml
    template_name = "dbt/dbt_project.yml"
    # output_file = f"./config/{project_id}/dbt/dbt_project.yml"
    output_file = DBT_PROJECT_FINAL_FILENAME
    write_config_from_template(
        environment, template_name, output_file, logger, project_id=project_id
    )
    if output_schema_suffix:
        config_file_text = "\n".join(
            [
                "",
                "models:",
                "    dbt_model_1:",
                "        core:",
                f"            +schema: '{output_schema_suffix}'",
                "        test:",
                f"            +schema: '{output_schema_suffix}'",
            ]
        )
    with open(output_file, "a") as f:
        f.write(config_file_text)

    # DBT: Create profiles yaml
    template_name = "dbt/profiles.yml"
    # output_file = f"./config/{project_id}/dbt/profiles.yml"
    output_file = DBT_PROFILES_FINAL_FILENAME
    write_config_from_template(
        environment,
        template_name,
        output_file,
        logger,
        host=project_db_config["host"],
        user=project_db_config["user"],
        password=extract_dbt_config_env_variable(project_db_config["pass"]),
        port=project_db_config["port"],
        dbname=project_db_config["dbname"],
        schema=project_db_config["schema"],
    )

    # GE: Great expectations yaml
    template_name = "great_expectations/great_expectations.yml"
    # output_file = f"./config/{project_id}/ge/great_expectations.yml"
    output_file = GE_GREAT_EXPECTATIONS_FINAL_FILENAME
    write_config_from_template(
        environment, template_name, output_file, logger, project_id=project_id
    )

    # GE: Batch config JSON
    template_name = "great_expectations/batch_config.json"
    # output_file = f"./config/{project_id}/ge/batch_config.json"
    output_file = GE_BATCH_CONFIG_FINAL_FILENAME
    # No variables to update, but using same mechanism for consistency
    write_config_from_template(environment, template_name, output_file, logger)

    # GE: Config variables yaml
    template_name = "great_expectations/config_variables.yml"
    # output_file = f"./config/{project_id}/ge/config_variables.yml"
    output_file = GE_CONFIG_VARIABLES_FINAL_FILENAME
    write_config_from_template(
        environment,
        template_name,
        output_file,
        logger,
        project_db_host=project_db_config["host"],
        project_db_username=project_db_config["user"],
        project_db_password=extract_dbt_config_env_variable(project_db_config["pass"]),
        project_db_port=project_db_config["port"],
        project_db_database=project_db_config["dbname"],
    )


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
    # dbt setup project-dependent "dbt_project.yml"
    with open(DBT_PROJECT_FINAL_FILENAME) as f:
        dbt_config = yaml.load(f, Loader=yaml.FullLoader)

    # dbt directories
    model_dir = f"./dbt/{get_dbt_config_model_paths(dbt_config)}/core"
    tests_dir = f"./dbt/{get_dbt_config_test_paths(dbt_config)}"

    # GE batch config
    with open(GE_BATCH_CONFIG_FINAL_FILENAME) as f:
        ge_batch_config = json.load(f)

    # GE directories
    ge_dir = f"./great_expectations/expectations/{project_id}"
    ge_test_suite_name = ge_batch_config["expectation_suite_name"]

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
        project_id=project_id,
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
    os.makedirs(os.path.dirname(tests_dir + "/test.txt"), exist_ok=True)
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
        # Note that here a version is pinned, it is also pinned in ge_test.json,
        # so it will have to be updated if the version changes
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

    os.makedirs(os.path.dirname(ge_dir + "/test.txt"), exist_ok=True)
    for f in os.listdir(ge_dir):
        if ".json" in f:
            os.remove(os.path.join(ge_dir, f))

    logger.info("Writing GE test suite: " + ge_test_suite_name)
    with open(ge_test_suite_file, "w") as f:
        json.dump(ge_test_file, f, indent=2)

    return dot_tests
