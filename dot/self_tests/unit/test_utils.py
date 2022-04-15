from mock import patch
from .base_self_test_class import BaseSelfTestClass

# UT after base_self_test_class imports
from utils.utils import (  # pylint: disable=wrong-import-order
    get_test_id,
    get_entity_id_from_name,
    get_entity_name_from_id,
)


class UtilsTest(BaseSelfTestClass):
    """Test Clase"""

    def setUp(self) -> None:
        # "../db/dot/2-upload_static_data.sql"
        with open("self_tests/data/queries/configured_tests_sample.sql", "r") as f:
            self.create_self_tests_db_schema(f.read())

    def tearDown(self) -> None:
        self.drop_self_tests_db_schema()

    @patch("utils.configuration_utils._get_config_filename")
    def test_get_test_id(
        self, mock_get_config_filename
    ):  # pylint: disable=no-value-for-parameter
        """test yaml file creation for 1 core entity -see file in filename below"""
        mock_get_config_filename.side_effect = self.mock_get_config_filename

        generated_test_id = get_test_id(
            test_type="possible_duplicate_forms",
            entity_id="66f5d13a-8f74-4f97-836b-334d97932781",
            column="",
            project_id="Muso",
            test_parameters="table_specific_reported_date: delivery_date| table_specific_patient_uuid: patient_id| table_specific_uuid: uuid",
        )
        expected_test_id = "329bdb85-5f36-372d-bab0-8efd3c2d33b4"
        self.assertEqual(
            expected_test_id,
            generated_test_id,
            f"difference in generated_test_id {generated_test_id} vs {expected_test_id} for possible_duplicate_forms test",
        )

    @patch("utils.configuration_utils._get_config_filename")
    def test_get_entity_id_from_name(
        self, mock_get_config_filename
    ):  # pylint: disable=no-value-for-parameter
        mock_get_config_filename.side_effect = self.mock_get_config_filename

        self.assertEqual(
            "66f5d13a-8f74-4f97-836b-334d97932781",
            get_entity_id_from_name("Muso", "dot_model__ancview_delivery"),
        )

    @patch("utils.configuration_utils._get_config_filename")
    def test_get_entity_name_from_id(
        self, mock_get_config_filename
    ):  # pylint: disable=no-value-for-parameter
        mock_get_config_filename.side_effect = self.mock_get_config_filename

        self.assertEqual(
            "dot_model__ancview_delivery",
            get_entity_name_from_id("Muso", "66f5d13a-8f74-4f97-836b-334d97932781"),
        )
