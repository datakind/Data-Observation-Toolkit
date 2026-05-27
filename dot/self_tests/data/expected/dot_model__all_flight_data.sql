{{ config(materialized='view') }}
{% set schema = 'schema_project' %}
select *
from {{ schema }}.flight_data 
