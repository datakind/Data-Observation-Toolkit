import logging
import pytest
from mock import patch
from .base_self_test_class import BaseSelfTestClass

# UT after base_self_test_class imports
from utils.configuration_management import (
    generate_tests_from_db,
)  # pylint: disable=wrong-import-order


class GenerateTestsFromDbTest(BaseSelfTestClass):
    """Test Class"""

    def setUp(self) -> None:
        self.create_self_tests_db_schema(f.read())

    def tearDown(self) -> None:
        self.drop_self_tests_db_schema()

    @patch("utils.configuration_utils._get_filename_safely")
    @pytest.mark.skip("intermediate commit - WIP for this test")
    def test_generate_tests_from_db(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """test yaml file creation for 1 core entity -see file in filename below"""
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        dot_tests = generate_tests_from_db(
            project_id="Muso", logger=logging.getLogger()
        )
        assert dot_tests
        assert False
