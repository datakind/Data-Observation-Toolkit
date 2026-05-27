"""base self tests class for tests checking the output of the DBT process"""
import os
import logging
import shutil

from mock import patch
from ..self_tests_utils.base_self_test_class import BaseSelfTestClass

from utils.utils import setup_custom_logger  # pylint: disable=wrong-import-order

from utils.dbt import (  # pylint: disable=wrong-import-order
    run_dbt_core,
    archive_previous_dbt_results,
    create_failed_dbt_test_models,
    run_dbt_test,
)


class DbtBaseSelfTestClass(BaseSelfTestClass):
    @staticmethod
    def cleanup_dbt_output_dir():
        # for safety: remove any previous dbt target directory and model files
        if os.path.isdir("dbt/target"):
            shutil.rmtree("dbt/target")
        for path in os.listdir("dbt/"):
            if path.startswith("models") or path.startswith("tests"):
                shutil.rmtree(f"dbt/{path}")

    @patch("utils.configuration_utils._get_filename_safely")
    def setUp(
        self, mock_get_filename_safely
    ) -> None:  # pylint: disable=no-value-for-parameter
        super().setUp()

        self.cleanup_dbt_output_dir()

        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        self.dbt_test_setup()

    def dbt_test_setup(self):
        """
        setup for dbt tests

        - dbt_project config file
        - entities to be tested
        """
        shutil.copy(
            "./config/example/self_tests/dbt/dbt_project.yml", "./dbt/dbt_project.yml"
        )

        # copy the models
        # (i.e. in the full DOT pipeline these are generated from the configured_entities)
        shutil.rmtree("dbt/models", ignore_errors=True)
        shutil.copytree(
            "self_tests/data/dot_input_files/dbt", "dbt/models/ScanProject1"
        )

    @staticmethod
    def run_dbt_steps():
        """
        Runs all the actions for dbt
        """
        project_id = "ScanProject1"
        logger = setup_custom_logger("self_tests/output/test.log", logging.INFO)
        run_dbt_core(project_id, logger)
        archive_previous_dbt_results(logger)
        create_failed_dbt_test_models(project_id, logger, "view")
        run_dbt_test(project_id, logger)
