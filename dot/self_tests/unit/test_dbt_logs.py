""" tests for utils/dbt.py """

import ast
import logging
from .base_self_test_class import BaseSelfTestClass

from utils.dbt import (  # pylint: disable=wrong-import-order
    run_dbt_core,
    archive_previous_dbt_results,
    create_failed_dbt_test_models,
    run_dbt_test,
)
from utils.utils import setup_custom_logger  # pylint: disable=wrong-import-order

# functions under test
from utils.dbt_logs import (  # pylint: disable=wrong-import-order
    DbtOutputProcessedRow,
    read_dbt_logs,
    _get_test_parameters,
    _get_test_type,
    process_dbt_logs_row,
)


class DbtLogsUtilsTest(BaseSelfTestClass):
    """Test Class for dbt log processing"""

    def setUp(self) -> None:
        # "../db/dot/2-upload_static_data.sql"
        with open("self_tests/data/queries/configured_tests_dbt_core.sql", "r") as f:
            self.create_self_tests_db_schema(f.read())

    def tearDown(self) -> None:
        self.drop_self_tests_db_schema()

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

    def test_get_test_type(self):
        """
        Gets test type from dbt manifest metadata
        """
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
                unique_id="test.dbt_model_1.not_negative_string_column_dot_model__fpview_registration_value__value.e15d766b3b",
                test_type="not_negative_string_column",
                test_status="fail",
                test_message="got 1 result, configured to fail if != 0",
                column_name="value",
                entity_name="dot_model__fpview_registration",
                test_parameters="{'name': 'value'}",
                short_test_name="tr_dot_model__fpview_registration_value",
            )
            self.assertEqual(res, expected)
