-- get relations by prefix string.
{% macro get_relations(schema, relation_prefix) %}
{{ return(dbt_utils.get_relations_by_prefix(schema, relation_prefix)) }}
{% endmacro %}