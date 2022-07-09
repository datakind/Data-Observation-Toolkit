import os
import re
from enum import Enum
from pathlib import Path
from typing import Iterable, Callable, Optional
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
    with open(_get_filename_safely(dot_config_FILENAME)) as f:
        db_config = yaml.load(f, Loader=yaml.FullLoader)

    db_credentials = _get_credentials(db_config, project_id, connection_params)

    # Support dbt environment variable format
    db_credentials["pass"] = extract_dbt_config_env_variable(db_credentials["pass"])
    return db_credentials


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


def _create_config_file(
    config_project_file_name: str,
    config_example_file_name: str,
    final_config_file_name: str,
    transform_example_file_function: Optional[
        Callable
    ] = lambda input_lines: input_lines,
    finally_action: Optional[Callable] = None,
    **kwargs,
) -> None:
    """
    Internal function - base for config file manipulation
    1. Tries to read the config file from the project-dependent path
    2. If the file in 1. does not exist, it takes the corresponding file in the example
        path
    3. Only if it is the example file, the tranformations defined in
        `transform_example_file_function` are applied
    4. If `finally_action` is defined, the customized is used to write the file from
        either 1. or 3. to the final destination `final_config_file_name`
    5. If not 4., the file resulting from either 1. or 3. is written to the final
        destination `final_config_file_name`

        Parameters
        ----------
        config_project_file_name : str
            project-dependent path
        config_example_file_name : str
            example path
        final_config_file_name : str
            final destination of the file
        transform_example_file_function : Optional[Callable]
            function to transform the output of the example file (if not set,
            no transformation is applied)
        finally_action : Optional[Callable]
            function to write the file into `final_config_file_name` (if not set,
            the file is writeen wo customization)
        Returns
        -------
        None
    """
    config_file_lines = []
    try:
        with open(_get_filename_safely(config_project_file_name), "r") as fr:
            # read project dependent file, if exists
            config_file_lines = fr.readlines()
    except FileNotFoundError:
        with open(_get_filename_safely(config_example_file_name), "r") as fr:
            # read example file and apply required transformations
            lines = fr.readlines()
            config_file_lines = transform_example_file_function(
                input_lines=lines, **kwargs
            )
    finally:
        if finally_action:
            finally_action(config_file_lines, final_config_file_name, **kwargs)
        else:
            with open(final_config_file_name, "w") as fw:
                fw.writelines(config_file_lines)


def create_profiles_yaml(project_id: str, db_credentials_project: dict) -> None:
    """
    Writes profiles.yml into its final destination, taking either the config file at
    the project-dependent path, or the example file applying
    project-dependent transformations

          Parameters
          ----------
              project_id : str
                  Project ID, eg 'Muso'. Must align with project_id in dot.projects
              db_credentials_project : dict
                  credentials
    """

    def finally_action(
        config_file_lines, final_config_file_name, **kwargs
    ):  # pylint: disable=unused-argument
        # put profiles.yaml into home
        d = "/".join(final_config_file_name.split("/")[:-1])
        if not os.path.isdir(d):
            os.makedirs(d)
        with open(final_config_file_name, "w") as fw:
            fw.writelines(config_file_lines)

    _create_config_file(
        f"./config/{project_id}/dbt/profiles.yml",
        "./config/example/project_name/dbt/profiles.yml",
        DBT_PROFILES_FINAL_FILENAME,
        transform_example_file_function=_adapt_credentials_yaml,
        finally_action=finally_action,
        db_credentials_project=db_credentials_project,
    )


def _adapt_credentials_yaml(
    db_credentials_project: dict, input_lines: Iterable[str], translate_keys: dict = {}
) -> Iterable[str]:
    """
    Transformations to apply to credentials (used for DBT profiles.yml,
    GE config_variables.yml)
    so that an example file can contail real credentials

          Parameters
          ----------
              db_credentials_project : dict
                  credentials
              input_lines : Iterable[str]
                  result of file.readlines() of the input file
              translate_keys : dict
                  dictionary of keys that need to be adapted, e.g. `user` instead
                  of `username`
          Returns
          -------
              output_lines : Iterable[str]
                  transformed lines, can be used to file.writelines()
    """
    dbt_profile_lines = []
    for line in input_lines:
        for k, v in db_credentials_project.items():
            k = translate_keys.get(
                k, k
            )  # change the key, if present in `translate_keys`
            line = re.sub(f"{k}:(.+\n)", f"{k}: {v}\n", line)
        dbt_profile_lines.append(line)
    return dbt_profile_lines


def create_dbt_project_yaml(project_id: str) -> None:
    """
    Writes dbt_project.yml into its final destination, taking either the config file
    at the project-dependent path,
    or the example file applying project-dependent transformations

          Parameters
          ----------
              project_id : str
                  Project ID, eg 'Muso'. Must align with project_id in dot.projects
    """
    with open(_get_filename_safely(dot_config_FILENAME)) as f:
        dot_config = yaml.load(f, Loader=yaml.FullLoader)

    _create_config_file(
        f"./config/{project_id}/dbt/dbt_project.yml",
        "./config/example/project_name/dbt/dbt_project.yml",
        DBT_PROJECT_FINAL_FILENAME,
        transform_example_file_function=_adapt_dbt_config_yaml,
        project_id=project_id,
        output_schema_suffix=dot_config.get("dot", {}).get("output_schema_suffix"),
    )


def _adapt_dbt_config_yaml(
    project_id: str,
    input_lines: Iterable[str],
    output_schema_suffix: Optional[str] = None,
) -> Iterable[str]:
    """
    Transformations to apply to ./dbt/dbt_project.yml so that it reads from the
    current project folders

          Parameters
          ----------
              project_id : str
                  Project ID, eg 'Muso'. Must align with project_id in dot.projects
              input_lines : Iterable[str]
                  result of file.readlines() of the input file
          Returns
          -------
              output_lines : Iterable[str]
                  transformed lines, can be used to file.writelines()
    """
    output_lines = []
    for line in input_lines:
        line = re.sub(
            'model-paths: (\[".+\\n)',
            f'model-paths: ["models{DBT_PROJECT_SEPARATOR}{project_id}"]\n',
            line,
        )
        line = re.sub(
            'test-paths: (\[".+\\n)',
            f'test-paths: ["tests{DBT_PROJECT_SEPARATOR}{project_id}"]\n',
            line,
        )
        output_lines.append(line)

    if output_schema_suffix:
        output_lines.append("models:\n")
        output_lines.append("  dbt_model_1:\n")
        output_lines.append("    core:\n")
        output_lines.append(f"      +schema: '{output_schema_suffix}'\n")
        output_lines.append("    test:\n")
        output_lines.append(f"      +schema: '{output_schema_suffix}'\n")

    return output_lines


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


def create_great_expectations_yaml(project_id: str) -> None:
    """
    Writes great_expectations.yml into its final destination, taking either the config
    file at the project-dependent path,
    or the example file applying project-dependent transformations

          Parameters
          ----------
              project_id : str
                  Project ID, eg 'Muso'. Must align with project_id in dot.projects
    """
    _create_config_file(
        f"./config/{project_id}/ge/great_expectations.yml",
        "./config/example/project_name/ge/great_expectations.yml",
        GE_GREAT_EXPECTATIONS_FINAL_FILENAME,
        transform_example_file_function=_adapt_great_expectations_yaml,
        project_id=project_id,
    )


def _adapt_great_expectations_yaml(
    project_id: str, input_lines: Iterable[str]
) -> Iterable[str]:
    """
    Transformations to apply to great_expectations.yml so that it reads from the
    current project folders

          Parameters
          ----------
              project_id : str
                  Project ID, eg 'Muso'. Must align with project_id in dot.projects
              input_lines : Iterable[str]
                  result of file.readlines() of the input file
          Returns
          -------
              output_lines : Iterable[str]
                  transformed lines, can be used to file.writelines()
    """
    output_lines = []
    for line in input_lines:
        line = re.sub(
            "base_directory: expectations/(.+\n)",
            f"base_directory: expectations/{project_id}/\n",
            line,
        )
        line = re.sub(
            "base_directory: uncommitted/validations/(.+\n)",
            f"base_directory: uncommitted/validations/{project_id}/\n",
            line,
        )
        output_lines.append(line)
    return output_lines


def create_batch_config_json(project_id: str):
    """
    Writes batch_config.json into its final destination, taking either the config file
    at the project-dependent path,
    or the example file applying project-dependent transformations

          Parameters
          ----------
              project_id : str
                  Project ID, eg 'Muso'. Must align with project_id in dot.projects
    """
    _create_config_file(
        f"./config/{project_id}/ge/batch_config.json",
        "./config/example/project_name/ge/batch_config.json",
        GE_BATCH_CONFIG_FINAL_FILENAME,
    )


def create_config_variables_yaml(project_id: str, db_credentials_project: dict) -> None:
    """
    Writes config_variables.yml into its final destination, taking either the config
    file at the project-dependent path,
    or the example file applying project-dependent transformations

          Parameters
          ----------
              project_id : str
                  Project ID, eg 'Muso'. Must align with project_id in dot.projects
              db_credentials_project : dict
                  credentials
    """
    d = "/".join(GE_CONFIG_VARIABLES_FINAL_FILENAME.split("/")[:-1])
    if not os.path.exists(d):
        os.makedirs(d)

    _create_config_file(
        f"./config/{project_id}/ge/config_variables.yml",
        "./config/example/project_name/ge/config_variables.yml",
        GE_CONFIG_VARIABLES_FINAL_FILENAME,
        transform_example_file_function=_adapt_credentials_yaml,
        db_credentials_project=db_credentials_project,
        translate_keys={
            "user": "username",
            "type": "drivername",
            "pass": "password",
            "dbname": "database",
        },
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
            "%\s*set\s*schema\s*=\s*(.+%)", f"% set schema = '{schema_project}' %", line
        )
        output_lines.append(line + "\n")
    return output_lines
