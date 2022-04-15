{{ config(materialized='view') }}

with source_data as (

    -- code below ignores mute and unmute dates; could be improved to include start and end dates
    -- however not sure if the entity health center makes sense for all deployments?
    select
        health_center_uuid,
        family_uuid as household_id
    from muting_table
    group by 1, 2

)

select *
from source_data
