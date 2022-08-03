-- non static data -entities and tests +

-- remove all tests created in `configured_tests_sample.sql`
DELETE FROM self_tests_dot.configured_tests;

-- NOTE this is identical to `configured_tests_sample.sql`, line 11, but adding `id_column_name` to value `id_column`
INSERT INTO self_tests_dot.configured_tests
(test_activated, project_id, test_id, scenario_id, priority, description, impact, proposed_remediation, entity_id, test_type, column_name, column_description, id_column_name, test_parameters, date_added, date_modified, last_updated_by)
VALUES(TRUE, 'Muso', '7f78de0e-8268-3da6-8845-9a445457cc9a', 'DUPLICATE-1', 3, '', '', '', 'adc007dd-2407-3dc2-95a7-002067e741f9', 'possible_duplicate_forms', '', '', 'id_column',
$${"table_specific_uuid": "uuid", "table_specific_period": "day", "table_specific_patient_uuid": "patient_id", "table_specific_reported_date": "delivery_date"}$$
, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Lorenzo');

-- NFP-1
-- NOTE this is identical to `configured_tests_sample.sql`, line 22, but adding `id_column_name` to value `id_column`
INSERT INTO self_tests_dot.configured_tests
(test_activated, project_id, test_id, scenario_id, priority, description, impact, proposed_remediation, entity_id, test_type, column_name, column_description, id_column_name, test_parameters, date_added, date_modified, last_updated_by)
VALUES(TRUE, 'Muso', 'c4a3da8f-32f4-4e9b-b135-354de203ca70', 'TREAT-1', 5, 'Test for new family planning method (NFP-1)', '', '', '52aa8e99-5221-3aac-bca5-b52b80b90929', 'custom_sql', '', '', 'patient_id',
$${"query": "SELECT patient_id as primary_table_id_field, 'dot_model__fpview_registration' as primary_table, value FROM {{ ref('dot_model__fpview_registration') }} a LIMIT 2"}$$
, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Leah');
