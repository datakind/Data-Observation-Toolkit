"""
Replicates tests in test_dot_utils.py adding the column id_column_name to the schema
"""
import uuid
import logging

from mock import patch
from .test_dot_utils import UtilsTest

# UT after base_self_test_class imports
from utils.utils import (  # pylint: disable=wrong-import-order
    get_configured_tests_row,
    get_test_rows,
    setup_custom_logger,
)
from utils.run_management import run_dot_tests  # pylint: disable=wrong-import-order


class UtilsTestImproved(UtilsTest):
    """Test Class"""

    def setUp(self) -> None:
        self.create_self_tests_db_schema(
            "\n".join(
                [
                    "ALTER TABLE self_tests_dot.configured_tests "
                    "ADD COLUMN id_column_name VARCHAR(300) NULL;",
                    "UPDATE self_tests_dot.configured_tests "
                    "SET id_column_name = 'uuid';",
                ]
            )
        )

    def tearDown(self) -> None:
        self.drop_self_tests_db_schema()

    @patch("utils.configuration_utils._get_filename_safely")
    def test_get_configured_tests_row(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """test yaml file creation for 1 core entity -see file in filename below"""
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        configured_tests_row = get_configured_tests_row(
            test_type="accepted_values",
            entity_id="ca4513fa-96e0-3a95-a1a8-7f0c127ea82a",
            column="stops",
            project_id="ScanProject1",
            test_parameters='{"values": ["1", "2", "3", "Non-stop"]}',
        )
        expected_test_id = "dac4c545-f610-3dae-ad82-1ddf27dae144"
        self.assertEqual(
            expected_test_id,
            configured_tests_row["test_id"],
            f"difference in generated_test_id {configured_tests_row['test_id']} "
            f"vs {expected_test_id} for possible_duplicate_forms test",
        )
        expected_row = {
            "test_activated": True,
            "project_id": "ScanProject1",
            "test_id": expected_test_id,
            "scenario_id": "INCONSISTENT-1",
            "priority": 3,
            "description": "Disallowed FP methods entered in form",
            "impact": "",
            "proposed_remediation": "",
            "entity_id": "ca4513fa-96e0-3a95-a1a8-7f0c127ea82a",
            "test_type": "accepted_values",
            "column_name": "stops",
            "column_description": "",
            "id_column_name": "uuid",
            "test_parameters": "{'values': ['1', '2', '3', 'Non-stop']}",
            "last_updated_by": "Matt",
        }
        for k, v in expected_row.items():  # pylint: disable=invalid-name
            self.assertEqual(
                str(v),
                str(configured_tests_row.get(k)),
                f"difference in {k}; {v} vs {configured_tests_row[k]}",
            )

    @patch("utils.configuration_utils._get_filename_safely")
    def test_get_test_rows(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """test get failing rows for custom test"""
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        # create data for the core entity
        # TODO should insert the necessary results instead
        logger = setup_custom_logger(
            "self_tests/output/logs/run_everything.log", logging.INFO
        )
        run_id = uuid.UUID("4541476c-814e-43fe-ab38-786f36beecbc")
        run_dot_tests("ScanProject1", logger, run_id)

        # create data for the test view of failing rows
        test_summary, run_id = self.get_test_summary(run_id)
        test_rows = get_test_rows(
            test_summary,
            run_id,
            project_id="ScanProject1",
            logger=setup_custom_logger("self_tests/output/test.log", logging.INFO),
        )
        self.assertEqual(
            len(test_rows.id_column_value.to_list()),
            253,
        )
        self.assertEqual(
            sorted(test_rows.id_column_value.to_list())[0],
            "000ea267-ffb3-3a58-8e71-eaa3c6a0a81f",
        )
