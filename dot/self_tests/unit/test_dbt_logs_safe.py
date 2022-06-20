""" tests for utils/dbt.py """

import os
import ast
import logging
import shutil

from mock import patch
from utils.configuration_utils import DBT_PROJECT_FINAL_FILENAME
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
    process_dbt_logs_row,
)


class DbtLogsUtilsTest(BaseSelfTestClass):
    """Test Class for dbt log processing"""

    def setUp(self) -> None:
        # create the schemas in each of the tests
        pass

    def tearDown(self) -> None:
        self.drop_self_tests_db_schema()

    @staticmethod
    def mock_get_filename_safely_dbt(path):
        """
        mock for dbt tests only, so that the yml and sql files are at models_self_tests
        (instead of e.g. models/Muso)
        """
        if path == DBT_PROJECT_FINAL_FILENAME:
            # dbt models at models_self_tests
            return "./config/example/self_tests/dbt/dbt_project.yml"
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Cannot find file {path}")
        return path

    def dbt_test_setup(self):
        """
        setup for dbt tests
        """
        with open("self_tests/data/queries/configured_tests_dbt_core.sql", "r") as f:
            self.create_self_tests_db_schema(f.read())

        shutil.copy(
            "./config/example/self_tests/dbt/dbt_project.yml", "./dbt/dbt_project.yml"
        )

        shutil.rmtree("dbt/models_self_tests", ignore_errors=True)
        shutil.copytree("self_tests/data/dot_input_files/dbt", "dbt/models_self_tests")

    @staticmethod
    def run_dbt_steps():
        """
        Runs all the actions for dbt
        """
        project_id = "Muso"
        logger = setup_custom_logger("self_tests/output/test.log", logging.INFO)
        run_dbt_core(project_id, logger)
        archive_previous_dbt_results(logger)
        create_failed_dbt_test_models(project_id, logger, "view")
        run_dbt_test(project_id, logger)

    @patch("utils.configuration_utils._get_filename_safely")
    def test_read_dbt_logs_safe(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """
        Will detect a change in logs due to dbt versions
        """
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely_dbt

        # 0. Test setup
        self.dbt_test_setup()

        # 1. Run all the dbt actions
        self.run_dbt_steps()

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
            for exp_k, exp_v in exp_line.items():
                if exp_k in ["timing", "execution_time", "thread_id"]:
                    continue
                out_line_v = out_line.get(exp_k)
                if isinstance(exp_v, dict):
                    for exp_k_2, exp_v_2 in exp_v.items():
                        if exp_k_2 in ["created_at"]:
                            continue
                        self.assertEqual(
                            out_line_v.get(exp_k_2),
                            exp_v_2,
                            f"failed key {exp_k}; expected: {exp_v}, output: {out_line.get(exp_k)}",
                        )
                else:
                    self.assertEqual(
                        out_line_v,
                        exp_v,
                        f"failed key {exp_k}; expected: {exp_v}, output: {out_line.get(exp_k)}",
                    )

    @patch("utils.configuration_utils._get_filename_safely")
    def test_process_dbt_logs_row_safe(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """
        Will detect a change in logs due to dbt versions, processing the raw and
        looking only for the required parameters
        """
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely_dbt

        # 0. Test setup
        self.dbt_test_setup()

        # 1. Run all the dbt actions
        self.run_dbt_steps()

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
                    "not_negative_string_column_dot_model__fpview_registration_value__value."
                    "e15d766b3b",
                    test_type="not_negative_string_column",
                    test_status="fail",
                    test_message="got 1 result, configured to fail if != 0",
                    column_name="value",
                    entity_name="dot_model__fpview_registration",
                    test_parameters="{'name': 'value'}",
                    short_test_name="tr_dot_model__fpview_registration_value",
                )
                self.assertEqual(res, expected)
                checked = True

        self.assertEqual(checked, True)
