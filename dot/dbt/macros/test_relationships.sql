-- This modification makes it possible to create downstream views
-- of failing test records by avoiding name collisions between
-- columns in the resulting view.
{% macro test_relationships(model, to, field,  where, table_specific_uuid='uuid') %}

{% set column_name = kwargs.get('column_name', kwargs.get('from')) %}

select array_agg(from_uuid) as uuid_list -- postgres only?
from (
    select {{ table_specific_uuid }} as from_uuid, {{ column_name }} as from_column_id from {{ model }}
    {{ where }}
) as from_model
left join (
    select {{ field }} as to_id from {{ to }}
) as to_model on to_model.to_id = from_model.from_column_id
where from_model.from_column_id is not null
  and to_model.to_id is null
having count(*) > 0

{% endmacro %}