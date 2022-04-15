{{ config(materialized='view') }}

select *
from {{ ref('malnutrition_registration') }}
