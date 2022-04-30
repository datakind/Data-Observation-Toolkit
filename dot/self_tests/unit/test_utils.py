import uuid
import logging
import pandas as pd
import pytest

from mock import patch
from typing import Tuple
from .base_self_test_class import BaseSelfTestClass

# UT after base_self_test_class imports
from utils.utils import (  # pylint: disable=wrong-import-order
    get_test_id,
    get_configured_tests_row,
    get_entity_id_from_name,
    get_entity_name_from_id,
    get_test_rows,
    setup_custom_logger,
    save_tests_to_db,
)
from utils.connection_utils import (  # pylint: disable=wrong-import-position
    DbParamsConnection,
)


class UtilsTest(BaseSelfTestClass):
    """Test Class"""

    def setUp(self) -> None:
        # "../db/dot/2-upload_static_data.sql"
        with open("self_tests/data/queries/configured_tests_sample.sql", "r") as f:
            self.create_self_tests_db_schema(f.read())

    def tearDown(self) -> None:
        self.drop_self_tests_db_schema()

    @staticmethod
    def get_test_summary() -> Tuple[pd.DataFrame, uuid.UUID]:
        """
        Get sample test summary DF + run id

        Returns
        -------
            Tuple[pd.DataFrame, uuid.UUID]
                test_summary & run_id
        """
        run_id = uuid.UUID("4541476c-814e-43fe-ab38-786f36beecbc")
        test_summary_row = {
            "run_id": run_id,
            "test_id": "ef6bb39d-7a89-3972-b5b6-719d4435e7f9",
            "entity_id": "95bd0f60-ab59-48fc-a62e-f256f5f3e6de",
            "test_type": "custom_sql",
            "column_name": "",
            # "id_column_name": "patient_id",
            "test_parameters": "SQL for the test definition; irrelevant for self_tests",
            "test_status": "fail",
            "test_status_message": "got 49 results, configured to fail if != 0",
            "failed_tests_view": "tr_dot_model__fpview_registration_id10",
            "failed_tests_view_sql": "SQL for  view of  failing rows; irrelevant self_tests",
        }
        test_summary = pd.DataFrame(test_summary_row, index=[0])
        return test_summary, run_id

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
            test_parameters="table_specific_reported_date: delivery_date"
            "| table_specific_patient_uuid: patient_id"
            "| table_specific_uuid: uuid",
        )
        expected_test_id = "329bdb85-5f36-372d-bab0-8efd3c2d33b4"
        self.assertEqual(
            expected_test_id,
            generated_test_id,
            f"difference in generated_test_id {generated_test_id} "
            f"vs {expected_test_id} for possible_duplicate_forms test",
        )

    @patch("utils.configuration_utils._get_config_filename")
    def test_get_configured_tests_row(
        self, mock_get_config_filename
    ):  # pylint: disable=no-value-for-parameter
        """test yaml file creation for 1 core entity -see file in filename below"""
        mock_get_config_filename.side_effect = self.mock_get_config_filename

        configured_tests_row = get_configured_tests_row(
            test_type="possible_duplicate_forms",
            entity_id="66f5d13a-8f74-4f97-836b-334d97932781",
            column="",
            project_id="Muso",
            test_parameters="table_specific_reported_date: delivery_date"
            "| table_specific_patient_uuid: patient_id"
            "| table_specific_uuid: uuid",
        )
        expected_test_id = "329bdb85-5f36-372d-bab0-8efd3c2d33b4"
        self.assertEqual(
            expected_test_id,
            configured_tests_row["test_id"],
            f"difference in generated_test_id {configured_tests_row['test_id']} "
            f"vs {expected_test_id} for possible_duplicate_forms test",
        )
        expected_row = {
            "test_activated": True,
            "project_id": "Muso",
            "test_id": "329bdb85-5f36-372d-bab0-8efd3c2d33b4",
            "scenario_id": "DUPLICATE-1",
            "priority": 3,
            "description": "",
            "impact": "",
            "proposed_remediation": "",
            "entity_id": "66f5d13a-8f74-4f97-836b-334d97932781",
            "test_type": "possible_duplicate_forms",
            "column_name": "",
            "column_description": "",
            # "id_column_name": "",
            "test_parameters": "table_specific_reported_date: delivery_date"
            "| table_specific_patient_uuid: patient_id"
            "| table_specific_uuid: uuid",
            "last_updated_by": "Lorenzo",
        }
        for k, v in expected_row.items():
            self.assertEqual(
                v,
                configured_tests_row.get(k),
                f"difference in {k}; {v} vs {configured_tests_row[k]}",
            )

    @patch("utils.configuration_utils._get_config_filename")
    def test_get_entity_id_from_name(
        self, mock_get_config_filename
    ):  # pylint: disable=no-value-for-parameter
        """test for get_entity_id_from_name"""
        mock_get_config_filename.side_effect = self.mock_get_config_filename

        self.assertEqual(
            "66f5d13a-8f74-4f97-836b-334d97932781",
            get_entity_id_from_name("Muso", "dot_model__ancview_delivery"),
        )

    @patch("utils.configuration_utils._get_config_filename")
    def test_get_entity_name_from_id(
        self, mock_get_config_filename
    ):  # pylint: disable=no-value-for-parameter
        """test for get_entity_name_from_id"""
        mock_get_config_filename.side_effect = self.mock_get_config_filename

        self.assertEqual(
            "dot_model__ancview_delivery",
            get_entity_name_from_id("Muso", "66f5d13a-8f74-4f97-836b-334d97932781"),
        )

    @patch("utils.configuration_utils._get_config_filename")
    def test_get_test_rows(
        self, mock_get_config_filename
    ):  # pylint: disable=no-value-for-parameter
        """test for get_test_rows"""
        mock_get_config_filename.side_effect = self.mock_get_config_filename

        # create data for the core entity
        # TODO add an utility function to do this
        schema_core, _, conn_core = self.get_self_tests_db_conn(
            connection=DbParamsConnection["project_core"]
        )
        cursor = conn_core.cursor()
        cursor.execute(
            f"""
            DROP SCHEMA IF EXISTS {schema_core} CASCADE;
            CREATE SCHEMA IF NOT EXISTS {schema_core};
            CREATE TABLE IF NOT EXISTS {schema_core}.dot_model__fpview_registration(
                uuid VARCHAR(300),
                value VARCHAR(1000) NOT NULL
            );
            INSERT INTO {schema_core}.dot_model__fpview_registration
            select * from
                (values ('patient_id1', '1'), ('patient_id2', '2'), ('patient_id3', '3'))
                x(patient_id, value)
            """
        )
        conn_core.commit()

        # create data for the failing test rows entity
        # TODO add an utility function to do this from the test definition
        schema_test, _, conn_test = self.get_self_tests_db_conn(
            connection=DbParamsConnection["project_test"]
        )
        cursor = conn_test.cursor()
        if schema_test != schema_core:
            cursor.execute(
                f"""
                DROP SCHEMA IF EXISTS {schema_test} CASCADE;
                CREATE SCHEMA IF NOT EXISTS {schema_test};
            """
            )
            conn_test.commit()

        cursor.execute(
            f"""
            CREATE SCHEMA IF NOT EXISTS {schema_test};
            CREATE TABLE IF NOT EXISTS {schema_test}.tr_dot_model__fpview_registration_id10(
                uuid VARCHAR(300) PRIMARY KEY,
                value VARCHAR(1000) NOT NULL,
                primary_table_id_field VARCHAR(300)
            );
            INSERT INTO {schema_test}.tr_dot_model__fpview_registration_id10
            select * from
                (values ('patient_id1', '1', 'patient_id'), ('patient_id2', '2', 'patient_id'))
                x(uuid, value)
        """
        )
        conn_test.commit()

        # create data for the test view of failing rows
        test_summary, run_id = self.get_test_summary()
        test_rows = get_test_rows(
            test_summary,
            run_id,
            project_id="Muso",
            logger=setup_custom_logger("self_tests/output/test.log", logging.INFO),
        )
        self.assertListEqual(
            sorted(test_rows.id_column_value.to_list()),
            ["patient_id1", "patient_id2"],
        )

    @pytest.mark.skip("temporarily disabled")
    @patch("utils.configuration_utils._get_config_filename")
    def test_save_tests_to_db(self, mock_get_config_filename):
        """
        TODO to make it work
              1. take care of FK when inserting test_rows: configured_tests, runs, etc
              2. at this stage, test_summary has some counts of failing/passing rows
                    ==> improve helper functions
        Parameters
        ----------
        mock_get_config_filename

        Returns
        -------

        """
        mock_get_config_filename.side_effect = self.mock_get_config_filename

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
            project_id="Muso",
            logger=setup_custom_logger("self_tests/output/test.log", logging.INFO),
        )
