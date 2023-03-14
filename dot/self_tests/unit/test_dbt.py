""" tests for utils/dbt.py """

import uuid
import logging
import pandas as pd
from mock import patch

from ..self_tests_utils.base_self_test_class import BaseSelfTestClass

# UT after base_self_test_class imports
from utils.dbt import (  # pylint: disable=wrong-import-order
    extract_df_from_dbt_test_results_json,
    get_view_definition,
)
from utils.utils import (  # pylint: disable=wrong-import-order
    setup_custom_logger,
    format_uuid_list,
)


class DbtUtilsTest(BaseSelfTestClass):
    """Test Class"""

    def setUp(self) -> None:
        with open("self_tests/data/queries/dbt_core_generated_objects.sql", "r") as f:
            self.create_self_tests_db_schema(additional_query=f.read())

    @patch("utils.configuration_utils._get_filename_safely")
    def test_extract_df_from_dbt_test_results_json(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """
        test output df generated from dbt results in json format
        (dbt target directory)
        """
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        run_id = uuid.UUID("4541476c-814e-43fe-ab38-786f36beecbc")
        output = extract_df_from_dbt_test_results_json(
            run_id=run_id,
            project_id="ScanProject1",
            logger=setup_custom_logger("self_tests/output/test.log", logging.INFO),
            target_path="self_tests/data/dot_output_files/dbt/target",
        )

        expected = pd.read_csv(
            "self_tests/data/expected/extract_df_from_dbt_test_results_json.csv",
            index_col=0,
        ).fillna("")
        skip_columns = [
            "run_id",
            "id_column_name",
        ]
        pd.testing.assert_frame_equal(
            output.drop(columns=skip_columns), expected.drop(columns=skip_columns)
        )

    @patch("utils.configuration_utils._get_filename_safely")
    def test_get_view_definition(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """
        test for function get_view_definition; needs db connection & the test view
        """
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        self.assertEqual(
            get_view_definition(
                "ScanProject1",
                "chv_tr_different_dot_model__all_flight_data_price_distribution",
            ),
            " SELECT dot_model__airlines_data.airline,\n"
            "    failed.failed\n"
            "   FROM self_tests_public_tests.dot_model__airlines_data\n"
            "     JOIN unnest(ARRAY['British Airways'::text]) failed(failed)"
            " ON failed.failed = dot_model__airlines_data.airline::text;",
        )

    @staticmethod
    def test_format_uuid_list():
        """
        Formats `uuid_list` from postgres as actually a list

        Returns
        -------

        """
        assert format_uuid_list("{fc9f60d4-3cbf-3493-918e-a01478aa91db}") == [
            "fc9f60d4-3cbf-3493-918e-a01478aa91db",
        ]
        assert format_uuid_list(
            "{f542d6ed-7fa7-3d86-b054-8dacf1a73406,"
            "04c739e0-13ea-3c8f-9e65-38eeafcca330,"
            "fa8a11a6-79ab-307b-bede-81cbff179e46}"
        ) == [
            "f542d6ed-7fa7-3d86-b054-8dacf1a73406",
            "04c739e0-13ea-3c8f-9e65-38eeafcca330",
            "fa8a11a6-79ab-307b-bede-81cbff179e46",
        ]
