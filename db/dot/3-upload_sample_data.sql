INSERT INTO dot.projects SELECT 'Muso', 'Muso project', true, 'public', null, '2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt';
INSERT INTO dot.projects SELECT 'Brac', 'Brac project',  true, 'public', null, '2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt';

-- entity categories
INSERT INTO dot.entity_categories VALUES('anc', 'Antenatal care');
INSERT INTO dot.entity_categories VALUES('fp', 'Family planning');
INSERT INTO dot.entity_categories VALUES('core', 'Core entities such as chw, patient, etc');
INSERT INTO dot.entity_categories VALUES('iccm', 'Integrated community case management on child mortality');
INSERT INTO dot.entity_categories VALUES('mn', 'Malnutitrion');
INSERT INTO dot.entity_categories VALUES('pnc', 'Postnatal care');

-- configured entities - sql definitions of DBT base objects
INSERT INTO dot.configured_entities VALUES('b05f1f9c-2176-46b0-8e8f-d6690f696b9b', 'ancview_danger_sign', 'anc', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.ancview_danger_sign','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('66f5d13a-8f74-4f97-836b-334d97932781', 'ancview_delivery', 'anc', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.ancview_delivery','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('638ed10b-3a2f-4f18-9ca1-ebf23563fdc0', 'ancview_pregnancy', 'anc', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select ap.*,
        ap.lmp as lmp_date,
        DATE_PART(''day'', reported - lmp) as days_since_lmp
from {{ schema }}.ancview_pregnancy ap','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('8ccab0bf-383e-4e41-9437-2b1c5007ba80', 'ancview_pregnancy_visit', 'anc', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.ancview_pregnancy_visit','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('f41fe8ee-ee1c-49dd-ae3d-c473daf441d5', 'chv', 'core', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
with source_data as (
    select distinct
        reported_by,
        reported_by_parent
    from
        {{ schema }}.iccmview_assessment
)
select *
from source_data','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('6ba8075f-6f35-4ff1-be3a-4c75d0884bf4', 'fpview_follow_up', 'fp', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.fpview_follow_up','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('95bd0f60-ab59-48fc-a62e-f256f5f3e6de', 'fpview_registration', 'fp', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.fpview_registration','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('173793ff-491d-4c73-8d0b-3903a82d3796', 'hhview_visits', 'core', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select *
from {{ schema }}.hhview_visits','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('baf349c9-c919-40ff-a611-61ddc59c2d52', 'iccmview_assessment', 'iccm', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
-- select *
-- from iccmview_assessment
select
  ia.*,
  ua.child_temperature::real ,
  ua.child_temperature_pre_chw::real ,
  ua.child_temperature_pre_chw_retake::real,
  fa.patient_age_in_months::integer,
  fa.malaria_act_dosage,
  fa.malaria_give_act
from
  {{ schema }}.useview_assessment ua,  -- should be maybe a left join with iccmview_assessment
  {{ schema }}.iccmview_assessment ia,
  {{ schema }}.formview_assessment fa  -- should be maybe a left join with iccmview_assessment
where
  ia.uuid = ua.uuid
  and fa.uuid = ua.uuid','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('50f31569-f2fc-4dc6-af49-4268381e7c13', 'iccmview_assessment_follow_up', 'iccm', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
with source_data as (
    select * from {{ schema }}.iccmview_assessment_follow_up
)
select *
from source_data','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('d0645118-bd68-4eba-8ead-fad114be86b7', 'mnview_follow_up', 'mn', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select * from {{ schema }}.mnview_follow_up','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('57a9fd48-51d8-4dc0-bbd1-a6e0405696cd', 'mnview_registration', 'mn', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
select * from {{ schema }}.mnview_registration','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('fade2413-8504-443f-b161-1c5470fc1df3', 'patient', 'core', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
with source_data as (
    select
        uuid,
        reported
      from {{ schema }}.contactview_metadata
     where type = ''person''
)
select *
from source_data','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');
INSERT INTO dot.configured_entities VALUES('eaea6e4c-a455-4f04-bb36-4bab0f6ba1a3', 'pncview_visits', 'pnc', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
with source_data as (
    select * from {{ schema }}.pncview_visits
)
select *
from source_data','2021-12-07 00:00:00+00','2021-12-07 00:00:00+00','Matt');

-- Note these UUIDs get reset by the trigger
-- Note these UUIDs get reset by the trigger
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '549c0575-e64c-3605-85a9-70356a23c4d2', 'MISSING-1', 3, 'Patient ID is not null', '', '', '6a4d1463-281e-34b4-9620-609756dbbaf5', 'not_null', 'patient_id', '', NULL, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Example');
-- ?
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '8aca2bee-9e95-3f8a-90e9-153714e05367', 'INCONSISTENT-1', 5, 'Patient age is not negative', '', '', '569b9515-eb80-39ab-a537-f6ef571dee64', 'not_negative_string_column', 'patient_age_in_years', '', '{"name": "patient_age_in_years"}', '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Example');
-- ?
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '52d7352e-56ee-3084-9c67-e5ab24afc3a3', 'DUPLICATE-1', 3, 'UUID is not unique', '', '', '1739a0b0-5a61-391f-a3b6-0aab7e2fe0b9', 'unique', 'uuid', '', NULL, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Example');
-- ?
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '935e6b61-b664-3eab-9d67-97c2c9c2bec0', 'INCONSISTENT-1', 3, 'Disallowed FP methods entered in form', '', '', '569b9515-eb80-39ab-a537-f6ef571dee64', 'accepted_values', 'fp_method_being_used', '', $${"values": ["oral mini-pill (progestogen)", "male condom", "female sterilization", "iud", "oral combination pill", "implants", "injectible"]}$$, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Example');
-- ??
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '0cdc9702-91e0-3499-b6f0-4dec12ad0f08', 'ASSESS-1', 3, 'Pregnancy danger signs with no pregnancy record', '', '', '5a6b486d-87fa-347e-888e-0b6c11db7cd7', 'relationships', 'pregnancy_uuid', '', $${"name": "danger_signs_with_no_pregnancy", "to": "ref('dot_model__ancview_pregnancy')", "field": "uuid"}$$, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Example');
-- MDSF-2
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '8b3f974c-16f2-4048-920c-f28086b9b411', 'MISSED-3', 9, 'Missing danger sign  follow up (MDSF-2)', '', '', '6a4d1463-281e-34b4-9620-609756dbbaf5', 'relationships', 'uuid', '', $${"name": "missed_danger_sign_followup", "to": "ref('dot_model__ancview_danger_sign')", "field": "pregnancy_uuid", "where": "danger_sign_at_reg=True" }$$, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Leah');
-- MAVF-1
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '1305077b-718d-4a0c-b08c-2bb57f104357', 'MISSED-3', 8, 'Expectant women should be followed up by a health worker (MAVF-1)', '', '', '6a4d1463-281e-34b4-9620-609756dbbaf5', 'relationships', 'uuid', '', $${"name": "missed_anc_visit_followup", "to": "ref('dot_model__ancview_pregnancy_visit')", "field": "pregnancy_uuid"}$$, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Leah');
-- GE-1
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '0cdc9702-91e0-3499-b6f0-4dec12ad0f18', 'BIAS-1', 6, 'Test for miscalibrated thermometer (GE-1)', '', '', '658f3ea9-d9ed-3dc2-8477-c5cc68bb44eb', 'expect_similar_means_across_reporters', 'child_temperature_pre_chw', '', $${"key": "reported_by","quantity": "child_temperature_pre_chw","form_name": "dot_model__iccmview_assessment","id_column": "reported_by"}$$, '2022-01-19 20:00:00.000 -0500', '2022-01-19 20:00:00.000 -0500', 'Medic unknown');
-- ??
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '62665f35-bff9-4304-a496-76619c895a19', 'MISSED-1', 3, 'Patient with no assessment', '', '', 'e8f3abe6-a25e-3581-b8dc-8f9919269689', 'custom_sql', '', '',
format('{%s: %s}',
    to_json('query'::text),
    to_json($query$
        with patient_no_assessment as (select
        patient.uuid as uuid,
        patient.reported as patient_reported
    from {{ ref('dot_model__patient') }} patient
    left join {{ ref('dot_model__iccmview_assessment') }} assessment
    on patient.uuid = assessment.patient_id
    where assessment.patient_id is null
)
select
    distinct uuid,
    'patient' as primary_table,
    'uuid' as primary_table_id_field
from patient_no_assessment pna
where (CURRENT_DATE::date - pna.patient_reported::date) >= 1095
    $query$::text)
)::json, '2022-02-01 19:00:00.000 -0500', '2022-02-01 19:00:00.000 -0500', 'Example');
-- WT-1
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '3081f033-e8f4-4f3b-aea8-36f8c5df05dc', 'INCONSISTENT-1', 8, 'Wrong treatment/dosage arising from wrong age of children (WT-1)', '', '', '658f3ea9-d9ed-3dc2-8477-c5cc68bb44eb', 'expression_is_true', '', '', $${"name": "t_under_24_months_wrong_dosage", "expression": "malaria_act_dosage is not null", "condition": "(patient_age_in_months<24) and (malaria_give_act is not null)"}$$, '2022-02-14 19:00:00.000 -0500', '2022-02-14 19:00:00.000 -0500', 'MoH');
-- NFP-1
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', 'c4a3da8f-32f4-4e9b-b135-354de203ca90', 'TREAT-1', 6, 'Test for new family planning method (NFP-1)', '', '', '569b9515-eb80-39ab-a537-f6ef571dee64', 'custom_sql', '', '',
format('{%s: %s}',
    to_json('query'::text),
    to_json($query$
        select
            a.patient_id,
            a.reported,
            a.fp_method_being_used,
            'dot_model__fpview_registration' as primary_table,
            'patient_id' as primary_table_id_field
        from {{ ref('dot_model__fpview_registration') }} a
            inner join
            (
                select distinct
                patient_id,
                max(reported) reported
                from {{ ref('dot_model__fpview_registration') }}
                where fp_method_being_used in ('vasectomie','female sterilization')
                group by patient_id
            ) b on a.patient_id = b.patient_id and a.reported > b.reported
            and fp_method_being_used not in ('vasectomie','female sterilization')
            and fp_method_being_used not like '%condom%'
    $query$::text)
)::json,'2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Leah');
-- LMP-1
INSERT INTO dot.configured_tests VALUES (TRUE, 'Muso', '3081f033-e8f4-4f3b-aea8-36f8c5df05ec','INCONSISTENT-1',9,'Erroneous LMP Date (LMP-1)','10','Put a validation on the application that no LMP should be less than 4 weeks at the time of registration','6a4d1463-281e-34b4-9620-609756dbbaf5','custom_sql','','',
format('{%s: %s}',
    to_json('query'::text),
    to_json($query$
        select
                ap.uuid,
                ap.days_since_lmp,
                cnt.appearances as tot_appearances,
                'dot_model__ancview_pregnancy' as primary_table,
                'uuid' as primary_table_id_field
        from (
        select
                round(ap.days_since_lmp::float) days_since_lmp,
                  count(*) appearances
                from {{ ref('dot_model__ancview_pregnancy') }} ap
            where ap.lmp_date is not null and round(ap.days_since_lmp::float)<=28
            group by round(ap.days_since_lmp::float)
        ) cnt
        join
        {{ ref('dot_model__ancview_pregnancy') }} ap
        on cnt.days_since_lmp = ap.days_since_lmp
        order by round(ap.days_since_lmp::float)
    $query$::text)
)::json,'2022-02-15 20:00:00.000 -0500','2022-02-15 20:00:00.000 -0500','Leah');
-- LMP-2
-- Deactivating, as logic needs further refinement with Medic
-- INSERT INTO dot.configured_tests VALUES (TRUE, 'Muso', '3081f033-e8f4-4f3b-aea8-36f8c5df05dc','INCONSISTENT-1',8,'LMP Date at Beginning of Month (LMP-2)','10','Use days/weeks since LMP instead of months as this may be much closer to the actual LMP instead of months since LMP','638ed10b-3a2f-4f18-9ca1-ebf23563fdc0','custom_sql','','','select
--         ap.uuid,
--         ap.days_since_lmp,
--         cnt.proportion as tot_proportion,
--         ''dot_model__ancview_pregnancy'' as primary_table,
--         ''uuid'' as primary_table_id_field
-- from
-- (
--         select round(days_since_lmp::float) days_since_lmp,
--                 count(*)*100.0/sum(count(*)) over() proportion
--         from {{ ref(''dot_model__ancview_pregnancy'') }} ap
--         where lmp_date is not null
--         group by round(days_since_lmp::float)
-- ) cnt
-- join
-- {{ ref(''dot_model__ancview_pregnancy'') }} ap
-- on cnt.days_since_lmp = ap.days_since_lmp
-- where cnt.proportion>1','2022-02-15 20:00:00.000 -0500','2022-02-15 20:00:00.000 -0500','Leah');
-- PDF-1
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', 'baadb20f-7efb-3ebd-bfc8-57561466f310', 'DUPLICATE-1', 7, 'Some CHWs may mistakenly register a pregnancy more than once (PDF-1)', '', '', '6a4d1463-281e-34b4-9620-609756dbbaf5', 'possible_duplicate_forms', '', '', $${"table_specific_reported_date": "reported", "table_specific_patient_uuid": "patient_id", "table_specific_uuid": "uuid", "table_specific_period": "day"}$$, '2021-12-23 19:00:00.000 -0500', '2022-03-21 19:00:00.000 -0500', 'Leah');
-- PDF-2
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '36d33837-bd92-370a-963a-264a4d5b2bac', 'DUPLICATE-1', 6, 'Same day repeat cases for pregnancy visits (PDF-2)', '', '', 'a35cf3bc-e054-3c85-acd7-0b46ac4ece77', 'possible_duplicate_forms', '', '', $${"table_specific_reported_date": "reported", "table_specific_patient_uuid": "patient_id", "table_specific_uuid": "uuid", "table_specific_period": "day"}$$, '2021-12-23 19:00:00.000 -0500', '2022-03-21 19:00:00.000 -0500', 'Mourice');
-- PDF-3
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', 'ab59ada1-5cfd-3f1b-9549-aa93c3d575ae', 'DUPLICATE-1', 6, 'Same day repeat cases for family planning duplicate records (PDF-3)', '', '', '1739a0b0-5a61-391f-a3b6-0aab7e2fe0b9', 'possible_duplicate_forms', '', '', $${"table_specific_reported_date": "reported", "table_specific_patient_uuid": "patient_id", "table_specific_uuid": "uuid", "table_specific_period": "day"}$$, '2021-12-23 19:00:00.000 -0500', '2022-03-21 19:00:00.000 -0500', 'Mourice');
-- PDF-4
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '68ea1480-b6b0-33b1-adc4-71a843ecb437', 'DUPLICATE-1', 8, 'FP same day repeat cases - some within a short time interval (PDF-4)', '', '', '569b9515-eb80-39ab-a537-f6ef571dee64', 'possible_duplicate_forms', '', '', $${"table_specific_reported_date": "reported", "table_specific_patient_uuid": "patient_id", "table_specific_uuid": "uuid", "table_specific_period": "day"}$$, '2021-12-23 19:00:00.000 -0500', '2022-03-21 19:00:00.000 -0500', 'Leah');
-- PDF-5
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', 'eeafde14-6515-30dc-a51c-c5079209bcdb', 'DUPLICATE-1', 5, 'Multiple forms of the same activity submitted in a day (PDF-5)', '', '', '658f3ea9-d9ed-3dc2-8477-c5cc68bb44eb', 'possible_duplicate_forms', '', '', $${"table_specific_patient_uuid": "patient_id", "table_specific_uuid": "uuid", "table_specific_period": "day"}$$, '2021-12-23 19:00:00.000 -0500', '2022-03-21 19:00:00.000 -0500', 'Medic unknown');
-- PDF-6
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '2660b519-9946-3e12-9b92-46d4321b1d56', 'DUPLICATE-1', 5, 'Multiple forms of the same activity submitted in a day (PDF-6)', '', '', '1cb91f66-9b67-328f-b5c5-3ab78435e99d', 'possible_duplicate_forms', '', '', $${"table_specific_patient_uuid": "patient_id", "table_specific_uuid": "uuid", "table_specific_period": "day"}$$, '2021-12-23 19:00:00.000 -0500', '2022-03-21 19:00:00.000 -0500', 'Medic unknown');
-- PDF-7
INSERT INTO dot.configured_tests VALUES(TRUE, 'Muso', '99ac4950-13df-3777-bd27-923e74be9dcb', 'DUPLICATE-1', 7, 'Multiple reporting of specific PNC visits (PDF-7)', '', '', '33accce9-9367-3d11-8272-a7fba412717c', 'possible_duplicate_forms', '', '', $${"table_specific_patient_uuid": "patient_id", "table_specific_uuid": "uuid", "table_specific_period": "day"}$$, '2021-12-23 19:00:00.000 -0500', '2022-03-21 19:00:00.000 -0500', 'Leah');

-- Required for Airflow deployment and easier access to uynderlying data
-- CREATE SCHEMA data_musoapp;
-- CREATE MATERIALIZED VIEW data_musoapp.dot__test_results_latest_with_data
-- AS
-- SELECT
--    tr.*,
--    dot.get_test_result_data_record(ce.entity_name, tr.id_column_name, tr.id_column_value,'data_musoapp')
-- FROM
--    dot.scenarios s,
--    dot.configured_tests ct,
--    dot.configured_entities ce,
--    dot.test_results tr,
--    dot.run_log rl,
--    (
--     SELECT MAX(run_start) AS last_run_date
--     FROM dot.run_log where project_id = 'Muso'
--   ) last_run
-- WHERE
--   s.scenario_id=ct.scenario_id AND
--   tr.test_id=ct.test_id and
--   ce.entity_id=ct.entity_id and
--   tr.run_id = rl.run_id
-- WITH DATA;

COMMIT;
