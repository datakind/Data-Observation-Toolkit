-- test to make sure the column values are all valid values.
{% macro test_no_impossible_values(model, column_name, values, name) %}

select
  count(*)
from
  {{model}}
where
  {{column_name}} in {{values}}

{% endmacro %}