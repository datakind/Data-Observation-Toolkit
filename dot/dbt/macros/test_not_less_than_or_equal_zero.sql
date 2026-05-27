-- test column values are not less than or equal to 0.
{% macro test_not_less_than_or_equal_zero(model, column_name) %}

select
  count(*)
from
  {{model}}
where
  {{column_name}} <= 0

{% endmacro %}