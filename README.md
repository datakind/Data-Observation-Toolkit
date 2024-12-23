![License](https://img.shields.io/badge/License-MIT-blue.svg)   ![Airflow Version](https://img.shields.io/badge/Airflow-2.2.4-blue)  ![Docker Image Version](https://img.shields.io/docker/v/apache/airflow/latest)  


# The Data Observation Toolkit (DOT)
In 2019, the United Nations Statistical Commission highlighted the critical role of accurate health data, stating, _“Every misclassified or unrecorded death is a lost opportunity to ensure other mothers and babies do not die in the same way. When it comes to health, better data can be a matter of life and death.”_ In response, **DataKind** developed DOT to increase trust in public health data, which is essential for equitable, data-driven health service delivery and optimized policy responses. DOT was created in collaboration with our global network of frontline health partners, including Ministries of Health, frontline health workers, and funders, all working together to strengthen health systems worldwide.
You can read more of this initiative in the articles below:
  -	[Pathways to Increasing Trust in Public Health Data](https://chance.amstat.org/2021/09/pathways/ "Pathways to Increasing Trust in Public Health Data")
  -	[Empowering Health Worker and Community Health Systems: Data Integrity and the Future of Intelligent Community Health Systems in Uganda](https://www.datakind.org/blog/empowering-health-workers-and-community-health-systems "Empowering Health Worker and Community Health Systems: Data Integrity and the Future of Intelligent Community Health Systems in Uganda")
  -	[Harnessing the power of data science in healthcare](https://anchor.fm/medxtekafrica/episodes/Ep19---Harnessing-the-power-of-data-science-in-healthcare-e1iijkm "Harnessing the power of data science in healthcare")
  -	[How Data Empowers Health Workers—and Powers Health Systems](https://chwi.jnj.com/news-insights/how-data-empowers-health-workers-and-powers-health-systems "How Data Empowers Health Workers—and Powers Health Systems")

The **Data Observation Toolkit (DOT)** is designed to monitor data and flag potential issues related to data integrity. It can identify problems such as missing or duplicate data, inconsistencies, outliers, and even domain-specific issues like missed follow-up medical treatments after diagnosis. DOT features a user-friendly interface for easily configuring powerful tools like the **DBT** and **Great Expectations** libraries, along with a built-in database for storing and classifying monitoring results.
The primary goal of DOT is to make data monitoring more accessible, allowing users to ensure high-quality data without requiring extensive technical expertise. – Below is a high overview of the tool and how is architected:
 <figure style="text-align:center;">
   <figcaption> DOT high overview </figcaption>
   <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/e650c78dc73b3842766d87d74f56701adb4019ff/images/dot.png" alt=" dot_overview " />
</figure>

<figure style="text-align:center;">
   <figcaption>DOT Architecture</figcaption>
   <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/e650c78dc73b3842766d87d74f56701adb4019ff/images/dot_architecture.png" alt="dot_acrh" />
</figure>

### General Configuration Pre-requisites:
To run DOT you will need to:
1.	Install Python [3.8.9](https://www.python.org/downloads/release/python-389/)  
2.	Install the necessary python packages by running the following commands in your terminal ([Additional information Mac/Linux terminal](https://support.apple.com/guide/terminal/open-or-quit-terminal-apd5265185d-f365-44cb-8b09-71a064a42125/mac#:~:text=On%20your%20Mac%2C%20do%20one,%2C%20then%20double%2Dclick%20Terminal.), [additional information Windows terminal](https://learn.microsoft.com/en-us/windows/terminal/)):
     - `pip install gdown`
     - `pip install python-on-whales`
3.	Install [Docker desktop](https://www.docker.com/products/docker-desktop/). First make sure you have checked the [Docker prerequisites](https://github.com/datakind/medic_data_integrity/tree/main/docker#pre-requisites). We recommend using at least 4GB memory which can be set in the docker preferences, but this can vary depending on the volume of data being tested
4.	If running on a Mac M1/M2 chip, install [Rosetta](https://support.apple.com/en-us/HT211861) and set export DOCKER_DEFAULT_PLATFORM=linux/amd64 in the terminal where you will run the instructions below
5.	(Windows Users only) Need to install WSL for Linux on Windows Pcs

Alternatively, you can use the provided  [environment.yml](./environment.yml) if you have [miniconda](https://docs.conda.io/en/latest/miniconda.html)  installed.

_After completing the software prerequisites for your operating system, **download or clone the DOT repository** to your computer. **You will need this repository for all the setups listed below.**_

 ### Configuration (work in progress)
The following sections provide step-by-step instructions for configuring various components of DOT:
-	[Getting Started with DOT](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/07a44ca01526679912a04e0f20bb6364134cdaf7/documentation_DOT/gettingstartedDOT.md)
-	[Setting Up the Docker Environment and Running DOT](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/e95231bdaf4c8410633b298ac246173b061dbe52/documentation_DOT/setuandrunDOTonDocker.md)
-	[Deploying DOT to Airflow](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/72a3bb7a36fbfc69b621180fd52034dc99d1ee86/documentation_DOT/airflowdeployment.md)
- [Configuring the DOT Database](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/b70d3e044858387443698354b0c4253a6b618b17/documentation_DOT/configuringDOTdb.md)
- [DBT for DOT](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/3c59ddd5c284bc07dc8428e039655827cb736ad5/documentation_DOT/DBTforDOT.md)
- [Configuring DOT](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/a22c4858caf890bd3fbb4a6d98e9aa12c38cbd4e/documentation_DOT/configuringDOT.md)
-	[Developing the Appsmith UI](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/d9845f8228bb147af7f28f7a300a68012e9b51ed/documentation_DOT/developingappsmith.md)
-	[Advanced Topics](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/cb6796d15e46c209e8d08b0d3984bfb6cb9d262d/documentation_DOT/AdavanceTopics.md#adding-more-projects-to-airflow)


### Sample data
Explore [these comprehensive datasets](https://drive.google.com/drive/folders/12tyTqYNNNpDZxQKMQqv7FVOCq18LCurQ?usp=sharing), including global COVID-19 data, U.S. childhood obesity records, and datasets ranging from 1,000 to over a million patient entries, along with a synthetic dataset demonstrating DOT's capabilities with frontline health data.

## Guidelines for adding new tests
*	Existing tests are at [the self-tests folder](dot/self_tests/unit)
*	All tests extend the [test base class](dot/self_tests/unit/base_self_test_class.py) that
    -	facilitates the import of modules under test
    -	recreates a directory in the file system for the test outputs
    -	provides a number of function for supporting tests that access the database, mocking the config files to point to the test [dot_config.yml](dot/self_tests/data/base_self_test/dot_config.yml), (re)creates a schema for DOT configuration and loads it with test data, etc.

## Code quality
We have instituted a pair of tools to ensure the code base will remain at an acceptable quality as it is shared and developed in the community.
1.	The [formulaic python formatter “black”](https://pypi.org/project/black/). As described by its authors it is deterministic and fast but can be modified. We use the default settings, most notably formatting to a character limit of 88 per line.
2.	The [code linter pylint](https://pylint.org/). This follows the [PEP8](https://peps.python.org/pep-0008/) style standard. PEP8 formatting standards are taken care of in black, with the exception that the default pylint line length is 80. Pylint is also modifiable and a standard set of exclusion to the PEP8 standard we have chosen are found [here](https://github.com/datakind/medic_data_integrity/blob/main/.pylintrc). We chose the default score of 7 as the minimum score for pylint to be shared.
The combination of black and pylint can be incorporated into the git process using a pre-commit hook by running setup_hooks.sh


_For detailed information on advanced configuration options and guidelines for contributing to the project, please refer to the [CONTRIBUTING.md](./CONTRIBUTING.md) document._

#
#

----------


## Setting up the DOT User Interface

The above steps will start the DOT user interface, which will allow you to manage DOT and see results. You need to
do a few steps the first time you use it ...

1. Go to [http://localhost:82/](http://localhost:82)
2. Click the button and register to create a login (keep note of the password)
3. Once created, click 'Build my own' on the next popup
4. Click app smith icon top-left to go back tom homepage
5. Top-right next to the new button, click on the '...' and select *import*
6. Select *Import from file* and navigate to file `./docker/appsmith/DOT App V2.json`
7. You will be prompted to enter details for the database connection. You can set these as required, but if using the
   DOT dockerized Postgres database, the parameters are:
    - `Host address: dot-db`
    - `Port: 5432`
    - `Database name: dot_db`
    - `Authentication > User name: postgres`
    - `Authentication > Password: <THE PASSWORD YOU USED WHEN BUILDING DOT>`

You should now see the DOT user interface in developer mode (ie you could edit it). To run in end-user mode:

1. Click button top-right click the 'Deploy' button. This should open a new tab with the user interface in all its glory!

Note: If you want to remove Appsmith information on the deployed app, add `?embed=True` at the end
of the deployed app URL.

## Viewing test results

Your test results will be in the `dot-db` container. You can view the results by opening a shell in the dot-db container:

`docker exec -it dot-db /bin/bash`

Then running the psql client locally in that container:

`psql -U postgres -d dot_db`


Or if you prefer a database client (like [DBeaver](https://dbeaver.io)), you can use their settings:
```
host=localhost
port=5433 
database=dot_db
user=postgres
password=<the POSTGRES_PASSWORD you set above>
```

Note: The host and port are set in the [docker-compose.yml](./docker/docker-compose.yml)

To see some raw results you can run `SELECT * from dot.test_results LIMIT 100;`. Some more advanced queries are provided below.


# Configuring DOT

The following sections provide instructions for adding entities and tests to DOT directly in the DOT database. You can 
also use the DOT user interface for tests, for more details please see section see section [The DOT User Interface](#the-dot-user-interface). If you want to test DOT with health related data, please feel free to use this [fabricated dataset] (https://docs.google.com/spreadsheets/d/1l6inpa6ykgUewC-MJkgrQwwc8HjUiTLLJFEDBtAMDB4/edit#gid=31188808) which resembles appointment information and contains some quality issues which DOT can highlight. 
## How to add new entities
The DOT will run tests against user-defined views onto the underlying data. These views are called "entities" and defined in table `dot.configured_entities`:


| Column | Description                                                               |
| :----------- |:--------------------------------------------------------------------------|
| entity_id | Name of the entity e.g. ancview_danger_sign                               |
| entity_category | Category of the entity e.g. anc => needs to be in `dot.entity_categories` |
| entity_definition | String for the SQL query that defines the entity                          |

For example, this would be an insert command to create `ancview_danger_sign`:

```postgres-sql
INSERT INTO dot.configured_entities (project_id,entity_id,entity_category,entity_definition,date_added,date_modified,last_updated_by) VALUES('Project1', 
'ancview_danger_sign', 'anc', '{{ config(materialized=''view'') }}
{% set schema = <schema> %}

select *
from {{ schema }}.ancview_danger_sign');

```

All entities use Jinja macro statements - the parts between `{ ... }` - which the DOT uses to create the entity 
materialized views in the correct database location. Use the above format for any new entities you create.

The SQL for the view definition can be more complex than the example above, combining data from multiple underlying 
tables or views. For example: 

```postgres-sql
{{ config(materialized=''view'') }}
{% set schema = <schema> %}

select ap.*,
        ap.lmp as lmp_date,
        DATE_PART(''day'', reported - lmp) as days_since_lmp
from {{ schema }}.ancview_pregnancy ap

```

When you add a new entity to the configuration, take a look to the existing `dot.entity_categories` to associate your new entity
to one of them. If you need to add a new category, the table `dot.entity_categories` has the following columns:
| Column | Description |
| :----------- | :----------- |
| entity_category | Category of the entity e.g. anc |
| description | A description of the category |

An example of an insert statement would be:
`INSERT INTO dot.entity_categories VALUES('anc', 'antenatal care');`

## How to configure tests  
Tests are defined in the table `dot.configured_tests`. Each test has an associated `test_type`, a list of which can be 
found in table `dot.test_types` (see section "DOT Database Schema" below for more details on the full schema).

To use one of these test types for a new test, insert a new row in `dot.configured_tests`.

Here are the columns included in a test:
| Column | Description |
| :----------- | :----------- |
test_activated | Whether the test is activated or not
project_id | ID of the project, for example "`ScanProject1`"
test_id | UUID of the test
scenario_id | ID of the scenario
priority | Priority level
description | Description of the test
impact | Why the test is important
proposed_remediation | How the issue in this test might be solved
entity | The entity against which the test runs (check `entities` below)
test_type | Test type
column_name | The column in the table against which the test runs
column_description | Description of the above column
test_parameters | Any parameters the test takes in
date_added | Date when the test was added
date_modified | Date when the test was last modified
last_updated_by | Person who last updated the test

The UUID in the above example will get overwritten with an automatically generated value. Also, your test must be unique
for the project. If you get a key violation it's probably because that test already exists.


### Activating/Deactivating existing tests

Note that it's possible to deactivate tests, which can sometimes be useful for testing. To do this simply
set `test_activated=False` in table `dot.configured_tests`. For example:


` update dot.configured_tests set test_activated=false where test_id not in ('7db8742b-c20b-3060-93e2-614e35da2d4b','0f26d515-a70f-3758-8266-8da326d90eb6'); `


# Advanced topics

### Running the DOT in Airflow (Demo)

A DAG has been included which copies data from the uploaded DB dump into the DOT DB 'data_ScanProject1' schema, and then runs 
the toolkit against this data. To do this ...

1. Go to [http://localhost:8083](http://localhost:8083/home)
2. Log in with airflow/airflow
3. Click on 'DAGs' in top menu
4. Search for 'dot' in top-right search box (be sure to hit return twice)
5. Toggle DAG 'run_dot_project' to Active (far left toggle on row)
6. Click play icon under 'Actions', this will start the run

To see progress, and/or logs ...

7. Click on one of the circles under 'Runs', eg 'running', or 'completed'
8. Click on top 'Dag Id'
9. Click on task and then 'Log', you should now see logs

To use Airflow CLI for debugging a task (assuming you are getting object ancview_danger_sign):
 
 1. `docker exec -it docker-airflow-worker-1 /bin/bash`
 2. `airflow tasks test run_dot_project sync_object_flight_data  2022-03-01`

Or to run just DOT stage ...

`airflow tasks test run_dot_project run_dot  2022-03-01`

## How the DOT works

The Data Observation Toolkit (DOT) uses the open source projects [DBT](https://docs.getdbt.com/docs/introduction/) and [Great Expectations](https://greatexpectations.io/)
as a framework for the definition, development and execution of the data tests.

Most tests are developed on DBT, leveraging its support for base tests for column not nulls, foreign key checks, and
a few more, all of which can be expressed as entries on a YAML file. Additionally, making use of its custom tests,
many complex tests involving a set of columns of one or two tables can be expressed using DBT, written with SQL/Jinja
statements.

Great Expectations adds the possibility of implementing tests in python, and are used for checks that cannot be
expressed in SQL, for example tests that inspect the statistical distribution of the data.


#### Extra notes

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
need to do is ..

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
```
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
```
pytest dot/self_tests/unit
```