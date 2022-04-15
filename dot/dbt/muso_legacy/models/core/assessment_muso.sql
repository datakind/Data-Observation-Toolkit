{{ config(materialized='view') }}

-- Use the `ref` function to select from other models

select *
from iccmview_assessment_modified_muso
