-- required static data
INSERT INTO self_tests_dot.scenarios VALUES('DUPLICATE-1', 'Duplicate data', 'Data entry error', 'Duplicate data entered', 'Duplicate records', 'Multiple person records for the same person');

INSERT INTO self_tests_dot.test_types VALUES('possible_duplicate_forms', 'dbt', 'Test to confirm duplicate records', 'single_table', 'table_specific_reported_date: reported| table_specific_patient_uuid: patient_id| table_specific_uuid: uuid');

INSERT INTO self_tests_dot.test_parameters_interface VALUES('possible_duplicate_forms', 'table_specific_reported_date', 'function_argument', 'Column which indicates when form created');
INSERT INTO self_tests_dot.test_parameters_interface VALUES('possible_duplicate_forms', 'table_specific_patient_uuid', 'function_argument', 'Column which holds to patient uuid');
INSERT INTO self_tests_dot.test_parameters_interface VALUES('possible_duplicate_forms', 'table_specific_uuid', 'function_argument', 'UUID for records in the table (form) being checked');

INSERT INTO self_tests_dot.scenario_test_types VALUES('DUPLICATE-1', 'possible_duplicate_forms');

-- non static data -entities and tests +
INSERT INTO self_tests_dot.projects SELECT 'Muso', 'Muso project', '2021-12-07 00:00:00+00', 'true', 'public';

INSERT INTO self_tests_dot.entity_categories VALUES('anc', 'antenatal care');

INSERT INTO self_tests_dot.configured_entities VALUES('66f5d13a-8f74-4f97-836b-334d97932781', 'ancview_delivery', 'anc', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}

select *
from {{ schema }}.ancview_delivery');

INSERT INTO self_tests_dot.configured_tests VALUES(TRUE, 'Muso', '7f78de0e-8268-3da6-8845-9a445457cc9a', 'DUPLICATE-1', 3, '', '', '', '66f5d13a-8f74-4f97-836b-334d97932781', 'possible_duplicate_forms', '', '', 'table_specific_reported_date: delivery_date| table_specific_patient_uuid: patient_id| table_specific_uuid: uuid', '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Lorenzo');
