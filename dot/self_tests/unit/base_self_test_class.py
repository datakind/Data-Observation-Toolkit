import unittest
import os
import sys
import shutil
from typing import Tuple, Optional
from mock import patch

import psycopg2 as pg
import sqlalchemy as sa
from psycopg2 import sql

# go to `dot` directory, i.e. 2 levels up to current test file
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print(os.getcwd())
sys.path.append(".")

# after this, imports from the dot_run can be done
from utils.connection_utils import (  # pylint: disable=wrong-import-position
    get_db_params_from_config,
    DbParamsConnection,
    DbParamsConfigFile,
)
from utils.configuration_utils import (  # pylint: disable=wrong-import-position
    dot_config_FILENAME,
)


class BaseSelfTestClass(unittest.TestCase):
    """
    Base class for all tests, includes some utility functions for self test outputs and
    db connection
    """

    @classmethod
    def setUpClass(cls):
        # prepare dir for output files
        test_output_path = "./self_tests/output"
        if os.path.isdir(test_output_path):
            shutil.rmtree(test_output_path)
        os.makedirs(test_output_path)

    @staticmethod
    def mock_get_config_filename(path: str) -> str:
        """
        Mock paths of config files

        Parameters
        ----------
        path

        Returns
        -------

        """
        if path == dot_config_FILENAME:
            return "self_tests/data/base_self_test/dot_config.yml"
        if path == "./config/example/project_name/dbt/dbt_project.yml":
            return path
        raise FileNotFoundError(f"file path {path} needs to be mocked")

    @patch("utils.configuration_utils._get_config_filename")
    def get_self_tests_db_conn(
        self, mock_get_config_filename
    ) -> Tuple[
        str, sa.engine.base.Engine, pg.extensions.connection
    ]:  # pylint: disable=no-value-for-parameter
        """
        Obtains the db connection for the self tests db

        Parameters
        ----------
        mock_get_config_filename

        Returns
        -------
            schema: str
            engine: sa.engine.base.Engine
            conn: pg.extensions.connection
        """
        mock_get_config_filename.side_effect = self.mock_get_config_filename
        schema, engine, conn = get_db_params_from_config(
            DbParamsConfigFile["dot_config.yml"],
            DbParamsConnection["dot"],
            "Muso",
        )
        return schema, engine, conn

    def drop_self_tests_db_schema(
        self,
        schema: str = None,
        conn: Optional[pg.extensions.connection] = None,
        cursor: Optional[pg.extensions.cursor] = None,
    ) -> None:
        """
        Drops the self tests' schema

        Parameters
        ----------
        schema: str
            schema for self tests
        conn: Optional[pg.extensions.connection]
            connection to the selt tests db; if not provided will
            figure out
        cursor: Optional[pg.extensions.cursor]
            cursor within `conn`, if not provided will figure out

        Returns
        -------

        """
        if schema is None or conn is None:
            (
                schema,
                _,
                conn,
            ) = self.get_self_tests_db_conn()  # pylint: disable=no-value-for-parameter

        if cursor is None:
            cursor = conn.cursor()

        query_drop = sql.SQL("drop schema if exists {name} cascade").format(
            name=sql.Identifier(schema)
        )
        cursor.execute(query_drop)
        conn.commit()

    def create_self_tests_db_schema(self, additional_query: str = None):
        """
        Creates the self tests' schema and runs the queries in `additional_query`
        if provided

        Parameters
        ----------
        additional_query
            string with valid queries to run

        Returns
        -------
        None
        """
        (
            schema,
            _,
            conn,
        ) = self.get_self_tests_db_conn()  # pylint: disable=no-value-for-parameter

        cursor = conn.cursor()

        self.drop_self_tests_db_schema(schema, conn, cursor)

        query_create = sql.SQL("create schema {name}").format(
            name=sql.Identifier(schema)
        )
        cursor.execute(query_create)
        conn.commit()

        with open("../db/dot/1-schema.sql", "r") as f:
            queries = []
            query_lines = []
            all_query_lines = []
            lines = f.readlines()
            for line in lines:
                if "create schema" in line.lower():
                    continue
                line = line.replace("dot.", f"{schema}.")
                query_lines.append(line)
                all_query_lines.append(line)
                if ";" in line:
                    queries.append("".join(query_lines))
                    query_lines = []

            for query in queries:
                if "create table if not exists" in query.lower():
                    # execute only table creation queries TODO reconsider
                    cursor.execute(query)
                    conn.commit()

            # execute all queries
            cursor.execute("".join(all_query_lines))
            conn.commit()

        if additional_query:
            cursor.execute(additional_query)
            conn.commit()
