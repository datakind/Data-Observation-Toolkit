""" Integration test: runs DOT for the demo dataset and checks the results """
import os
import uuid
import logging
import shutil
import pandas as pd
from mock import patch
from ..self_tests_utils.dbt_base_safe_test_class import DbtBaseSelfTestClass

# UT after base_self_test_class imports
from utils.run_management import run_dot_tests  # pylint: disable=wrong-import-order
from utils.utils import setup_custom_logger  # pylint: disable=wrong-import-order
from utils.connection_utils import (
    get_db_params_from_config,
)  # pylint: disable=wrong-import-order
from utils.configuration_utils import (
    DbParamsConfigFile,
    DbParamsConnection,
)  # pylint: disable=wrong-import-order


class RunDotTestsTest(DbtBaseSelfTestClass):
    """Test Class"""

    def setUp(self) -> None:
        # load the DOT demo dataset
        self.create_self_tests_db_schema()

        self.cleanup_dbt_output_dir()

    @patch("utils.configuration_utils._get_filename_safely")
    def test_run_dot_tests(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """run all dot tests"""
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        logger = setup_custom_logger(
            "self_tests/output/logs/run_everything.log", logging.INFO
        )

        run_id = uuid.uuid4()

        run_dot_tests("ScanProject1", logger, run_id)

        # check results
        schema_dot, _, conn_dot = get_db_params_from_config(
            DbParamsConfigFile["dot_config.yml"],
            DbParamsConnection["dot"],
            "ScanProject1",
        )

        test_results_summary = pd.read_sql(
            f"SELECT * FROM {schema_dot}.test_results_summary", conn_dot
        )
        expected_test_results_summary = pd.read_csv(
            "self_tests/data/expected/integration/test_results_summary.csv", index_col=0
        )
        pd.testing.assert_frame_equal(
            test_results_summary.drop(columns=["run_id"]),
            expected_test_results_summary.drop(columns=["run_id"]),
        )

        test_results = pd.read_sql(f"SELECT * FROM {schema_dot}.test_results", conn_dot)
        expected_test_results = pd.read_csv(
            "self_tests/data/expected/integration/test_results.csv", index_col=0
        )
        pd.testing.assert_frame_equal(
            expected_test_results.drop(
                columns=["run_id", "test_result_id", "id_column_value"]
            ),
            test_results.drop(columns=["run_id", "test_result_id", "id_column_value"]),
        )
        self.assertListEqual(
            sorted(expected_test_results["id_column_value"].to_list()),
            sorted(test_results["id_column_value"].to_list()),
        )
