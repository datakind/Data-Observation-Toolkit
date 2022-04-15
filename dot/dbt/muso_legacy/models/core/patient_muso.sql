{{ config(materialized='view') }}

-- Use the `ref` function to select from other models

select uuid as patient_id
  from contactview_metadata
 where type = 'person'
