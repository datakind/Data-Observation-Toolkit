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
    uses_parameters BOOLEAN NOT NULL,
    uses_column BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dot.test_parameters_interface(
    test_type VARCHAR(300) NOT NULL,
    parameter VARCHAR(300) NOT NULL,
    parameter_type VARCHAR(300) CHECK(parameter_type IN ('entity any field', 'entity id field', 'entity columns boolean logic',
                                                         'view/table', 'entity date field', 'one of (hour, day, week)',
                                                         'entity numeric field', 'sql statement', 'list of values')),
    example VARCHAR(300) NOT NULL,
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
    active BOOLEAN,
    project_schema VARCHAR(300) NULL,
    contacts VARCHAR(1000) NULL,
    date_added TIMESTAMP WITH TIME ZONE NOT NULL,
    date_modified TIMESTAMP WITH TIME ZONE NOT NULL,
    last_updated_by VARCHAR(200) NOT NULL
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
  project_id VARCHAR(300) NOT NULL,
  entity_id UUID,
  entity_name VARCHAR(300),
  entity_category VARCHAR(300),
  entity_definition VARCHAR(4096),
  date_added TIMESTAMP WITH TIME ZONE NOT NULL,
  date_modified TIMESTAMP WITH TIME ZONE NOT NULL,
  last_updated_by VARCHAR(200) NOT NULL,
  Primary Key (entity_id),
  CONSTRAINT fk_entity_category
      FOREIGN KEY(entity_category)
      REFERENCES dot.entity_categories(entity_category),
  CONSTRAINT fk_project
      FOREIGN KEY(project_id)
	  REFERENCES dot.projects(project_id)
);

CREATE TABLE IF NOT EXISTS dot.configured_tests(
    test_activated BOOLEAN NOT NULL,
    project_id VARCHAR(300) NOT NULL references dot.projects on update cascade,
    test_id UUID PRIMARY KEY,
    scenario_id VARCHAR(300) NOT NULL references dot.scenarios on update cascade,
    priority INT NOT NULL CHECK (priority in (1,2,3,4,5,6,7,8,9,10)),
    description VARCHAR(1000) NOT NULL,
    impact VARCHAR(1000) NULL,
    proposed_remediation VARCHAR(1000) NULL,
    entity_id UUID NOT NULL references dot.configured_entities on update cascade,
    test_type VARCHAR(300) NOT NULL references dot.test_types on update cascade,
    column_name VARCHAR(300) NULL,
    column_description VARCHAR(1000) NULL,
    test_parameters JSONB NULL,
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

CREATE TABLE IF NOT EXISTS dot.configured_tests_parameters(
    test_id UUID PRIMARY KEY references dot.configured_tests on update cascade,
    parameter_type VARCHAR(300) CHECK(parameter_type IN ('function_argument','sql_statement')),
    parameter_name VARCHAR(300) NULL,
    parameter_value VARCHAR(300) NULL,
    CONSTRAINT test_id
      FOREIGN KEY(test_id)
	  REFERENCES dot.configured_tests(test_id)
);

CREATE TABLE IF NOT EXISTS dot.test_results(
  test_result_id VARCHAR(300) NOT NULL,
  run_id UUID,
  test_id UUID references dot.configured_tests on update cascade,
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
  test_id UUID references dot.configured_tests on update cascade,
  entity_id UUID references dot.configured_entities on update cascade,
  test_type VARCHAR(300) NOT NULL references dot.test_types on update cascade,
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

CREATE OR REPLACE FUNCTION dot.configured_tests_insert()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
declare
   KEY_STRING text;
BEGIN
   -- If you change how this UUID is generated, be sure to also change how it is created in get_test_id in /utils/utils.py
   KEY_STRING := new.project_id || new.test_type || new.entity_id || new.column_name || COALESCE(CAST(new.test_parameters AS VARCHAR),'');
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
declare
   KEY_STRING text;
BEGIN
   KEY_STRING := new.project_id || new.test_type || new.entity_id || new.column_name || COALESCE(CAST(new.test_parameters AS VARCHAR),'');
   NEW.test_id := uuid_generate_v3(uuid_ns_oid(), KEY_STRING);
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



CREATE OR REPLACE VIEW dot.test_type_parameters_json
AS
    SELECT
        test_type,
        CONCAT('{',replace(replace(string_agg(CONCAT('"' , parameter , '": "' , example, '"'), ', '),'"[','['),']"',']'),'}') as "json_sample"
    FROM
        dot.test_parameters_interface
    GROUP BY
        test_type;

CREATE OR REPLACE FUNCTION dot.get_test_result_data_record(entity varchar(300), id_col text, id_col_val text, results_schema text)
RETURNS table (j json) as $$
BEGIN
	RETURN QUERY EXECUTE 'SELECT row_to_json(dot_model__'|| entity || ') from ' || results_schema || '.dot_model__' || entity || ' WHERE ' || id_col || '=''' || id_col_val || '''';
END; $$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION dot.configured_entities_insert()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
declare
   KEY_STRING text;
BEGIN
   KEY_STRING := new.entity_name || new.entity_category || new.entity_definition;
   NEW.entity_id := uuid_generate_v3(uuid_ns_oid(), KEY_STRING);
   new.date_added := NOW();
   new.date_modified := NOW();
   RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION dot.configured_entities_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
declare
   KEY_STRING text;
   OLD_ENTITY_ID uuid;
   NEW_ENTITY_ID uuid;
BEGIN
   KEY_STRING := new.entity_name || new.entity_category || new.entity_definition;
   NEW.entity_id := uuid_generate_v3(uuid_ns_oid(), KEY_STRING);
   new.date_modified := NOW();
   RETURN NEW;
END;
$$;

CREATE TRIGGER configured_entities_insert_trigger
BEFORE INSERT ON dot.configured_entities
FOR EACH ROW EXECUTE PROCEDURE dot.configured_entities_insert() ;

CREATE TRIGGER configured_entities_update_trigger
BEFORE UPDATE ON dot.configured_entities
FOR EACH ROW EXECUTE PROCEDURE dot.configured_entities_update() ;

-- Utility function that returns JSON of all possible parameters. Used in UI to generate full field set
CREATE OR REPLACE FUNCTION dot.test_params_all_json()
RETURNS text
LANGUAGE plpgsql
AS $$
declare
   full_json text;
BEGIN
   full_json := (SELECT
                   -- CONCAT('{',replace(replace(string_agg(CONCAT('"' ,test_type, '%%%', parameter , '": "' , example, '"'), ', '),'"[','['),']"',']'),'}')
                   CONCAT('{',replace(replace(string_agg(CONCAT('"' ,parameter , '": "' , example, '"'), ', '),'"[','['),']"',']'),'}')
				 FROM
				    dot.test_parameters_interface);
   return full_json;
END;
$$;
