""" Tests of configuration utils module """

from mock import patch
from ..self_tests_utils.base_self_test_class import BaseSelfTestClass

# UT after base_self_test_class imports
from utils.configuration_utils import (  # pylint: disable=wrong-import-order
    get_dbt_config_custom_schema_output_objects,
)


class ConfigUtilsTest(BaseSelfTestClass):
    """Test Class"""

    @patch("utils.configuration_utils._get_filename_safely")
    def test_dbt_config_custom_schema_output_objects(self, mock_get_filename_safely):
        """test get_dbt_config_custom_schema_output_objects"""
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        assert get_dbt_config_custom_schema_output_objects() == "tests"
        assert get_dbt_config_custom_schema_output_objects() == "tests"
        assert get_dbt_config_custom_schema_output_objects() == "tests"
