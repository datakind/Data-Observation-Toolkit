CREATE SCHEMA dot;
-- CREATE SCHEMA data;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS dot.scenarios(
    scenario_id VARCHAR(300) PRIMARY KEY,
    scenario VARCHAR(1000) NOT NULL,
    cause VARCHAR(1000) NOT NULL,
    cause_sub_category VARCHAR(1000) NOT NULL,
    symptoms VARCHAR(1000) NOT NULL,
    example VARCHAR(1000) NOT NULL
);

CREATE TABLE IF NOT EXISTS dot.test_types(
    test_type VARCHAR(300) PRIMARY KEY,
    library VARCHAR(300) NOT NULL,
    description VARCHAR(1000) NOT NULL,
    scope VARCHAR(300) CHECK(scope in ('column','single_table', 'multi_table','any')),
    example_test_parameters VARCHAR(1000) NULL
);

CREATE TABLE IF NOT EXISTS dot.test_parameters_interface(
    test_type VARCHAR(300) NOT NULL,
    parameter VARCHAR(300) NULL,
    parameter_type VARCHAR(300) CHECK(parameter_type IN ('function_argument','sql_statement')),
    description VARCHAR(1000) NOT NULL,
    UNIQUE (test_type, parameter),
    CONSTRAINT fk_test_type
      FOREIGN KEY(test_type)
	  REFERENCES dot.test_types(test_type)
);

CREATE TABLE IF NOT EXISTS dot.scenario_test_types(
    scenario_id VARCHAR(300) NOT NULL,
    test_type VARCHAR(300) NOT NULL,
    UNIQUE (scenario_id, test_type),
    CONSTRAINT fk_scenario_id
      FOREIGN KEY(scenario_id)
	  REFERENCES dot.scenarios(scenario_id),
    CONSTRAINT fk_test_type
      FOREIGN KEY(test_type)
	  REFERENCES dot.test_types(test_type)
);

CREATE TABLE IF NOT EXISTS dot.projects(
    project_id VARCHAR(300) PRIMARY KEY,
    description VARCHAR(1000) NOT NULL,
    created_on TIMESTAMP WITH TIME ZONE NOT NULL,
    active BOOLEAN,
    project_schema VARCHAR(300) NULL,
    contacts VARCHAR(1000) NULL
);

CREATE TABLE IF NOT EXISTS dot.run_log (
    run_id UUID PRIMARY KEY,
    project_id VARCHAR(300)  NOT NULL,
    run_start TIMESTAMP WITH TIME ZONE NOT NULL,
    run_finish TIMESTAMP WITH TIME ZONE NULL,
    run_status VARCHAR(300) CHECK(run_status in ('Running','Failed', 'Finished')),
    run_error VARCHAR(3000) NULL,
    UNIQUE (run_id, project_id),
    CONSTRAINT fk_project
      FOREIGN KEY(project_id)
	  REFERENCES dot.projects(project_id)
);

CREATE TABLE IF NOT EXISTS dot.entity_categories (
  entity_category VARCHAR(300),
  description VARCHAR(1000),
  Primary Key (entity_category)
);

CREATE TABLE IF NOT EXISTS dot.configured_entities (
  entity_id UUID,
  entity_name VARCHAR(300),
  entity_category VARCHAR(300),
  entity_definition VARCHAR(4096),
  Primary Key (entity_id),
  CONSTRAINT fk_entity_category
      FOREIGN KEY(entity_category)
      REFERENCES dot.entity_categories(entity_category)
);

CREATE TABLE IF NOT EXISTS dot.configured_tests(
    test_activated BOOLEAN NOT NULL,
    project_id VARCHAR(300) NOT NULL,
    test_id UUID PRIMARY KEY,
    scenario_id VARCHAR(300) NOT NULL,
    priority INT NOT NULL CHECK (priority in (1,2,3,4,5,6,7,8,9,10)),
    description VARCHAR(1000) NOT NULL,
    impact VARCHAR(1000) NULL,
    proposed_remediation VARCHAR(1000) NULL,
    entity_id UUID NOT NULL,
    test_type VARCHAR(300) NOT NULL,
    column_name VARCHAR(300) NULL,
    column_description VARCHAR(1000) NULL,
    test_parameters VARCHAR(1000) NULL,
    date_added TIMESTAMP WITH TIME ZONE NOT NULL,
    date_modified TIMESTAMP WITH TIME ZONE NOT NULL,
    last_updated_by VARCHAR(200) NOT NULL,
    CONSTRAINT fk_scenario_id
      FOREIGN KEY(scenario_id)
	  REFERENCES dot.scenarios(scenario_id),
	CONSTRAINT fk_project
      FOREIGN KEY(project_id)
	  REFERENCES dot.projects(project_id),
	CONSTRAINT fk_test_types
      FOREIGN KEY(test_type)
	  REFERENCES dot.test_types(test_type),
	CONSTRAINT fk_configured_entities
	  FOREIGN KEY(entity_id)
	  REFERENCES dot.configured_entities(entity_id)
);

CREATE TABLE IF NOT EXISTS dot.test_results(
  test_result_id VARCHAR(300) NOT NULL,
  run_id UUID,
  test_id UUID,
  entity_id UUID,
  status TEXT,
  view_name VARCHAR(300) NULL,
  id_column_name TEXT,
  id_column_value TEXT,
  Primary Key (test_result_id, run_id, test_id),
  CONSTRAINT fk_test_id
      FOREIGN KEY(test_id)
	  REFERENCES dot.configured_tests(test_id),
  CONSTRAINT fk_run_id
      FOREIGN KEY(run_id)
	  REFERENCES dot.run_log(run_id)
);

CREATE TABLE IF NOT EXISTS dot.test_results_summary (
  run_id UUID,
  test_id UUID,
  entity_id UUID,
  test_type VARCHAR(300) NOT NULL,
  column_name VARCHAR(300) NULL,
  test_parameters VARCHAR(1000) NULL,
  test_status TEXT,
  test_status_message TEXT,
  failed_tests_view VARCHAR(300) NULL,
  failed_tests_view_sql TEXT NULL,
  rows_total INT NULL,
  rows_failed INT NULL,
  rows_passed INT null,
  Primary Key (run_id, test_id),
  CONSTRAINT fk_test_id
      FOREIGN KEY(test_id)
	  REFERENCES dot.configured_tests(test_id),
  CONSTRAINT fk_test_type
      FOREIGN KEY(test_type)
	  REFERENCES dot.test_types(test_type),
  CONSTRAINT fk_run_id
      FOREIGN KEY(run_id)
	  REFERENCES dot.run_log(run_id)
);


CREATE OR REPLACE FUNCTION dot.test_validation(test_type text, test_parameters text, column_name text, entity_id UUID)
RETURNS boolean as $$
DECLARE
 validation_status boolean;
 entity_id_in UUID; -- to get around ambiguity
begin
	entity_id_in := entity_id;
    CASE
        WHEN test_type = 'custom_sql' THEN
            -- Enforce mandatory fields in custom_sql select statement
            CASE
               WHEN test_parameters ~ 'primary_table[$ ",'']' AND
		            test_parameters ~ 'primary_table_id_field' THEN
		          SELECT TRUE INTO validation_status;
		       else
		          RAISE NOTICE '%', test_parameters;
		          SELECT FALSE INTO validation_status;
		          RAISE EXCEPTION 'primary_table and primary_table_id_field must be in fields of custom_sql SQL statement';
		    END CASE;
		WHEN test_type = 'accepted_values' then
		    CASE
               WHEN test_parameters ~ '^values:\s?\[.*\]' THEN
		          SELECT TRUE INTO validation_status;
		       ELSE
		          SELECT FALSE INTO validation_status;
		          RAISE EXCEPTION  'accepted_values test parameters must be: values:[<LIST>] ';
		    END CASE;
	    WHEN test_type = 'not_negative_string_column' then
		    CASE
               WHEN test_parameters ~ '^name:' THEN
		          SELECT TRUE INTO validation_status;
		       ELSE
		          SELECT FALSE INTO validation_status;
		          RAISE EXCEPTION  'not_negative_string_column test parameters must be: name:<NAME> ';
		    END CASE;
	   WHEN test_type = 'relationships' then
		    CASE
               WHEN test_parameters ~ '^name:.*?\|\s?to:\s?ref\(.*?\)\|\s?field:' THEN
		          SELECT TRUE INTO validation_status;
		       ELSE
		          SELECT FALSE INTO validation_status;
		          RAISE EXCEPTION  'relationships test parameters must be: name: <TEST NAME>| to: ref(''<RELATED TABLE/view>'')| field:<FIELD THAT LINKS THEM>';
		    END CASE;
	   WHEN test_type = 'expect_similar_means_across_reporters' then
		    CASE
               WHEN test_parameters ~ '^\{"key":\s?".*?",".*?":\s?".*?","form_name":\s?".*?","id_column":\s?".*?"\}' THEN
		          SELECT TRUE INTO validation_status;
		       ELSE
		          SELECT FALSE INTO validation_status;
		          RAISE EXCEPTION  'expect_similar_means_across_reporters test parameters must be: {"key": "<UNIQUE ID FIELD>","quantity": "<COLUMN THE MEAN IS FROM>","form_name": "<MODEL VIEW>","id_column": "<ID COLUMN>"}';
		    END CASE;
	   WHEN test_type = 'expression_is_true' then
		    CASE
               WHEN test_parameters ~ '^name:\s?".*?"\|\s?expression:\s?".*?"\|\s?condition:\s?"' THEN
		          SELECT TRUE INTO validation_status;
		       ELSE
		          SELECT FALSE INTO validation_status;
		          RAISE EXCEPTION  'expression_is_true test parameters must be: name: "<TEST DESCRIPTOR>"| expression: "<EXPRESSION>"| condition: "<CONDITION>"';
		    END CASE;
	   WHEN test_type = 'possible_duplicate_forms' then
		    CASE
               WHEN test_parameters ~ 'table_specific_.*?:.*?\|\s?table_specific_.*?:.*?\|\s?table_specific_period:' THEN
		          SELECT TRUE INTO validation_status;
		       ELSE
		          SELECT FALSE INTO validation_status;
		          RAISE NOTICE '%', test_parameters;
		          RAISE EXCEPTION 'possible_duplicate_forms test parameters must be: table_specific_patient_uuid: <UNIQUE PATIENT ID COLUMN NAME>| table_specific_uuid: <TABLE UUID COLUMN NAME>| table_specific_period: <PERIOD, eg day>';
		    END CASE;
	   WHEN test_type = 'not_null' or test_type = 'unique' then
		    case
		       -- Make sure column is in entity view list of columns
               WHEN column_name IN (
                  SELECT
	                 c.column_name
	              FROM
	                 information_schema.columns c,
	                 dot.configured_entities ce
	              WHERE
	                 c.table_name = ce.entity_name and
	                 ce.entity_id=entity_id_in) THEN
		          SELECT TRUE INTO validation_status;
		       ELSE
		          SELECT FALSE INTO validation_status;
		          RAISE EXCEPTION 'You must specify a column in the entity view for test type not_null';
		    END CASE;
        ELSE
          SELECT FALSE into validation_status;
          RAISE EXCEPTION  'Unknown test_type %', test_type;
    END CASE;
	RETURN validation_status;
END; $$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION dot.test_validation_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
  validation_status boolean;
BEGIN
	SELECT dot.test_validation(new.test_type, new.test_parameters, new.column_name, new.entity_id) INTO validation_status;
	if validation_status != true then
		RAISE EXCEPTION 'Test parameters validation failed';
	end if;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION dot.test_validation_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
  validation_status boolean;
BEGIN
	SELECT dot.test_validation(new.test_type, new.test_parameters, new.column_name, new.entity_id) INTO validation_status;
	if validation_status != true then
		RAISE EXCEPTION 'Test parameters validation failed';
	end if;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_test_parameters_validation_trigger
AFTER INSERT OR UPDATE ON dot.configured_tests
FOR EACH ROW EXECUTE PROCEDURE dot.test_validation_trigger_function();

-- TODO these will be added to self-tests
-- select dot.test_validation('possible_duplicate_forms','table_specific_patient_uuid: patient_id| table_specific_uuid: uuid| table_specific_period: day');
-- select dot.test_validation('possible_duplicate_forms','table_specific_patient_uuid: patient_id| tabXle_specific_uuid: uuid| table_specific_period: day');
-- select dot.test_validation('expression_is_true','name: "t_under_24_months_wrong_dosage"| expression: "malaria_act_dosage is not null"| condition: "(patient_age_in_months<24) and (malaria_give_act is not null)"');
-- select dot.test_validation('expression_is_true','name: "t_under_24_months_wrong_dosage"| exprXession: "malaria_act_dosage is not null"| condition: "(patient_age_in_months<24) and (malaria_give_act is not null)"');
-- select dot.test_validation('expect_similar_means_across_reporters','{"key": "reported_by","quantity": "child_temperature_pre_chw","form_name": "dot_model__iccmview_assessment","id_column": "reported_by"}');
-- select dot.test_validation('expect_similar_means_across_reporters','{"key": "reported_by","quantity": "child_temperature_pre_chw","form_name": "dot_model__iccmview_assessment","id_cXolumn": "reported_by"}');
-- select dot.test_validation('relationships','name: danger_signs_with_no_pregnancy| to: ref(''dot_model__ancview_pregnancy'')| field: uuid');
-- select dot.test_validation('relationships','name: danger_signs_with_no_pregnancy| to: ref(''dot_model__ancview_pregnancy'')| fiXeld: uuid');
-- select dot.test_validation('not_negative_string_column', 'name:patient_age_in_years');
-- select dot.test_validation('not_negative_string_column', 'namXe:patient_age_in_years');
-- select dot.test_validation('accepted_values', 'values: [dog]');
-- select dot.test_validation('accepted_values', 'valuXXes: [dog]');
-- select dot.test_validation('custom_sql', 'select 1 as primary_table  primary_table_id_field from table');
-- select dot.test_validation('custom_sql', 'select 1 as prXXimary_table  primary_table_id_field from table');
-- select dot.test_validation('custom_sql', 'select 1 as primary_table  priXXmary_table_id_field from table');

CREATE OR REPLACE FUNCTION dot.configured_tests_insert()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
declare
   KEY_STRING text;
BEGIN
   -- If you change how this UUID is generated, be sure to also change how it is created in get_test_id in /utils/utils.py
   KEY_STRING := new.project_id || new.test_type || new.entity_id || new.column_name || new.test_parameters;
   NEW.test_id := uuid_generate_v3(uuid_ns_oid(), KEY_STRING);
   new.date_added := NOW();
   new.date_modified := NOW();
   RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION dot.configured_tests_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
   new.date_modified := NOW();
   RETURN NEW;
END;
$$;

CREATE TRIGGER configured_tests_insert_trigger
BEFORE INSERT ON dot.configured_tests
FOR EACH ROW EXECUTE PROCEDURE dot.configured_tests_insert() ;

CREATE TRIGGER configured_tests_update_trigger
BEFORE UPDATE ON dot.configured_tests
FOR EACH ROW EXECUTE PROCEDURE dot.configured_tests_update() ;

CREATE TABLE IF NOT EXISTS dot.remediation_log(
    test_id UUID PRIMARY KEY,
    remediation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    remediation_by UUID NOT NULL,
    remediation_type Text NOT NULL,
    CONSTRAINT fk_test_id
      FOREIGN KEY(test_id)
	  REFERENCES dot.configured_tests(test_id)
);

CREATE OR REPLACE FUNCTION dot.get_test_result_data_record(entity varchar(300), id_col text, id_col_val text, results_schema text)
RETURNS table (j json) as $$
BEGIN
	RETURN QUERY EXECUTE 'SELECT row_to_json(dot_model__'|| entity || ') from ' || results_schema || '.dot_model__' || entity || ' WHERE ' || id_col || '=''' || id_col_val || '''';
END; $$ LANGUAGE 'plpgsql';


