""" tests for utils/dbt.py """

import ast

from mock import patch
from ..self_tests_utils.base_self_test_class import BaseSelfTestClass

# functions under test
from utils.dbt_logs import (  # pylint: disable=wrong-import-order
    DbtOutputProcessedRow,
    read_dbt_logs,
    _get_test_parameters,
    _get_test_type,
    process_dbt_logs_row,
)
from utils.configuration_utils import (  # pylint: disable=wrong-import-position
    dot_config_FILENAME,
    DBT_PROJECT_FINAL_FILENAME,
)


class DbtLogsUtilsTest(BaseSelfTestClass):
    """Test Class for dbt log processing"""

    @staticmethod
    def mock_get_filename_safely(path: str) -> str:
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
        if path == DBT_PROJECT_FINAL_FILENAME:
            return "./config/example/project_name/dbt/dbt_project.yml"
        raise FileNotFoundError(f"file path {path} needs to be mocked")

    def test_read_dbt_logs(self):
        """
        This test is not really so useful; a better test would run dbt on the inputs
        and check that the logs have not changed
        """
        output = read_dbt_logs(
            target_path="self_tests/data/dot_output_files/dbt/target",
        )
        with open("self_tests/data/expected/read_dbt_output_files.json", "r") as f:
            expected = ast.literal_eval(f.read())
        self.assertEqual(output, expected)

    def test_get_test_parameters_non_neg_string_column(self):
        """
        this test should be refactored to use not a full node from a manifest
        but a json constructed in the test itself w the right parameters
        TODO add test for mode node types, and in particular cutom_sql nodes
        """
        with open(
            "self_tests/data/dot_output_files/dbt/manifest_node_ex_non_negative_string_column.json",
            "r",
        ) as f:
            node = ast.literal_eval(f.read())
            output = _get_test_parameters(node, "not_negative_string_column")
            self.assertEqual(output, "{'name': 'value'}")

    @patch("utils.configuration_utils._get_filename_safely")
    def test_get_test_type(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """
        Gets test type from dbt manifest metadata
        """
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        node = {"test_metadata": {"name": "test_type_x"}}
        self.assertEqual(_get_test_type(node), "test_type_x")
        node = {"test_metadata": {}, "original_file_path": "tests/Muso/test_x.sql"}
        self.assertEqual(_get_test_type(node), "custom_sql")
        node = {"test_metadata": {}}
        self.assertEqual(_get_test_type(node), None)

    def test_process_dbt_logs_row(self):
        """
        Same as test_read_dbt_output_files, will not detect a problem due to dbt
        version changing logs
        """
        with open("self_tests/data/expected/read_dbt_output_files.json", "r") as f:
            # below contains lines read from logs passed through read_dbt_output_files
            expected_lines = ast.literal_eval(f.read())
            res = process_dbt_logs_row(expected_lines[0])
            expected = DbtOutputProcessedRow(
                unique_id="test.dbt_model_1.not_null_dot_model__all_flight_data_origin_airport.2196b664b6",
                test_type="not_null",
                test_status="fail",
                test_message="got 53 results, configured to fail if != 0",
                column_name="origin_airport",
                entity_name="dot_model__all_flight_data",
                test_parameters="{}",
                short_test_name="tr_dot_model__all_flight_data_not_null_origin_a",
            )
            self.assertEqual(res, expected)
