# How the DOT Works
The Data Observation Toolkit (DOT) leverages two powerful open-source frameworks—[DBT]( https://docs.getdbt.com/docs/introduction/) and [Great Expectations](https://greatexpectations.io/)—to define, develop, and execute data tests. These frameworks allow DOT to perform comprehensive and flexible data validation across various stages of the data pipeline.
1.	### DBT for Data Tests

      DBT (Data Build Tool) serves as the backbone for most of the testing in DOT. It provides robust support for foundational data tests, such as verifying column nullability, checking foreign key constraints, and validating uniqueness. These tests can be easily defined in DBT through simple entries in a YAML file, ensuring they are automated and repeatable.
      
      In addition to these base tests, DBT’s custom tests allow for more complex validations. For example, you can define custom SQL tests for checking the relationships between multiple columns or tables. These tests are written using SQL and Jinja templating, offering flexibility in handling sophisticated data validation scenarios.

2.	### Great Expectations for Advanced Testing

      While DBT handles most SQL-based data tests, Great Expectations] is integrated into DOT for tests that cannot be easily expressed in SQL. Great Expectations enables the implementation of Python-based tests, making it ideal for more advanced checks, such as inspecting statistical distributions, identifying outliers, or performing other data quality assessments that go beyond what SQL can capture.
      
      Great Expectations provides additional flexibility by supporting custom Python code for tests, allowing users to define complex validation logic that incorporates data science techniques or external data sources.
  
  By combining DBT’s SQL-centric approach with Great Expectations’ Python-based tests, DOT creates a comprehensive framework for both basic and advanced data validation. This ensures that data quality is consistently monitored, with tests addressing a wide range of data integrity issues across the pipeline.

---

# Configuring DOT
The following sections provide instructions for adding entities and tests to DOT directly in the DOT database. You can also use the DOT user interface for tests, for more details please see section see section [The DOT User Interface](#the-dot-user-interface). If you want to test DOT with health related data, please feel free to use this [fabricated dataset](https://docs.google.com/spreadsheets/d/1l6inpa6ykgUewC-MJkgrQwwc8HjUiTLLJFEDBtAMDB4/edit#gid=31188808) which resembles appointment information and contains some quality issues which DOT can highlight.

## How to add new entities
The DOT will run tests against user-defined views on the underlying data. These views are called "entities" and defined in table dot.configured_entities:

| Column            | Description                                                               |
| :---------------- | :------------------------------------------------------------------------ |
| entity_id         | Name of the entity e.g. ancview_danger_sign                               |
| entity_category   | Category of the entity e.g. anc => needs to be in `dot.entity_categories` |
| entity_definition | String for the SQL query that defines the entity                          |

For example, this would be an insert command to create ```ancview_danger_sign```:

```sql
INSERT INTO dot.configured_entities (project_id,entity_id,entity_category,entity_definition,date_added,date_modified,last_updated_by) VALUES('Project1', 
'ancview_danger_sign', 'anc', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}
```

```sql
select *
from {{ schema }}.ancview_danger_sign');
```

All entities use Jinja macro statements - the parts between { ... } - which the DOT uses to create the entity materialized views in the correct database location. Use the above format for any new entities you create.
The SQL for the view definition can be more complex than the example above, combining data from multiple underlying tables or views. For example:
```{{ config(materialized=''view'') }}```
```{% set schema = <schema> %}```

```sql
SELECT ap.*, ap.lmp as lmp_date, DATE_PART(''day'', reported - lmp) as days_since_lmp
FROM {{ schema }}.ancview_pregnancy ap
```
When you add a new entity to the configuration, take a look to the existing ```dot.entity_categories``` to associate your new entity to one of them. If you need to add a new category, the table ```dot.entity_categories``` has the following columns:

| Column          | Description                     |
| :-------------- | :------------------------------ |
| entity_category | Category of the entity e.g. anc |
| description     | A description of the category   |

An example of an insert statement would be:

```sql
INSERT INTO dot.entity_categories VALUES('anc', 'antenatal care');
```
## How to configure tests
Tests are defined in the table ```dot.configured_tests```. Each test has an associated test_type, a list of which can be found in table ```dot.test_types``` (see section "DOT Database Schema" below for more details on the full schema).To use one of these test types for a new test, insert a new row in dot.configured_tests.Here are the columns included in a test:

| Column               | Description                                                     |
| :------------------- | :-------------------------------------------------------------- |
| test_activated       | Whether the test is activated or not                            |
| project_id           | ID of the project, for example "`ScanProject1`"                 |
| test_id              | UUID of the test                                                |
| scenario_id          | ID of the scenario                                              |
| priority             | Priority level                                                  |
| description          | Description of the test                                         |
| impact               | Why the test is important                                       |
| proposed_remediation | How the issue in this test might be solved                      |
| entity               | The entity against which the test runs (check `entities` below) |
| test_type            | Test type                                                       |
| column_name          | The column in the table against which the test runs             |
| column_description   | Description of the above column                                 |
| test_parameters      | Any parameters the test takes in                                |
| date_added           | Date when the test was added                                    |
| date_modified        | Date when the test was last modified                            |
| last_updated_by      | Person who last updated the test                                |

The UUID in the above example will get overwritten with an automatically generated value. Also, your test must be unique for the project. If you get a key violation it's probably because that test already exists.
Test validation
Any insert of update of configured tests will call database function ```dot.test_validation```, as defined in [./db/dot/1-schema.sql](./db/dot/1-schema.sql). This function performs some basic validation to ensure test parameters are in an expected format. It is not infallable, if there are any issues with test parameters and tests do not execute, you can confirm this by looking at columns test_status and test_status_message in dot.test_results_summary.

### Example INSERT statements for adding a new test for each test type:

**Note:** In all of the following examples, the UUID in the insert statement will be replaced with an automatically generated one.
1.	**relationship**
```sql
'INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '0cdc9702-91e0-3499-b6f0-4dec12ad0f08', 'ASSESS-1', 3, '', '', '', 'ancview_pregnancy', 'relationships', 'uuid', '', $${"name": "danger_signs_with_no_pregnancy", "to": "ref('dot_model__ancview_danger_sign')", "field": "pregnancy_uuid"}$$, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```
2.	**unique**
```sql
INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '52d7352e-56ee-3084-9c67-e5ab24afc3a3', 'DUPLICATE-1', 3, '', '', '', 'ancview_pregnancy', 'unique', 'uuid', 'alternative index?', '', '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```
3.	**not_negative_string_column**
```sql
INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '8aca2bee-9e95-3f8a-90e9-153714e05367', 'INCONSISTENT-1', 3, '', '', '', 'ancview_pregnancy', 'not_negative_string_column', 'patient_age_in_years', '', $${"name": "patient_age_in_years"}$$, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```
4.	**not_null**
```sql
INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '549c0575-e64c-3605-85a9-70356a23c4d2', 'MISSING-1', 3, '', '', '', 'ancview_pregnancy', 'not_null', 'patient_id', '', '', '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```
5.	**accepted_values**
```sql
INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '935e6b61-b664-3eab-9d67-97c2c9c2bec0', 'INCONSISTENT-1', 3, '', '', '', 'ancview_pregnancy', 'accepted_values', 'fp_method_being_used', '', $${"values": ['oral mini-pill (progestogen)', 'male condom', 'female sterilization', 'iud', 'oral combination pill', 'implants', 'injectible']}$$, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```
6.	**possible_duplicate_forms**
```sql
INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '7f78de0e-8268-3da6-8845-9a445457cc9a', 'DUPLICATE-1', 3, '', '', '', 'ancview_pregnancy', 'possible_duplicate_forms', '', '', $${"table_specific_reported_date": "delivery_date", "table_specific_patient_uuid": "patient_id", "table_specific_uuid": "uuid"}$$, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```
7.	**associated_columns_not_null**
```sql
INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', 'd74fc600-31c3-307d-9501-5b7f6b09aff5', 'MISSING-1', 3, '', '', '', 'ancview_pregnancy', 'associated_columns_not_null', 'diarrhea_dx', 'diarrhea diagnosis', $${"name": "diarrhea_dx_has_duration", "col_value": True, "associated_columns": ['max_symptom_duration']}$$, '2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'your-name');
```
8.	**expect_similar_means_across_reporters**
```sql
INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '0cdc9702-91e0-3499-b6f0-4dec12ad0f08', 'BIAS-1', 3, 'Test for miscalibrated thermometer', '', '', 'ancview_pregnancy', 'expect_similar_means_across_reporters', 'child_temperature_pre_chw', '', '{"key": "reported_by","quantity": "child_temperature_pre_chw","form_name": "dot_model__iccmview_assessment","id_column": "reported_by"}', '2022-01-19 20:00:00.000 -0500', '2022-01-19 20:00:00.000 -0500', 'your-name');
```
9.	**expression_is_true**
```sql
INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', '3081f033-e8f4-4f3b-aea8-36f8c5df05dc', 'INCONSISTENT-1', 3, 'Wrong treatment/dosage arising from wrong age of children (WT-1)', '', '', 'ancview_pregnancy', 'expression_is_true', '', '', $${"name": "t_under_24_months_wrong_dosage", "expression": "malaria_act_dosage is not null", "condition": "(patient_age_in_months<24) and (malaria_give_act is not null)"}$$, '2022-02-14 19:00:00.000 -0500', '2022-02-14 19:00:00.000 -0500', 'your-name');
```
10.	**custom_sql**

Custom SQL queries require special case because they must have ```primary_table``` and ```primary_table_id_field``` specified within the SQL query as shown below:
```sql
INSERT INTO dot.configured_tests VALUES(TRUE, 'ScanProject1', 'c4a3da8f-32f4-4e9b-b135-354de203ca90', 'TREAT-1', 6, 'Test for new family planning method (NFP-1)', '', '', 'ancview_pregnancy', 'custom_sql', '', '',format('{%s: %s}', to_json('query'::text), to_json(query select a.patient_id, a.reported, a.fp_method_being_used, 'dot_model__fpview_registration' as primary_table, 'patient_id' as primary_table_id_field from {{ ref('dot_model__fpview_registration') }} a inner join ( select distinct patient_id, max(reported) reported from {{ ref('dot_model__fpview_registration') }} where fp_method_being_used in ('vasectomie','female sterilization') group by patient_id ) b on a.patient_id = b.patient_id and a.reported > b.reported and fp_method_being_used not in ('vasectomie','female sterilization') and fp_method_being_used not like '%condom%' query::text) )::json,'2021-12-23 19:00:00.000 -0500', '2021-12-23 19:00:00.000 -0500', 'Leah');
```
### Activating/Deactivating existing tests
Note that it's possible to deactivate tests, which can sometimes be useful for testing. To do this simply set test_activated=False in table dot.configured_tests. For example:
```sql
UPDATE dot.configured_tests 
SET test_activated=false 
WHERE test_id not in ('7db8742b-c20b-3060-93e2-614e35da2d4b','0f26d515-a70f-3758-8266-8da326d90eb6');
```


## Developing DOT

The DOT is open source so we encourage any development is done as part of that intiative. For reference this would
include code quality standards and self-tests, some details of which are provided below.

### Self-tests

The DOT runs some self-tests to check that its functions are running fine. If you are contributing to the project
by adding a new feature or solving a bug, please follow the following guidelines:
- find the existing tests applicable to the area that you are modifying
- add a few more relevant tests for your bugfix/improvement
- implement your changes until the test pass

#### Running self-tests

##### Using Docker

The Docker build provided above to run DOT, also includes self-test. So once you have the container running, all you
need to do is:

1. `exec -it dot /bin/bash`
2. `pytest dot/self_tests/unit`

##### On your local machine

Assuming you would like to run the tests locally, as preparation steps, you will need to:
- Create a local env for python via either venv or conda
- Make sure your Python version aligns with that in `.github/workflows/lint.yml`
- Create a conda environment using the `environment.yml` file at the root directory
- Prepare a postgres database that the tests can use (e.g. you can deploy a docker container and use it as a database
only, or you could use a local instance of a Postgres DB)
- Prepare a [dot_config.yml](dot/self_tests/data/base_self_test/dot_config.yml) at directory
`dot/self_tests/data/base_self_test` with the same structure as the [dot_config.yml](dot/config/example/dot_config.yml)
for the DOT; should look like something as follows (note that the config below points to DB in the docker container):
```YAML
dot:
  save_passed_tests: False
  output_schema_suffix: tests
dot_db:
  type: postgres
  host: localhost
  user: postgres
  pass: "{{ env_var('POSTGRES_PASSWORD') }}"
  port: 5433
  dbname: dot_db
  schema: self_tests_dot
  threads: 4
ScanProjec1_db:
  type: postgres
  host: localhost
  user: postgres
  pass: "{{ env_var('POSTGRES_PASSWORD') }}"
  port: 5433
  dbname: dot_db
  schema: self_tests_public
  threads: 4
```

And finally you can run the tests from a terminal as follows:
```bash
pytest dot/self_tests/unit
```

#### Additional notes

The Data Observation Toolkit (DOT) works with a few assumptions in terms of what an expectation should accept and return.

1. We create views out of the DOT results with Postgresql-specific syntax. If you're using any other database engine,
please adapt the query in [great_expectations.py](dot/utils/great_expectations.py).

2. An expectation accepts both column names and table names as arguments. Great Expectations generally has
table-agnostic suites running on specific single tables, but we're changing this model a bit because data integrity
queries often depend on more than one table. Therefore, a default empty dataset is added in the `batch_config.json`
for all custom expectations, and a relevant table name should be passed to the expectation in the suite definition.
The default dataset won't be read at all and is used as a placeholder.

3. Custom expectations are found in custom_expectations.py under plugins, it is recommended to follow their format and
to add your own custom expectations as methods of that same class.

4. The toolkit's post-processing step expects a few specific field in the output of the expectations
(refer to example custom expectations to see how they're implemented)