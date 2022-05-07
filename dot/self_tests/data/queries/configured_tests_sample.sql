-- required static data
INSERT INTO self_tests_dot.scenarios VALUES('DUPLICATE-1', 'Duplicate data', 'Data entry error', 'Duplicate data entered', 'Duplicate records', 'Multiple person records for the same person');
INSERT INTO self_tests_dot.scenarios VALUES('TREAT-1', 'Incorrect treatment', 'Process errors', 'Incorrect treatment', 'Outliers', 'Drug protocol not followed for Malaria treatment; FP for people on tubal ligation, pregnant or had vasectomy');

INSERT INTO self_tests_dot.test_types VALUES('possible_duplicate_forms', 'dbt', 'Test to confirm duplicate records', 'single_table', 'table_specific_reported_date: reported| table_specific_patient_uuid: patient_id| table_specific_uuid: uuid');
INSERT INTO self_tests_dot.test_types VALUES('custom_sql', 'dbt', 'Custom SQL, if rows returned test failed', 'any', '""select 1""');

INSERT INTO self_tests_dot.test_parameters_interface VALUES('possible_duplicate_forms', 'table_specific_reported_date', 'function_argument', 'Column which indicates when form created');
INSERT INTO self_tests_dot.test_parameters_interface VALUES('possible_duplicate_forms', 'table_specific_patient_uuid', 'function_argument', 'Column which holds to patient uuid');
INSERT INTO self_tests_dot.test_parameters_interface VALUES('possible_duplicate_forms', 'table_specific_uuid', 'function_argument', 'UUID for records in the table (form) being checked');

INSERT INTO self_tests_dot.scenario_test_types VALUES('DUPLICATE-1', 'possible_duplicate_forms');
INSERT INTO self_tests_dot.scenario_test_types VALUES('TREAT-1', 'custom_sql');

-- non static data -entities and tests +
INSERT INTO self_tests_dot.projects SELECT 'Muso', 'Muso project', '2021-12-07 00:00:00+00', 'true', 'public';

INSERT INTO self_tests_dot.entity_categories VALUES('anc', 'antenatal care');
INSERT INTO self_tests_dot.entity_categories VALUES('fp', 'Family planning');

-- this entity has only an entity as it is normally defined; there no impact views in the test setup, thus no data to test
INSERT INTO self_tests_dot.configured_entities VALUES('66f5d13a-8f74-4f97-836b-334d97932781', 'ancview_delivery', 'anc', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}

select *
from {{ schema }}.ancview_delivery');

-- same as above, this configured test cannot be run
INSERT INTO self_tests_dot.configured_tests VALUES(TRUE, 'Muso', '7f78de0e-8268-3da6-8845-9a445457cc9a', 'DUPLICATE-1', 3, '', '', '', '66f5d13a-8f74-4f97-836b-334d97932781', 'possible_duplicate_forms', '', '', 'table_specific_reported_date: delivery_date| table_specific_patient_uuid: patient_id| table_specific_uuid: uuid| table_specific_period: day', '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Lorenzo');

INSERT INTO self_tests_dot.configured_entities VALUES('95bd0f60-ab59-48fc-a62e-f256f5f3e6de', 'fpview_registration', 'fp', 'select * from
(values (''patient-id1'', ''1''), (''patient_id2'', ''2''), (''patient_id3'', ''3'')) x(patient_id, value)
');

-- NFP-1
INSERT INTO self_tests_dot.configured_tests VALUES(TRUE, 'Muso', 'c4a3da8f-32f4-4e9b-b135-354de203ca70', 'TREAT-1', 5, 'Test for new family planning method (NFP-1)', '', '', '95bd0f60-ab59-48fc-a62e-f256f5f3e6de', 'custom_sql', '', '', '
  SELECT
      patient_id as primary_table_id_field,
      ''dot_model__fpview_registration'' as primary_table,
      value
    FROM {{ ref(''dot_model__fpview_registration'') }} a
    LIMIT 2', '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Leah');
