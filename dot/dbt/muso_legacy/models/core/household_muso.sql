{{ config(materialized='view') }}

-- Use the `ref` function to select from other models

select parent_uuid as household_id
  from contactview_metadata
 where type = 'person'
 group by parent_uuid
