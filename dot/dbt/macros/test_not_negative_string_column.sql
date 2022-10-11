-- test to make sure that columns of string type that
-- represents an integer is not negative.
{% macro test_not_negative_string_column(model, column_name, name, description, table_specific_uuid='uuid') %}

select
  array_agg({{ table_specific_uuid }}) as uuid_list -- postgres only?
from
  {{model}}
where
  {{column_name}}::varchar like '-%'
having count(*) > 0

{% endmacro %}
