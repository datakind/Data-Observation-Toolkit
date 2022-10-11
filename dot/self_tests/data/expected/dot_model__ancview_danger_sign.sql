{{ config(materialized='view') }}
{% set schema = 'data_muso' %}

select *
from {{ schema }}.ancview_danger_sign
