import logging
import os
from mock import patch
from .base_self_test_class import BaseSelfTestClass

# UT after base_self_test_class imports
from utils.dbt import create_core_entities  # pylint: disable=wrong-import-order


class CoreEntitiesCreationTest(BaseSelfTestClass):
    """Test Class"""

    def setUp(self) -> None:
        with open("self_tests/data/queries/core_entities_creation.sql", "r") as f:
            self.create_self_tests_db_schema(f.read())

    def tearDown(self) -> None:
        self.drop_self_tests_db_schema()

    @patch("utils.configuration_utils._get_config_filename")
    def test_yaml_creation(
        self, mock_get_config_filename
    ):  # pylint: disable=no-value-for-parameter
        """test yaml file creation for 1 core entity -see file in filename below"""
        mock_get_config_filename.side_effect = self.mock_get_config_filename

        schema, _, conn = self.get_self_tests_db_conn()
        output_dir = "self_tests/output/test_yaml_creation"
        filename = "dot_model__ancview_danger_sign.sql"
        schema_project = "data_muso"
        create_core_entities(
            schema, conn, schema_project, output_dir, logger=logging.getLogger()
        )
        conn.close()

        assert os.path.isfile(os.path.join(output_dir, filename))
        with open(f"self_tests/data/expected/{filename}", "r") as expected:
            expected_lines = expected.readlines()
            with open(os.path.join(output_dir, filename), "r") as result:
                result_lines = result.readlines()
            self.assertListEqual(expected_lines, result_lines)
