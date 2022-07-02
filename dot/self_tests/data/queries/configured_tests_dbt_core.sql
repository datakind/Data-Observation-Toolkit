-- required static data
INSERT INTO self_tests_dot.scenarios VALUES('MISSING-1', 'Missing fields', 'Data entry error', 'Form data entry error', 'Null fields', 'Blank fields');
INSERT INTO self_tests_dot.scenarios VALUES('INCONSISTENT-1', 'Inconsistent data', 'Data entry error', 'Form data entry error', 'Outliers', 'Jaundice alert=No when fever+jaundice; Incorrect LMP, wrong visit dates');

INSERT INTO self_tests_dot.test_types VALUES('not_negative_string_column', 'dbt', 'Test to confirm all positive', 'column', false, true);
INSERT INTO self_tests_dot.test_types VALUES('not_null', 'dbt', 'Test to confirm if null', 'column', false, true);

-- non static data -entities and tests +
INSERT INTO self_tests_dot.projects SELECT 'Muso', 'Muso project', true, 'public', null, '2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt';

INSERT INTO self_tests_dot.entity_categories VALUES('anc', 'antenatal care');
INSERT INTO self_tests_dot.entity_categories VALUES('fp', 'Family planning');

-- this entity has only an entity as it is normally defined; there no impact views in the test setup, thus no data to test
INSERT INTO self_tests_dot.configured_entities VALUES('Muso','66f5d13a-8f74-4f97-836b-334d97932781', 'ancview_pregnancy', 'anc', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select * from
(values (''patient-id1'', ''1''), (NULL, ''2'')) x(patient_id, value)','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');

CREATE SCHEMA IF NOT EXISTS self_tests_public;
CREATE TABLE self_tests_public.ancview_pregnancy (
    patient_id VARCHAR(300),
    value VARCHAR(300)
);
INSERT INTO self_tests_public.ancview_pregnancy
SELECT * FROM (values ('patient-id1', '1'), (NULL, '2')) x(patient_id, value);

INSERT INTO self_tests_dot.configured_tests VALUES(TRUE, 'Muso', '549c0575-e64c-3605-85a9-70356a23c4d2', 'MISSING-1', 3, 'Patient ID is not null', '', '', '3ed4d6ed-74b1-32cb-b74f-b51ebaa13294', 'not_null', 'patient_id', '', NULL, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Example');


INSERT INTO self_tests_dot.configured_entities VALUES('Muso','95bd0f60-ab59-48fc-a62e-f256f5f3e6de', 'fpview_registration', 'fp', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select * from
(values (''patient-id1'', ''1''), (''patient_id2'', ''2''), (''patient_id3'', ''-3'')) x(uuid, value)','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');

CREATE TABLE self_tests_public.fpview_registration (
    uuid VARCHAR(300),
    value VARCHAR(300)
);
INSERT INTO self_tests_public.fpview_registration
SELECT * FROM (values ('patient-id1', '1'), ('patient_id2', '2'), ('patient_id3', '-3')) x(uuid, value);

INSERT INTO self_tests_dot.configured_tests VALUES(TRUE, 'Muso', '549c0575-e64c-3605-85a9-70356a23c4d2', 'MISSING-1', 3, 'UUID is not null', '', '', '95bd0f60-ab59-48fc-a62e-f256f5f3e6de', 'not_null', 'uuid', '', NULL, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Example');
INSERT INTO self_tests_dot.configured_tests VALUES(TRUE, 'Muso', '8aca2bee-9e95-3f8a-90e9-153714e05367', 'INCONSISTENT-1', 5, 'value not negative', '', '', '95bd0f60-ab59-48fc-a62e-f256f5f3e6de', 'not_negative_string_column', 'value', '', $${"name": "value"}$$, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Example');
