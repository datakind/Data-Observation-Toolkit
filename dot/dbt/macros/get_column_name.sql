-- get column name from a relation.
{% macro get_column_name(relation, schema, relation_prefix) %}

{% set base_column = relation | string %}
{% set strip_col = base_column.split('.')[-1] %}

{% set column_name = strip_col | replace(relation_prefix ~ "_", "") | replace("\"","") %}

-- Debugging purposes. Can Comment out or switch to info=False to not print to stdout.
{{ log("(get_column_name macro output) Column name: " ~ column_name, info=True) }}
{{ return(column_name) }}
{% endmacro %}