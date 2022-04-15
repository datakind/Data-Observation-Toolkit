
-- dot.scenarios
INSERT INTO dot.scenarios VALUES('MISSING-1', 'Missing fields', 'Data entry error', 'Form data entry error', 'Null fields', 'Blank fields');
INSERT INTO dot.scenarios VALUES('INCONSISTENT-1', 'Inconsistent data', 'Data entry error', 'Form data entry error', 'Outliers', 'Jaundice alert=No when fever+jaundice; Incorrect LMP, wrong visit dates');
INSERT INTO dot.scenarios VALUES('INCONSISTENT-2', 'Inconsistent data', 'Data entry error', 'Time/Date incorrect on phone', 'Date logic issues, outliers', '');
INSERT INTO dot.scenarios VALUES('FAKE-1', 'Fake data', 'Data entry error', 'Fake data entered into forms', 'Outliers', '');
INSERT INTO dot.scenarios VALUES('DUPLICATE-1', 'Duplicate data', 'Data entry error', 'Duplicate data entered', 'Duplicate records', 'Multiple person records for the same person');
INSERT INTO dot.scenarios VALUES('BIAS-1', 'Miscalibrated instruments', 'Data entry error', 'Measurement bias', 'Outliers', 'Thermometer bias');
INSERT INTO dot.scenarios VALUES('BIAS-2', 'CHW Training issues', 'Data entry error', 'Measurement bias', 'Outliers', 'Breath counts not measured correctly');
INSERT INTO dot.scenarios VALUES('BUGS-1', 'Foreign keys errors', 'Software bugs', 'Database bugs', 'Foreign key errors', '');
INSERT INTO dot.scenarios VALUES('BUGS-2', 'Inconsistent field formats ', 'Software bugs', 'Database bugs', 'Inconsistent field formats ', 'During form updates/modifications the app developer changes the  response type of a field');
INSERT INTO dot.scenarios VALUES('BUGS-3', 'Data category errors ', 'Software bugs', 'Database bugs', 'Category distribution changes over time', '‘Male’ mixed with ‘man’ instead of all ‘Male''');
INSERT INTO dot.scenarios VALUES('BUGS-4', 'Field name changes', 'Software bugs', 'Application bugs', 'Field data changes over time', 'During form updates/modifications the app developer renames a form field name or changes the  response type of a field');
INSERT INTO dot.scenarios VALUES('BUGS-5', 'Incorrect metrics/indicators calculation/aggregation', 'Software bugs', 'Reporting bugs', 'Errors in calculated metrics', 'Technical debt complexity in pregnancy national metrics');
INSERT INTO dot.scenarios VALUES('MISSED-1', 'Missed person or patient', 'Process errors', 'Missed task', 'Houses in district not included', 'Unvisited household');
INSERT INTO dot.scenarios VALUES('MISSED-2', 'Missed assessment/report', 'Process errors', 'Missed task', 'Missed follow-up forms', 'Missed pregnancy; Missed delivery report');
INSERT INTO dot.scenarios VALUES('MISSED-3', 'Missed followup', 'Process errors', 'Missed task', 'Inconsistent patterns in follow-up data', '');
INSERT INTO dot.scenarios VALUES('MISSED-4', 'Missed referral visit', 'Process errors', 'Missed task', 'Missing referral visits', 'Patient referred but doesn''t attend');
INSERT INTO dot.scenarios VALUES('MISSED-5', 'Missed treatment', 'Process errors', 'Missed task', 'Inconsistencies in treatment data, outliers', 'No Malaria treatment after diagnosis; Underreporting immunization');
INSERT INTO dot.scenarios VALUES('MISSED-6', 'Missed CHW supervision', 'Process errors', 'Missed task', 'Missed supervision forms', '');
INSERT INTO dot.scenarios VALUES('MISSED-7', 'Missed family planning', 'Process errors', 'Missed task', 'No FP for relevant househould, outliers', '');
INSERT INTO dot.scenarios VALUES('FOLLOWUP-1', 'Unrealistically fast followup', 'Process errors', 'Incorrect followup', 'Unrealistically fast followups', '');
INSERT INTO dot.scenarios VALUES('MULTIEVENTS-1', 'Mutiple same day events', 'Process errors', 'Multiple events', 'Mutiple same day events', '');
INSERT INTO dot.scenarios VALUES('ASSESS-1', 'Inconsistent data', 'Process errors', 'Incorrect assessment', 'Outliers', 'Jaundice alert=No when fever+jaundice; ');
INSERT INTO dot.scenarios VALUES('TREAT-1', 'Incorrect treatment', 'Process errors', 'Incorrect treatment', 'Outliers', 'Drug protocol not followed for Malaria treatment; FP for people on tubal ligation, pregnant or had vasectomy');

-- dot.test_types
INSERT INTO dot.test_types VALUES('relationships', 'dbt', 'Test missing relationships between records', 'multi_table', 'name: danger_signs_with_no_pregnancy| to: ref(''pregnancy'')| field: uuid');
INSERT INTO dot.test_types VALUES('unique', 'dbt', 'Test to confirm uniqueness ', 'column', '');
INSERT INTO dot.test_types VALUES('not_negative_string_column', 'dbt', 'Test to confirm all positive', 'column', 'name: patient_age_in_years');
INSERT INTO dot.test_types VALUES('not_null', 'dbt', 'Test to confirm if null', 'column', '');
INSERT INTO dot.test_types VALUES('accepted_values', 'dbt', 'Test to confirm values adhere to specified list', 'column', 'values: [True, False]');
INSERT INTO dot.test_types VALUES('custom_sql', 'dbt', 'Custom SQL, if rows returned test failed', 'any', '""select
    reported,
    reported_by_parent as chw_uuid,
    count(*)
from {{ ref(''household_visit'') }}
group by 1, 2
having count(*) > 100""');
INSERT INTO dot.test_types VALUES('possible_duplicate_forms', 'dbt', 'Test to confirm duplicate records', 'single_table', 'table_specific_reported_date: reported| table_specific_patient_uuid: patient_id| table_specific_uuid: uuid');
INSERT INTO dot.test_types VALUES('associated_columns_not_null', 'dbt', 'Test to confirm related columns not null', 'column', '');
INSERT INTO dot.test_types VALUES('expect_similar_means_across_reporters', 'great_expectations', 'Test to compare means across reporters (eg of temperature)', 'column', '');
INSERT INTO dot.test_types VALUES('fake_expectation_for_test_purposes', 'great_expectations', 'Great expectation test test, ignore', 'column', '');
INSERT INTO dot.test_types VALUES('expression_is_true', 'dbt', 'Test to confirm a value of an expression given a condition', 'any', 'name: "t_referral_follow_up_negative"| expression: "not(treat_malnutrition and danger_sign)"| condition: "not(fu_ref_rec or fu_rec)"');


-- dot.test_parameters_interface
INSERT INTO dot.test_parameters_interface VALUES('relationships', 'name', 'function_argument', 'Name of the test');
INSERT INTO dot.test_parameters_interface VALUES('relationships', 'reference', 'function_argument', 'Referenced field to be checked if missing');
INSERT INTO dot.test_parameters_interface VALUES('relationships', 'field', 'function_argument', 'Field being checked');
INSERT INTO dot.test_parameters_interface VALUES('not_negative_string_column', 'name', 'function_argument', 'Name of column to be check3ed for non-negative values');
INSERT INTO dot.test_parameters_interface VALUES('accepted_values', 'values', 'function_argument', 'List of accepted values for the field being checked');
INSERT INTO dot.test_parameters_interface VALUES('possible_duplicate_forms', 'table_specific_reported_date', 'function_argument', 'Column which indicates when form created');
INSERT INTO dot.test_parameters_interface VALUES('possible_duplicate_forms', 'table_specific_patient_uuid', 'function_argument', 'Column which holds to patient uuid');
INSERT INTO dot.test_parameters_interface VALUES('possible_duplicate_forms', 'table_specific_uuid', 'function_argument', 'UUID for records in the table (form) being checked');
INSERT INTO dot.test_parameters_interface VALUES('custom_sql', '', 'sql_statement', 'Custom SQL to use to determine test fails, SQL is defined in columns test_parameter');
INSERT INTO dot.test_parameters_interface VALUES('expression_is_true', 'name', 'function_argument', 'Name of the test');
INSERT INTO dot.test_parameters_interface VALUES('expression_is_true', 'condition', 'function_argument', 'Where clause of rows that are going to be checked');
INSERT INTO dot.test_parameters_interface VALUES('expression_is_true', 'expression', 'function_argument', 'If not true, the row fails the test');

-- dot.scenario_test_types
INSERT INTO dot.scenario_test_types VALUES('MISSING-1', 'associated_columns_not_null');
INSERT INTO dot.scenario_test_types VALUES('MISSING-1', 'not_null');
INSERT INTO dot.scenario_test_types VALUES('INCONSISTENT-1', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('INCONSISTENT-1', 'not_negative_string_column');
INSERT INTO dot.scenario_test_types VALUES('INCONSISTENT-1', 'accepted_values');
INSERT INTO dot.scenario_test_types VALUES('INCONSISTENT-1', 'expression_is_true');
INSERT INTO dot.scenario_test_types VALUES('INCONSISTENT-2', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('FAKE-1', 'accepted_values');
INSERT INTO dot.scenario_test_types VALUES('FAKE-1', 'expect_similar_means_across_reporters');
INSERT INTO dot.scenario_test_types VALUES('DUPLICATE-1', 'unique');
INSERT INTO dot.scenario_test_types VALUES('DUPLICATE-1', 'possible_duplicate_forms');
INSERT INTO dot.scenario_test_types VALUES('DUPLICATE-1', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('BIAS-1', 'expect_similar_means_across_reporters');
INSERT INTO dot.scenario_test_types VALUES('BIAS-2', 'expect_similar_means_across_reporters');
INSERT INTO dot.scenario_test_types VALUES('BUGS-1', 'relationships');
--INSERT INTO dot.scenario_test_types VALUES('BUGS-2', '');
--INSERT INTO dot.scenario_test_types VALUES('BUGS-3', '');
--INSERT INTO dot.scenario_test_types VALUES('BUGS-4', '');
--INSERT INTO dot.scenario_test_types VALUES('BUGS-5', '');
INSERT INTO dot.scenario_test_types VALUES('MISSED-1', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('MISSED-2', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('MISSED-3', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('MISSED-4', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('MISSED-5', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('MISSED-6', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('MISSED-7', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('FOLLOWUP-1', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('MULTIEVENTS-1', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('ASSESS-1', 'custom_sql');
INSERT INTO dot.scenario_test_types VALUES('TREAT-1', 'custom_sql');

