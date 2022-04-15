-- test to check if a patient was reported more than once in an hour.
-- If so flag as possible duplicate form.
{% macro test_possible_duplicate_forms(model, table_specific_reported_date='reported', table_specific_patient_uuid='patient_uuid', table_specific_uuid='uuid', name='possible_duplicate_forms') %}

with records_per_patient_hour as (
select
	date_trunc('hour', {{ table_specific_reported_date }}::timestamp) as date_hour,
	{{ table_specific_patient_uuid }} as patient_uuid_to_flag,
	count({{ table_specific_uuid }}) as number_of_records
FROM {{ model }}
group by 1, 2
),

possible_duplicate_combinations as (
select *
from records_per_patient_hour
where number_of_records > 1
)

select array_agg({{ table_specific_uuid }})  as uuid_list -- postgres only?
from possible_duplicate_combinations pdc
left join {{ model }} m
on date_trunc('hour', m.{{ table_specific_reported_date }}::timestamp) = pdc.date_hour
and m.{{ table_specific_patient_uuid }} = pdc.patient_uuid_to_flag
having count(*) > 0

{% endmacro %}
