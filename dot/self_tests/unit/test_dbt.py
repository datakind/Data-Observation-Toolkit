""" tests for utils/dbt.py """

import uuid
import logging

from .base_self_test_class import BaseSelfTestClass

import pandas as pd

# UT after base_self_test_class imports
from utils.dbt import (  # pylint: disable=wrong-import-order
    extract_df_from_dbt_test_results_json,
)
from utils.utils import setup_custom_logger  # pylint: disable=wrong-import-order


class DbtUtilsTest(BaseSelfTestClass):
    """Test Class"""

    def setUp(self) -> None:
        # "../db/dot/2-upload_static_data.sql"
        with open("self_tests/data/queries/configured_tests_dbt_core.sql", "r") as f:
            self.create_self_tests_db_schema(f.read())

    def tearDown(self) -> None:
        self.drop_self_tests_db_schema()

    def test_extract_df_from_dbt_test_results_json(
        self,
    ):  # pylint: disable=no-value-for-parameter
        """test yaml file creation for 1 core entity -see file in filename below"""
        run_id = uuid.UUID("4541476c-814e-43fe-ab38-786f36beecbc")
        output = extract_df_from_dbt_test_results_json(
            run_id=run_id,
            project_id="Muso",
            logger=setup_custom_logger("self_tests/output/test.log", logging.INFO),
            target_path="self_tests/data/dot_output_files/dbt/target",
        )
        expected = pd.read_csv(
            "self_tests/data/expected/extract_df_from_dbt_test_results_json.csv",
            index_col=0,
        ).fillna("")
        skip_columns = [
            "run_id",
            "id_column_name",
        ]
        pd.testing.assert_frame_equal(
            output.drop(columns=skip_columns), expected.drop(columns=skip_columns)
        )
