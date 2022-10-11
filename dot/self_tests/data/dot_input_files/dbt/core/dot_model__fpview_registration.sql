{{ config(materialized='view') }}
{% set schema = 'self_tests_public' %}
select * from
(values ('patient-id1', '1'), ('patient_id2', '2'), ('patient_id3', '-3')) x(uuid, value)

