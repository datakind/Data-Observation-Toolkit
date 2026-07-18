-- Test to check if the same group key appears more than once in a specified period.
-- Input period parameter is database specific (https://hub.getdbt.com/dbt-labs/dbt_utils/0.1.13/)
--  Some valid values for PostgreSQL include 'day', 'week', 'hour'
-- (See https://www.postgresql.org/docs/9.1/functions-datetime.html#FUNCTIONS-DATETIME-TRUNC)
-- If so, flag as possible duplicate records.
{% macro test_possible_duplicate_forms(model, date_column='reported', group_column='patient_uuid', id_column='uuid', period='hour', name='possible_duplicate_records') %}

with records_per_group_period as (
select
	date_trunc('{{ period}}', {{ date_column }}::timestamp) as date_period,
	{{ group_column }} as group_key_to_flag,
	count({{ id_column }}) as number_of_records
FROM {{ model }}
group by 1, 2
),

possible_duplicate_combinations as (
select *
from records_per_group_period
where number_of_records > 1
)

select array_agg({{ id_column }})  as uuid_list -- postgres only?
from possible_duplicate_combinations pdc
left join {{ model }} m
on date_trunc('{{ period}}', m.{{ date_column }}::timestamp) = pdc.date_period
and m.{{ group_column }} = pdc.group_key_to_flag
having count(*) > 0

{% endmacro %}
