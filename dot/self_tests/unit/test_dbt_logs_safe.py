""" tests for utils/dbt.py """

import ast

from ..self_tests_utils.dbt_base_safe_test_class import DbtBaseSelfTestClass

# functions under test
from utils.dbt_logs import (  # pylint: disable=wrong-import-order
    DbtOutputProcessedRow,
    read_dbt_logs,
    process_dbt_logs_row,
)


class DbtLogsUtilsTest(DbtBaseSelfTestClass):
    """Test Class for dbt log processing

    safe test -meaning it will detect if a change of version in DBT
    changes the output logs in a way that will make DOT fail

    (i.e. because DOT relies on DBT logs, and that's not really safe)
    """

    def setUp(self) -> None:  # pylint: disable=arguments-differ
        super().setUp()  # pylint: disable=no-value-for-parameter

        # i.e. DBT is run for each of the tests on this class
        self.run_dbt_steps()

    @staticmethod
    def _cleanup_schema_name(value):
        """
        Cleans up schema from self_tests_dot to dot
        """
        return value.replace("self_tests_", "") if isinstance(value, str) else value

    def check_output_recursive(
        self,
        exp_line: str,
        out_line: str,
        skip_keys: dict = {
            0: ["timing", "execution_time", "thread_id"],
            1: ["created_at", "root_path"],
        },
        recursion_level: int = 0,
    ):
        """check outputs recursively for dbt logs"""
        for exp_k, exp_v in exp_line.items():
            if exp_k in skip_keys.get(recursion_level, []):
                continue
            out_line_v = out_line.get(exp_k)
            if isinstance(exp_v, dict):
                self.check_output_recursive(
                    exp_v, out_line_v, skip_keys, recursion_level + 1
                )
            else:
                self.assertEqual(
                    self._cleanup_schema_name(out_line_v),
                    self._cleanup_schema_name(exp_v),
                    f"failed key {exp_k}; expected: {exp_v}, output: {out_line.get(exp_k)}",
                )

    def test_read_dbt_logs_safe(self):
        """
        Will detect a change in logs due to dbt versions
        """

        # 2. test that the outputs are still ok
        output = read_dbt_logs(
            target_path="dbt/target",  # i.e. the usual execution path
        )
        with open("self_tests/data/expected/read_dbt_output_files.json", "r") as f:
            expected = ast.literal_eval(f.read())
        self.assertEqual(len(output), len(expected))
        for exp_line in expected:
            unique_id = exp_line["unique_id"]
            out_lines = [l for l in output if l.get("unique_id") == unique_id]
            self.assertEqual(
                len(out_lines),
                1,
                f"there should be 1 and only 1 output w unique_id {unique_id}",
            )
            out_line = out_lines[0]
            self.check_output_recursive(exp_line, out_line)

    def test_process_dbt_logs_row_safe(self):
        """
        Will detect a change in logs due to dbt versions, processing the raw and
        looking only for the required parameters
        """

        # 2. check results
        output = read_dbt_logs(
            target_path="dbt/target",  # i.e. the usual execution path
        )
        checked = False
        for line in output:
            res = process_dbt_logs_row(line)
            if res.test_type == "not_negative_string_column":
                expected = DbtOutputProcessedRow(
                    unique_id="test.dbt_model_1."
                    "not_negative_string_column_dot_model__all_flight_data_price__price."
                    "322389c2ba",
                    test_type="not_negative_string_column",
                    test_status="fail",
                    test_message="got 1 result, configured to fail if != 0",
                    column_name="price",
                    entity_id="dot_model__all_flight_data",
                    test_parameters="{'name': 'price'}",
                    short_test_name="tr_dot_model__all_flight_data_price",
                )
                self.assertEqual(res, expected)
                checked = True

        self.assertEqual(checked, True)
