{{ config(materialized='view') }}
{% set schema = 'self_tests_public' %}
select * from
(values ('patient-id1', '1'), (NULL, '2')) x(patient_id, value)
