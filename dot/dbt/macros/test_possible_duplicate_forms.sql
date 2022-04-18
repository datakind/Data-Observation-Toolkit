-- Test to check if a patient was reported more than once in a specified period.
-- Input period parameter is database specific (https://hub.getdbt.com/dbt-labs/dbt_utils/0.1.13/)
--  Some valid values for PostgreSQL include 'day', 'week', 'hour' 
-- (See https://www.postgresql.org/docs/9.1/functions-datetime.html#FUNCTIONS-DATETIME-TRUNC)
-- If so, flag as possible duplicate form.
{% macro test_possible_duplicate_forms(model, table_specific_reported_date='reported', table_specific_patient_uuid='patient_uuid', table_specific_uuid='uuid', table_specific_period='hour', name='possible_duplicate_forms') %}

with records_per_patient_period as (
select
	date_trunc('{{ table_specific_period}}', {{ table_specific_reported_date }}::timestamp) as date_period,
	{{ table_specific_patient_uuid }} as patient_uuid_to_flag,
	count({{ table_specific_uuid }}) as number_of_records
FROM {{ model }}
group by 1, 2
),

possible_duplicate_combinations as (
select *
from records_per_patient_period
where number_of_records > 1
)

select array_agg({{ table_specific_uuid }})  as uuid_list -- postgres only?
from possible_duplicate_combinations pdc
left join {{ model }} m
on date_trunc('{{ table_specific_period}}', m.{{ table_specific_reported_date }}::timestamp) = pdc.date_period
and m.{{ table_specific_patient_uuid }} = pdc.patient_uuid_to_flag
having count(*) > 0

{% endmacro %}
