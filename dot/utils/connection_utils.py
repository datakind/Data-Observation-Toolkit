import os
from typing import Tuple, Iterable, Optional

import psycopg2 as pg
import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData
from utils.configuration_utils import (
    DbParamsConfigFile,
    DbParamsConnection,
    load_credentials,
)

metadata: sa.sql.schema.MetaData = None


def get_metadata() -> sa.sql.schema.MetaData:
    """
    Gets the metadata local object to this module

    Returns
    -------
        MetaData
    """
    return metadata


def refresh_db_metadata(
    engine: sa.engine.base.Engine, schema: str
) -> sa.sql.schema.MetaData:
    """
    Refresh ddbb metadata. Slow operation!
    Can be called from anywhere and refreshes the object local object to this module

    @param engine: engine for connection to database
    @return: updated database metadata
    """
    global metadata
    metadata = MetaData(engine, schema=schema)
    metadata.reflect()
    return metadata


def create_sqlalchemy_engine(db_credentials: dict) -> sa.engine.base.Engine:
    """
    Default configs for creating engine

    Parameters
    ----------
    db_credentials : dict
        db credentials dictiontay
    Returns
    -------
    engine :
        SQL alchemy engine
    """
    engine = create_engine(
        "postgresql://"
        + db_credentials["user"]
        + ":"
        + db_credentials["pass"]
        + "@"
        + db_credentials["host"]
        + ":"
        + str(db_credentials["port"])
        + "/"
        + db_credentials["dbname"],
        paramstyle="format",
        executemany_mode="values",
        executemany_values_page_size=1000,
        executemany_batch_page_size=200,
    )
    refresh_db_metadata(engine, db_credentials["schema"])
    return engine


def update_db_config_from_os(db_config):
    """Overrides password with environment variable if db_config has environment
    variable syntax

    Parameters
    ----------
    db_config : json
        Raw Great expectations database config
    Returns
    -------
    db_config :
        Great expectations database config file with environment variables inserted

    """
    orig_pw = db_config["password"]
    env_var = (
        orig_pw[2:-1] if (orig_pw.startswith("${") and orig_pw.endswith("}")) else None
    )
    db_config["password"] = os.environ[env_var] if env_var else orig_pw
    return db_config


def get_db_params_from_config(
    config_file: DbParamsConfigFile,
    connection_params: DbParamsConnection,
    project_id: str,
) -> Tuple[str, sa.engine.base.Engine, pg.extensions.connection]:
    """Parses dbt yaml file to get db credentials. Also substitutes environment
    variables.

    Parameters
    ----------
    config_file: DbParamsConfigFile
        enum for dbt_project.yml config file
    connection_params: DbParamsConnection
        enum for connection
    project_id: str
        Project ID, eg 'Muso'. Must align with project_id in dot.projects

    Returns
    -------
    schema : str
        Name of db schema in yaml file
    engine : sqlalchemy db connection
        sqlalchemy db connection
    connection :
        pg.connect
    """
    if config_file == DbParamsConfigFile["dot_config.yml"]:
        db_credentials = load_credentials(project_id, connection_params)
    else:
        # since config_file is enum, this could only happen if a new value is added
        # but not implemented
        raise NotImplementedError(f"{config_file.name} is not implemented yet")

    conn = pg.connect(
        host=db_credentials["host"],
        user=db_credentials["user"],
        password=db_credentials["pass"],
        port=db_credentials["port"],
        dbname=db_credentials["dbname"],
    )

    # Added to prevent timeout in self-tests due to locked select query transation
    conn.set_session(autocommit=True)

    schema = db_credentials["schema"]
    engine = create_sqlalchemy_engine(db_credentials)
    return schema, engine, conn


def add_ge_schema_parameters(
    test_parameters: dict,
    project_id: str,
    schema_core: Optional[str] = None,
    schema_source: Optional[str] = None,
) -> dict:
    """
    Regardless of the parameters for any of the GE tests in db, some extra parameters
    for config need to be added,e.g. schema in which the core models are stored

        Parameters
        ----------
        test_parameters: dict
            json for the parameters of 1 test
        project_id: str
            Project ID, eg 'Muso'. Must align with project_id in dot.projects
        schema_core: Optional[str]
            schema in which the core models are stored
            if not informed, goes to db params to fetch the name
        schema_source: Optional[str]
            schema of the source data
            if not informed, goes to db params to fetch the name

        Returns
        -------
        output : dict
            test parameters including extra
    """
    if schema_core is None:
        schema_core, _, _ = get_db_params_from_config(
            DbParamsConfigFile["dot_config.yml"],
            DbParamsConnection["project_core"],
            project_id,
        )

    if schema_source is None:
        schema_source, _, _ = get_db_params_from_config(
            DbParamsConfigFile["dot_config.yml"],
            DbParamsConnection["project"],
            project_id,
        )

    return {
        **test_parameters,
        **{
            "schema_core": schema_core,
            "schema_source": schema_source,
        },
    }


def remove_ge_schema_parameters(test_parameters: Iterable[dict]) -> Iterable[dict]:
    """
    Remove extra paramets added by `add_ge_schema_parameters` so that test parameters
    correspond to the ones stored in the DOT configuration database

        Parameters
        ----------
        test_parameters: Iterable[dict]
            list of json for the parameters of all GE tests, including extra parameters

        Returns
        -------
        output : Iterable[dict]
            list of json for the parameters of all GE tests, excluding extra parameters
    """
    return [
        {
            k: v
            for k, v in tp.items()
            if k
            not in [
                "schema_core",
                "schema_source",
            ]
        }
        for tp in test_parameters
    ]
