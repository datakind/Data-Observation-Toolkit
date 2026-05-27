-- make sure dates are valid. Can specifiy the earliest date a
-- particular column value can be within the schema test. The
-- latest possible date is the current date.
{% macro test_valid_date(model, column_name, earliest_date) %}

with validation as (
  select
    {{ column_name }} as date_field
  from {{ model }}
),

validation_errors as (
  select
    date_field
  from validation
  where date_field::date < '{{ earliest_date }}'::date
  or date_field::date > NOW()::date
)

select count(*)
from validation_errors

{% endmacro %}