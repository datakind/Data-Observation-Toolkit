{{ config(materialized='view') }}
{% set schema = 'self_tests_public' %}
select DISTINCT airline
from {{ schema }}.flight_data   
