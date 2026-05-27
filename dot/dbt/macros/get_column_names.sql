-- get column names from multiple relations.
{% macro get_column_names(schema, relation_prefix) %}

{% set column_names = [] %}
{% set relations = get_relations(schema, relation_prefix) %}

{% for relation in relations %}
{% set column_name = get_column_name(relation=relation, schema=schema, relation_prefix=relation_prefix) %}
{% do column_names.append(column_name) %}
{% endfor %}

{{ return(column_names) }}

{% endmacro %}