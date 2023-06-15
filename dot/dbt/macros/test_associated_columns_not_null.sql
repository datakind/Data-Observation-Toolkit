-- test the number of rows that are null in associated columns.
-- For instance if fever = yes then one of the associated
-- column is fever_duration.
{% macro test_associated_columns_not_null(model, associated_columns, name, condition='1=1', table_specific_uuid='uuid') %}

select
  array_agg({{ table_specific_uuid }})  as uuid_list -- postgres only?
from
  {{model}}
where
  {{condition}}
  and (
    {% for col in associated_columns %}
      {{col}} is null
      {% if not loop.last %}
        or
      {% endif %}
    {% endfor %}
  )
having count(*) > 0

{% endmacro %}
