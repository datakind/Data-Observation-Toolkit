-- 1. Wipe the slate clean for rapid testing (Results MUST be deleted before Tests,
-- Tests before Entities)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
delete from dot.test_results
where
    test_id
    in (select test_id from dot.configured_tests where project_id = 'EduProject')
;
delete from dot.test_results_summary
where
    test_id
    in (select test_id from dot.configured_tests where project_id = 'EduProject')
;
delete from dot.configured_tests
where project_id = 'EduProject'
;
delete from dot.configured_entities
where project_id = 'EduProject'
;

-- 2. Ensure base projects and categories exist (using ON CONFLICT to prevent
-- duplicates)
INSERT INTO dot.projects (project_id, description, active, project_schema, date_added, date_modified, last_updated_by) 
VALUES ('EduProject', 'Educational Data System', 'true', 'data_dot_data_education', NOW(), NOW(), 'admin')
ON CONFLICT (project_id) DO NOTHING;

INSERT INTO dot.entity_categories VALUES('EDU','Education')
ON CONFLICT (entity_category) DO NOTHING;

INSERT INTO dot.test_types (test_type, library, description, scope, uses_parameters, uses_column)
VALUES ('expect_column_values_to_be_between', 'great_expectations', 'Test to confirm values are within a range', 'column', true, true)
ON CONFLICT (test_type) DO NOTHING;

-- 3. Insert Entities
insert into dot.configured_entities values('EduProject', 'students_data', 'EDU', 
'{{  config(materialized=''view'')  }}
{% set schema = <schema> %}
select * 
from {{  schema  }}.students ', NOW(), NOW(), 'admin');

insert into dot.configured_entities values('EduProject', 'enrollments_data', 'EDU', 
'{{  config(materialized=''view'')  }}
{% set schema = <schema> %}
select * 
from {{  schema  }}.enrollments ', NOW(), NOW(), 'admin');

insert into dot.configured_entities values('EduProject', 'excel_grades', 'EDU', 
'{{  config(materialized=''view'')  }}
{% set schema = <schema> %}
select * 
from {{  schema  }}.excel_grades ', NOW(), NOW(), 'admin');

-- 4. Insert Tests
-- dbt test (accepted_values)
insert into dot.configured_tests values(
true,
'EduProject',
'11111111-1111-1111-1111-111111111111',
 'INCONSISTENT-1', 
 3,
 'Disallowed student status entered',
 '',
 '',
 'students_data',
 'accepted_values',
 'status', 
 'status of student',
 $${"values":["Active","Inactive","Graduated"]}$$,
 NOW(),
 NOW(),
 'admin'
);

-- dbt custom sql test (conflict detection)
insert into dot.configured_tests values (
true, 'EduProject', '11111111-1111-1111-1111-111111111111', 'TREAT-1', 5, 'Custom sql test to check course', '', '', 'enrollments_data', 'custom_sql', '', '',
format('{%s:%s}', to_json('query'::text), to_json($query$ SELECT e.enrollment_id, 'dot_model__enrollments_data' as primary_table, 'enrollment_id' as primary_table_id_field, e.student_id, e.course_id, e.semester, e.dropped FROM {{ ref('dot_model__enrollments_data') }} e INNER JOIN ( SELECT student_id, course_id, semester FROM {{ ref('dot_model__enrollments_data') }} e WHERE dropped = FALSE GROUP BY student_id, course_id, semester HAVING COUNT(*) > 1 ) AS duplicates ON e.student_id = duplicates.student_id AND e.course_id = duplicates.course_id AND e.semester = duplicates.semester WHERE e.dropped = false $query$::text) )::json,
NOW(), NOW(), 'admin');