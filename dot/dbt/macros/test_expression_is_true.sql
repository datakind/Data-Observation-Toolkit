-- wrapper around dbt_utils.expression_is_true including the name
-- Commented out column as the expression determines that
{% test expression_is_true(model, expression, column_name=None, condition='1=1', name='do_set_name') %}
  {{ return(adapter.dispatch('test_expression_is_true', 'dbt_utils')(model, expression, '', condition)) }}
{% endtest %}
