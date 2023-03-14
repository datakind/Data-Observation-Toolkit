""" Tests for some of the functions in utils.utils """
from typing import Tuple

import uuid
import logging
import pytest
import pandas as pd

from mock import patch
from ..self_tests_utils.base_self_test_class import BaseSelfTestClass

# UT after base_self_test_class imports
from utils.utils import (  # pylint: disable=wrong-import-order
    get_test_id,
    get_configured_tests_row,
    get_test_rows,
    setup_custom_logger,
    save_tests_to_db,
)
from utils.connection_utils import (  # pylint: disable=wrong-import-order
    get_db_params_from_config,
    DbParamsConnection,
    DbParamsConfigFile,
)


class UtilsTest(BaseSelfTestClass):
    """Test Class"""

    @staticmethod
    def get_test_summary(run_id: uuid.UUID) -> Tuple[pd.DataFrame, uuid.UUID]:
        """
        Get sample test summary DF + run id

        Returns
        -------
            Tuple[pd.DataFrame, uuid.UUID]
                test_summary & run_id
        """
        test_summary_row = {
            "run_id": run_id,
            "test_id": "cad13f73-27b5-3427-be8f-4d213bba3b19",
            "entity_id": "all_flight_data",
            "test_type": "accepted_values",
            "column_name": "stops",
            "id_column_name": None,
            "test_parameters": "{'values': ['1', '2', '3', 'Non-stop']}",
            "test_status": "fail",
            "test_status_message": "got 2 results, configured to fail if != 0",
            "failed_tests_view": "tr_dot_model__all_flight_data_accepted_values_stops",
            "failed_tests_view_sql": "Definition not needed for the self test",
        }
        test_summary = pd.DataFrame(test_summary_row, index=[0])
        return test_summary, run_id

    @staticmethod
    def prepare_failing_test_view():
        dot_model_view = (
            "-- self_tests_public_tests.dot_model__all_flight_data source\n\n"
            "CREATE OR REPLACE VIEW self_tests_public_tests.dot_model__all_flight_data\n"
            "AS SELECT flight_data.uuid,\n"
            "    flight_data.departure_time,\n"
            "    flight_data.airline,\n"
            "    flight_data.origin_airport,\n"
            "    flight_data.origin_iata,\n"
            "    flight_data.destination_airport,\n"
            "    flight_data.destination_iata,\n"
            "    flight_data.stops,\n"
            "    flight_data.price\n"
            "   FROM self_tests_public.flight_data;"
        )

        failing_test_view = (
            "-- self_tests_public_tests"
            ".tr_dot_model__all_flight_data_accepted_values_stops source\n\n"
            "CREATE OR REPLACE VIEW"
            " self_tests_public_tests.tr_dot_model__all_flight_data_accepted_values_stops\n"
            "AS WITH all_values AS (\n"
            "         SELECT dot_model__all_flight_data.stops AS value_field,\n"
            "            count(*) AS n_records\n"
            "           FROM self_tests_public_tests.dot_model__all_flight_data\n"
            "          GROUP BY dot_model__all_flight_data.stops\n"
            "        )\n"
            " SELECT all_values.value_field,\n"
            "    all_values.n_records\n"
            "   FROM all_values\n"
            "  WHERE all_values.value_field::text <> ALL (ARRAY["
            "'1'::character varying, "
            "'2'::character varying, "
            "'3'::character varying, "
            "'Non-stop'::character varying]::text[]"
            ");\n"
        )

        _, _, conn_test = get_db_params_from_config(
            DbParamsConfigFile["dot_config.yml"],
            DbParamsConnection["project_test"],
            "ScanProject1",
        )
        cursor = conn_test.cursor()
        cursor.execute(dot_model_view)
        cursor.execute(failing_test_view)

    @patch("utils.configuration_utils._get_filename_safely")
    def test_get_test_id(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """test yaml file creation for 1 core entity -see file in filename below"""
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        generated_test_id = get_test_id(
            test_type="not_negative_string_column",
            entity_id="all_flight_data",
            column="price",
            project_id="ScanProject1",
            test_parameters="""$$
                {
                   'name': 'price'
                }$$
            """.replace(
                "\n", ""
            ),
        )
        expected_test_id = "ed27037a-4054-3070-9d88-fdf9cd0231c8"
        self.assertEqual(
            expected_test_id,
            generated_test_id,
            f"difference in generated_test_id {generated_test_id} "
            f"vs {expected_test_id} for possible_duplicate_forms test",
        )

    @patch("utils.configuration_utils._get_filename_safely")
    def test_possible_duplicate_forms_test_malformed(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """test a possible_duplicate_forms w missing parameters"""
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        with self.assertRaises(Exception):
            self.create_self_tests_db_schema(
                additional_query="INSERT INTO self_tests_dot.configured_tests "
                "VALUES(TRUE,"
                "'ScanProject1',"
                "'7f78de0e-8268-3da6-8845-9a445457cc9a',"
                "'DUPLICATE-1',"
                "3, '', '', '', "
                "'adc007dd-2407-3dc2-95a7-002067e741f9',"
                "'possible_duplicate_forms', '', '',"
                """$${
                   'table_specific_uuid': 'uuid',
                   'table_specific_patient_uuid': 'patient_id',
                   'table_specific_reported_date': 'delivery_date',
                }$$
                ,"""
                "'2021-12-23 19:00:00.000 -0500',"
                "'2021-12-23 19:00:00.000 -0500',"
                "'Lorenzo');",
                schema_filepath=None,
                do_recreate_schema=False,
            )

    @patch("utils.configuration_utils._get_filename_safely")
    def test_custom_sql_test_malformed(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """test a possible_duplicate_forms w missing parameters"""
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        with self.assertRaises(Exception):
            self.create_self_tests_db_schema(
                additional_query="""
                    INSERT INTO self_tests_dot.configured_tests 
                    VALUES(TRUE, 'ScanProject1', 'c4a3da8f-32f4-4e9b-b135-354de203ca70',
                    'TREAT-1', 5, 'Test for new family planning method (NFP-1)', 
                    '', '', '52aa8e99-5221-3aac-bca5-b52b80b90929', 'custom_sql', 
                    '', '', $${"query":"SELECT
                              patient_id as primary_table_id_field,
                              value
                            FROM {{ ref('dot_model__fpview_registration') }} a
                            LIMIT 2"}$$,
                    '2021-12-23 19:00:00.000 -0500', 
                    '2021-12-23 19:00:00.000 -0500', 
                    'Leah');""",
                schema_filepath=None,
                do_recreate_schema=False,
            )

    @patch("utils.configuration_utils._get_filename_safely")
    def test_get_configured_tests_row_reference_error(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """test not found exception if the test has wrong parameters"""
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        with self.assertRaises(ReferenceError):
            _ = get_configured_tests_row(
                test_type="possible_duplicate_forms",
                entity_id="adc007dd-2407-3dc2-95a7-002067e741f9",
                column="",
                project_id="ScanProject1",
                test_parameters="""
                {
                   'table_specific_uuid': 'uuid',
                   'table_specific_period': 'day',
                   'table_specific_patient_uuid': 'patient_id',
                   'table_specific_reported_date': 'delivery_date',
                }
                """,
            )

    @patch("utils.configuration_utils._get_filename_safely")
    def test_get_configured_tests_row(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """test yaml file creation for 1 core entity -see file in filename below"""
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        configured_tests_row = get_configured_tests_row(
            test_type="not_negative_string_column",
            entity_id="all_flight_data",
            column="price",
            project_id="ScanProject1",
            test_parameters="{'name': 'price'}",
        )
        expected_test_id = "ed27037a-4054-3070-9d88-fdf9cd0231c8"
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
            "priority": 5,
            "description": "Price is not negative",
            "impact": "",
            "proposed_remediation": "",
            "entity_id": "all_flight_data",
            "test_type": "not_negative_string_column",
            "column_name": "price",
            "column_description": "",
            "test_parameters": "{'name': 'price'}",
            "last_updated_by": "Matt",
        }
        for k, v in expected_row.items():
            self.assertEqual(
                str(v),
                str(configured_tests_row.get(k)),
                f"difference in {k}; {v} vs {configured_tests_row[k]}",
            )

    @patch("utils.configuration_utils._get_filename_safely")
    def test_get_test_rows(
        self, mock_get_filename_safely
    ):  # pylint: disable=no-value-for-parameter
        """test for get_test_rows"""
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        # create data for the test view that has failing rows
        run_id = uuid.UUID("4541476c-814e-43fe-ab38-786f36beecbc")
        self.prepare_failing_test_view()

        # function under test is `get_test_rows`
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

    @pytest.mark.skip("temporarily disabled")
    @patch("utils.configuration_utils._get_filename_safely")
    def test_save_tests_to_db(self, mock_get_filename_safely):
        """
        TODO to make it work
              1. take care of FK when inserting test_rows: configured_tests, runs, etc
              2. at this stage, test_summary has some counts of failing/passing rows
                    ==> improve helper functions
        Parameters
        ----------
        mock_get_filename_safely

        Returns
        -------

        """
        mock_get_filename_safely.side_effect = self.mock_get_filename_safely

        test_summary, run_id = self.get_test_summary()
        test_row_dict = {
            "test_result_id": uuid.UUID("30bf02ca-7ddb-3562-96dc-e4cf81a5ce98"),
            "run_id": run_id,
            "test_id": "329bdb85-5f36-372d-bab0-8efd3c2d33b4",
            "entity_id": "95bd0f60-ab59-48fc-a62e-f256f5f3e6de",
            "status": "fail",
            "view_name": "tr_dot_model__fpview_registration_id10",
            "id_column_name": "uuid",
            "id_column_value": "patient_id2",
        }
        test_rows = pd.DataFrame(test_row_dict, index=[0])

        save_tests_to_db(
            test_rows,
            test_summary,
            project_id="ScanProject1",
            logger=setup_custom_logger("self_tests/output/test.log", logging.INFO),
        )
