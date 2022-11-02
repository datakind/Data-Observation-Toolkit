import uuid
import logging
from mock import patch
from .base_self_test_class import BaseSelfTestClass

# UT after base_self_test_class imports
from utils.run_management import run_dot_tests  # pylint: disable=wrong-import-order
from utils.utils import setup_custom_logger  # pylint: disable=wrong-import-order


class RunDotTestsTest(BaseSelfTestClass):
    """Test Class"""

    def setUp(self) -> None:
        self.create_self_tests_db_schema()

    def tearDown(self) -> None:
        self.drop_self_tests_db_schema()

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

        # TODO
