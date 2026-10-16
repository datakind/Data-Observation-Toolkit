--CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DELETE FROM dot.test_results
WHERE test_id IN (
    SELECT test_id
    FROM dot.configured_tests
    WHERE project_id = 'UDTSProject'
);

DELETE FROM dot.test_results_summary
WHERE test_id IN (
    SELECT test_id
    FROM dot.configured_tests
    WHERE project_id = 'UDTSProject'
);

DELETE FROM dot.configured_tests
WHERE project_id = 'UDTSProject';

DELETE FROM dot.configured_entities
WHERE project_id = 'UDTSProject';


insert into dot.projects values ('UDTSProject','udts project',true,'data_staging_udts_01_synth_demo_gold_dhss_demo01_static',null,NOW(),NOW(),'Juwon') on conflict do nothing;

insert into dot.entity_categories values ('UDTS', 'Unified Data & Technology System') on conflict do nothing;

insert into dot.configured_entities 
values (
	'UDTSProject',
	'enrollment',
	'UDTS',
	$def${{ config(materialized='view') }}{% set schema = <schema> %}
SELECT
	e."EnrollmentIdentifier" as uuid,
	e.*
FROM {{ schema }}."Enrollment" as e
$def$,
	NOW(),
	NOW(),
	'Juwon'
);

insert into dot.configured_tests 
values (
	true,
	'UDTSProject',
	uuid_generate_v4(),
	'INCONSISTENT-1',
	2,
	'start date must be less than end date',
	'',
	'',
	'enrollment',
	'custom_sql',
	'',
	'',
	format(
		'{%s: %s}',
		to_json('query'::text),
		to_json(
			$query$
			select  *, 'uuid' AS primary_table_id_field
			from {{ ref('dot_model__enrollment') }}
			where ("EndDate" is null) or ("StartDate" > "EndDate")
			$query$::text
		)
	)::json,
	NOW(),
	NOW(),
	'admin'
);

insert into dot.configured_tests 
values (
	true,
	'UDTSProject',
	uuid_generate_v4(),
	'INCONSISTENT-1',
	2,
	'last active online date must be greater than end date',
	'',
	'',
	'enrollment',
	'custom_sql',
	'',
	'',
	format(
		'{%s: %s}',
		to_json('query'::text),
		to_json(
			$query$
			select *, 'uuid' AS primary_table_id_field from
			(select * 
			from {{ ref('dot_model__enrollment') }} e 
			where (e."LastActiveOnlineDate" is not null) and (e."StartDate" is not null)) as query
			where query."LastActiveOnlineDate" < query."StartDate"
			$query$::text
		)
	)::json,
	NOW(),
	NOW(),
	'admin'
);