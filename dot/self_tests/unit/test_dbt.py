import uuid
import pytest

from mock import patch
from .base_self_test_class import BaseSelfTestClass

# UT after base_self_test_class imports
from utils.dbt import (  # pylint: disable=wrong-import-order
    extract_df_from_dbt_test_results_json,
)


class DbtUtilsTest(BaseSelfTestClass):
    """Test Class"""

    def setUp(self) -> None:
        # "../db/dot/2-upload_static_data.sql"
        with open("self_tests/data/queries/configured_tests_sample.sql", "r") as f:
            self.create_self_tests_db_schema(f.read())

    def tearDown(self) -> None:
        self.drop_self_tests_db_schema()

    @pytest.mark.skip("wip")
    @patch("utils.configuration_utils._get_config_filename")
    def test_extract_df_from_dbt_test_results_json(
        self, mock_get_config_filename
    ):  # pylint: disable=no-value-for-parameter
        """test yaml file creation for 1 core entity -see file in filename below"""
        mock_get_config_filename.side_effect = self.mock_get_config_filename

        run_id = uuid.UUID("4541476c-814e-43fe-ab38-786f36beecbc")
        output = extract_df_from_dbt_test_results_json(
            run_id=run_id,
            project_id="Muso",
        )
        assert False
