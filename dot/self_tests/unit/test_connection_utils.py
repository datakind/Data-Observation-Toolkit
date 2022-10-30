from ..utils.base_self_test_class import BaseSelfTestClass

# UT after base_self_test_class imports
from utils.connection_utils import (  # pylint: disable=wrong-import-order
    remove_ge_schema_parameters,
    add_ge_schema_parameters,
)


class ConnUtilsTest(BaseSelfTestClass):
    """Test Clase"""

    @staticmethod
    def test_remove_ge_schema_parameters():
        """test function remove_ge_schema_parameters"""
        assert remove_ge_schema_parameters(
            [
                {
                    "key": "reported_by",
                    "quantity": "child_temperature_pre_chw",
                    "form_name": "dot_model__iccmview_assessment",
                    "id_column": "reported_by",
                    "schema_core": "public_tests",
                    "schema_source": "public",
                },
                {"another_param": "v", "schema_core": "public_tests"},
            ]
        ) == [
            {
                "key": "reported_by",
                "quantity": "child_temperature_pre_chw",
                "form_name": "dot_model__iccmview_assessment",
                "id_column": "reported_by",
            },
            {
                "another_param": "v",
            },
        ]

    @staticmethod
    def test_add_ge_schema_parameters():
        """test function add_ge_schema_parameters"""
        assert add_ge_schema_parameters(
            {
                "key": "reported_by",
                "quantity": "child_temperature_pre_chw",
                "form_name": "dot_model__iccmview_assessment",
                "id_column": "reported_by",
            },
            project_id=None,
            schema_core="whatever",
            schema_source="public",
        ) == {
            "key": "reported_by",
            "quantity": "child_temperature_pre_chw",
            "form_name": "dot_model__iccmview_assessment",
            "id_column": "reported_by",
            "schema_core": "whatever",
            "schema_source": "public",
        }
