{{ config(materialized='view') }}

select *
from {{ ref('malnutrition_follow_up') }}
