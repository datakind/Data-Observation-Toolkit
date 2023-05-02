""" Configuration utils """

import os
import re
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional
import yaml

DbParamsConfigFile = Enum("DbParamsConfigFile", "dot_config.yml")
DbParamsConnection = Enum("DbParamsConnection", "dot project project_test project_core")

dot_config_FILENAME = "./config/dot_config.yml"
DBT_PROJECT_FINAL_FILENAME = "./dbt/dbt_project.yml"
DBT_PROFILES_FINAL_FILENAME = f"{Path.home()}/.dbt/profiles.yml"
GE_GREAT_EXPECTATIONS_FINAL_FILENAME = "./great_expectations/great_expectations.yml"
GE_BATCH_CONFIG_FINAL_FILENAME = "./great_expectations/batch_config.json"
GE_CONFIG_VARIABLES_FINAL_FILENAME = (
    "./great_expectations/uncommitted/config_variables.yml"
)
DBT_MODELNAME_PREFIX = "dot_model__"

DBT_PROJECT_SEPARATOR = "/"


def _get_filename_safely(path: str) -> str:
    """
    Internal function - checks if the path exists

        Parameters
        ----------
        path : str
            path of the file
        Returns
        -------
        path : str
            path of the file
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Cannot find file {path}")
    return path


def _get_credentials(
    db_config: dict, project_id: str, connection_params: DbParamsConnection
) -> dict:
    """
    Internal function - gets credentials either for the project or the DOT

        Parameters
        ----------
        db_config : dict
            dictionary containing all credentials (from dot_config.yml)
        project_id : str
            Project id as found in dot.project_id, eg 'Muso'
        connection_params : DbParamsConnection
            Enum for DOT vs project db connection
        Returns
        -------
        path : str
            path of the file
    """
    key = connection_params.name
    if connection_params in [
        DbParamsConnection["project"],
        DbParamsConnection["project_test"],
        DbParamsConnection["project_core"],
    ]:
        key = project_id
    if (db_config is None) or (f"{key}_db" not in db_config.keys()):
        raise Exception(
            f"review malformed config at dot_config.yml; content of file as follows '{db_config}'"
        )
    creds = db_config[f"{key}_db"]

    if connection_params in [
        DbParamsConnection["project_test"],
        DbParamsConnection["project_core"],
    ]:
        # add schema suffix, if present
        schema_suffix = get_dbt_config_custom_schema_output_objects()
        if schema_suffix:
            creds["schema"] = "_".join(
                [
                    creds["schema"],
                    schema_suffix,
                ]
            )
    return creds


def load_credentials(project_id: str, connection_params: DbParamsConnection) -> dict:
    """
    Loads credentials and transforms password for project id and connection

          Parameters
          ----------
              project_id : str
                  Project ID, eg 'Muso'. Must align with project_id in dot.projects
              connection_params : DbParamsConnection
                  enum type
    """
    db_config = load_config_file()

    db_credentials = _get_credentials(db_config, project_id, connection_params)

    # Support dbt environment variable format
    db_credentials["pass"] = extract_dbt_config_env_variable(db_credentials["pass"])
    return db_credentials


def load_config_file():
    """
    Reads config file safely

    Returns
    -------
    config: str
        content of config file
    """
    with open(_get_filename_safely(dot_config_FILENAME)) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


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


def get_dbt_config_original_model_paths(dbt_config: Optional[dict] = None) -> str:
    """
    Gets original (i.e. project_independent) path of `model-paths` (i.e. where DBT
    models are located) from dbt_project.yml config file items

          Parameters
          ----------
              dbt_config : Optional[dict]
                  dbt_project.yml config file
          Returns
          -------
              path : str
                  e.g. models
    """
    return _get_dbt_config_original_path("model-paths", dbt_config)


def get_dbt_config_original_test_paths(dbt_config: Optional[dict] = None) -> str:
    """
    Gets original (i.e. project_independent) path of `test-paths` (i.e. where DBT
    tests are located) from dbt_project.yml config file items

          Parameters
          ----------
              dbt_config : Optional[dict]
                  dbt_project.yml config file
          Returns
          -------
              path : str
                  e.g. tests
    """
    return _get_dbt_config_original_path("test-paths", dbt_config)


def get_dbt_config_model_paths(dbt_config: Optional[dict] = None) -> str:
    """
    Gets project-dependent path of `models-paths` (i.e. where DBT models are located)
    from dbt_project.yml config file items

          Parameters
          ----------
              dbt_config : Optional[dict]
                  dbt_project.yml config file
          Returns
          -------
              path : str
                  e.g. models_Muso
    """
    return _get_dbt_config_key("model-paths", dbt_config)


def get_dbt_config_test_paths(dbt_config: Optional[dict] = None) -> str:
    """
    Gets project-dependent path of `tests-paths` (i.e. where DBT tests are located)
    from dbt_project.yml config file items

          Parameters
          ----------
              dbt_config : Optional[dict]
                  dbt_project.yml config file
          Returns
          -------
              path : str
                  e.g. tests_Muso
    """
    return _get_dbt_config_key("test-paths", dbt_config)


def _get_dbt_config_key(key: str, dbt_config: Optional[dict] = None) -> str:
    """
    Gets key from dbt_project.yml config file items
    Converts the result from list to str, assuming the list has only one element

          Parameters
          ----------
              key : str
                  key of dbt_project.yml config file
              dbt_config : Optional[dict]
                  dbt_project.yml config file
          Returns
          -------
              path : str
                  e.g. models_Muso
    """
    if dbt_config is None:
        filename = _get_filename_safely(DBT_PROJECT_FINAL_FILENAME)
        with open(filename) as f:
            dbt_config = yaml.load(f, Loader=yaml.FullLoader)

    if len(dbt_config[key]) != 1:
        raise NotImplementedError(
            f"current implementation expects a list of size exactly 1 for {key} "
            f"in dbt_config (list={dbt_config[key]})"
        )

    return dbt_config[key][0]


def get_dbt_config_custom_schema_output_objects(
    dot_config: Optional[dict] = None,
) -> str:
    """
    Get schema suffix for test objects generated by dbt

          Parameters
          ----------
              dot_config : Optional[dict]
                  dot_project.yml config file
          Returns
          -------
              path : str
                  schema suffix for test objects
    """
    if dot_config is None:
        with open(_get_filename_safely(dot_config_FILENAME)) as f:
            dot_config = yaml.load(f, Loader=yaml.FullLoader)

    return dot_config.get("dot", {}).get("output_schema_suffix", None)


def _get_dbt_config_original_path(key: str, dbt_config: Optional[dict] = None) -> str:
    """
    Gets original (i.e. project_independent) path of `key` (can be anything, but refers
    to either dbt models or tests) from dbt_project.yml config file items

          Parameters
          ----------
              key : str
                  key of dbt_project.yml config file
              dbt_config : Optional[dict]
                  dbt_project.yml config file
          Returns
          -------
              path : str
                  e.g. models
    """
    if dbt_config is None:
        with open(DBT_PROJECT_FINAL_FILENAME) as f:
            dbt_config = yaml.load(f, Loader=yaml.FullLoader)

    return DBT_PROJECT_SEPARATOR.join(
        _get_dbt_config_key(key, dbt_config).split(DBT_PROJECT_SEPARATOR)[:-1]
    )


def adapt_core_entities(schema_project: str, entity_definition: str) -> Iterable[str]:
    """
    Adapts core entities definition to point the schema Jinja statement to the
    project schema

    Parameters
    ----------
    schema_project: str
        project schema
    entity_definition: str
        text for the entity definition

    Returns
    -------
    output_lines : Iterable[str]
        transformed lines, can be used to file.writelines()
    """
    output_lines = []
    for line in entity_definition.split("\n"):
        line = re.sub(
            "%\s*set\s*schema\s*=\s*(.+%)",  # pylint: disable=anomalous-backslash-in-string
            f"% set schema = '{schema_project}' %",
            line,
        )
        output_lines.append(line + "\n")
    return output_lines
