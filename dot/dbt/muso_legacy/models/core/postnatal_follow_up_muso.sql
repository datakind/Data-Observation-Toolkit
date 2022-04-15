{{ config(materialized='view') }}

select *
from {{ ref('postnatal_follow_up') }}
