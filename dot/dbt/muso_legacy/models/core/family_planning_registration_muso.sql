{{ config(materialized='view') }}

select *
from {{ ref('family_planning_registration') }}
