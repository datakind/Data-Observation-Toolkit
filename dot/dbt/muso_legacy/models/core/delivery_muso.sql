{{ config(materialized='view') }}

-- Use the `ref` function to select from other models

select *
from delivery_modified_muso -- TODO figure out if this includes all deliveries
