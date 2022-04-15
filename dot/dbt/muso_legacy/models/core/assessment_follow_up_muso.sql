{{ config(materialized='view') }}

select *
from {{ ref('assessment_follow_up') }}
