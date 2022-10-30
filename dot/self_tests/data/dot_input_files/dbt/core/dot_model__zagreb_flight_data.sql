{{ config(materialized='view') }}
{% set schema = 'self_tests_public' %}
select *
from {{ schema }}.flight_data WHERE origin_airport='Zagreb airport'    
