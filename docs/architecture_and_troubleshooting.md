# Architecture & Troubleshooting

This document provides a deep dive into the internal architecture of DOT (dbt and Great Expectations) and offers troubleshooting advice for common issues, including useful database queries.

## Table of Contents
- [Internal Architecture Overview](#internal-architecture-overview)
  - [Database Connection Registry (`dot_config.yml`)](#database-connection-registry-dot_configyml)
  - [dbt Integration](#dbt-integration)
  - [Great Expectations Integration](#great-expectations-integration)
  - [Database Schema](#database-schema)
- [Developing DOT](#developing-dot)
  - [Self-Tests](#self-tests)
  - [Code Quality](#code-quality)
- [Troubleshooting Port Conflicts](#troubleshooting-port-conflicts)
- [Useful Database Queries](#useful-database-queries)

---

## Internal Architecture Overview

DOT uses [dbt](https://docs.getdbt.com/) and [Great Expectations](https://greatexpectations.io/) to execute tests. Most tests leverage dbt (for SQL-based tests like `not_null` or custom SQL), while Great Expectations is reserved for statistical checks via Python/Pandas.

### Database Connection Registry (`dot_config.yml`)

The `dot_config.yml` file is the connection registry that allows DOT to authenticate and run tests against the correct databases. When deployed via Docker, this file is mounted to the container at `/app/dot/config/dot_config.yml`.

It defines these blocks:
- **`dot`**: Global configuration. `output_schema_suffix: tests` is the suffix DOT appends for test-output schemas (e.g., `public_tests`).
- **`dot_db`**: The internal DOT database where the application state, configuration metadata, and test results are stored.
- **`[ProjectName]_db`**: A connection block for that project's data. In the Airflow demo, `ScanProject1_db` and `EduProject_db` share one Postgres server but differ by schema (`data_dot_data_public` and `data_dot_data_education`).

**Example Structure:**
```yaml
dot:
  output_schema_suffix: tests
dot_db:
  type: postgres
  host: dot_db
  user: postgres
  pass: "{{ env_var('POSTGRES_PASSWORD') }}"
  port: 5432
  dbname: dot_db
  schema: dot
  threads: 4
ScanProject1_db:
  type: postgres
  ...
  schema: data_dot_data_public
EduProject_db:
  ...
```

Notice the use of `{{ env_var('POSTGRES_PASSWORD') }}`. This Jinja templating securely reads the password from your environment variables at runtime rather than storing it in plain text.

**The Lookup Process:**
Before a run starts, two things must be true: the YAML key must be the project id plus `_db` (project `ScanProject1` requires a block named `ScanProject1_db`), and that block's `schema` must be the schema Airflow loaded for that project. When you trigger a run for `ScanProject1`, the DOT engine reads `ScanProject1_db` and builds the dbt and Great Expectations connections from it.

*Note on Schema Naming: Airflow names the destination schema `data_<source_connid>_<source_schema>`, using the Airflow source connection id from `dot_projects.json`. In the demo, the connection id is `dot_data`, so `public` becomes `data_dot_data_public` and `education` becomes `data_dot_data_education`. If the connection id were `postgres` and the source schema were `public`, the schema would be `data_postgres_public`. If you are running a non-Airflow deployment, or connecting to an existing external database, you must set `schema` to the real target schema instead of an Airflow-generated name.*

(For more on isolation, see the [Technical Documentation](../TECHNICAL_DOCUMENTATION.md)).

### dbt Integration

Most dbt files are **dynamically written** by DOT based on the `dot.configured_entities` and `dot.configured_tests` tables.

- **`macros/`**: Jinja macros to support organized code and custom schema tests.
- **`models/`**: Contains dynamically generated SQL for models and `.yml` files for schema tests.
- **`tests/`**: Custom SQL tests dynamically generated for `custom_sql` test types.
- **`target/` (Auto-generated)**: Compiled SQL used to create models and tests.
- **`dot/utils/dbt.py`**: The core Python utility that manages dbt job execution, extracts failing rows into views, and updates test results to the DB.

### Great Expectations Integration

- **`expectations/`**: JSON files indicating the tests to be run (Dynamically generated).
- **`plugins/custom_expectations.py`**: Where arbitrary Python checks are implemented under the `CustomSqlAlchemyDataset` class.
- **`batch_config.json`**: Defines datasources and test suites. A default empty dataset is added here for custom expectations as a placeholder.

### Database Schema

| Table | Description |
| :--- | :--- |
| `projects` | Defines active projects associated with source databases. |
| `configured_entities` | Holds views onto underlying data that DOT will test. |
| `configured_tests` | Defines what tests to run for each project. |
| `test_types` | Available test types (e.g., `not_null`, `unique`, `custom_sql`). |
| `test_results` | Main test results table tracking individual row failures. |

---

## Developing DOT

DOT is open source. We encourage all development to be done as part of that initiative. This includes following the code quality standards and self-test guidelines described below.

### Self-Tests

The DOT runs self-tests to verify that its core functions are working correctly. If you are contributing to the project by adding a new feature or fixing a bug, please follow these guidelines:

- Find the existing tests applicable to the area you are modifying.
- Add a few more relevant tests for your bugfix or improvement.
- Implement your changes until all tests pass.

#### Running Self-Tests

<details>
<summary><strong>Using Docker</strong></summary>

The Docker build used to run DOT also includes the self-test suite. Once you have the container running, all you need to do is:

```bash
docker exec -it dot /bin/bash
pytest dot/self_tests/unit
```

</details>

<details>
<summary><strong>On your local machine</strong></summary>

To run the tests locally, complete the following preparation steps first:

- Create a local Python environment via `venv` or `conda`.
- Make sure your Python version matches the one specified in `.github/workflows/lint.yml`.
- Create a conda environment using the `environment.yml` file at the root directory.
- Prepare a PostgreSQL database that the tests can use (e.g., a local Postgres instance or a Docker container used as a database only).
- Create a `dot_config.yml` file at `dot/self_tests/data/base_self_test/` with the same structure as [dot/config/example/dot_config.yml](../dot/config/example/dot_config.yml). It should look like the following (note this config points to the DB in the Docker container):

```yaml
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
ScanProject1_db:
  type: postgres
  host: localhost
  user: postgres
  pass: "{{ env_var('POSTGRES_PASSWORD') }}"
  port: 5433
  dbname: dot_db
  schema: self_tests_public
  threads: 4
```

Then run the tests from your terminal:

```bash
pytest dot/self_tests/unit
```

</details>

#### Guidelines for Adding New Tests

- Existing tests are located in [dot/self_tests/unit](../dot/self_tests/unit).
- All tests extend the [test base class](../dot/self_tests/unit/base_self_test_class.py), which:
  - Facilitates the import of modules under test.
  - Recreates a directory in the file system for test outputs.
  - Provides a set of helper functions for tests that access the database — mocking the config files to point to the test `dot_config.yml`, (re)creating a schema for DOT configuration, and loading it with test data.

---

### Code Quality

Two tools are used to ensure the codebase remains at an acceptable quality as it is shared and developed in the community:

1. **[black](https://pypi.org/project/black/)** — a deterministic Python formatter. We use the default settings, most notably formatting to a character limit of 88 per line.
2. **[pylint](https://pylint.org/)** — a code linter following the [PEP8](https://peps.python.org/pep-0008/) style standard. PEP8 formatting is handled by black, with the exception that the default pylint line length is 80. We use a standard set of exclusions (found [here](https://github.com/datakind/medic_data_integrity/blob/main/.pylintrc)) and require a minimum pylint score of **7** before code can be shared.

Both tools can be incorporated into your git workflow as a pre-commit hook by running:

```bash
./setup_hooks.sh
```

> **Note:** See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full contributor guide, including the GitHub workflow (gitflow branching model, PR process) and Continuous Integration setup.

---

## Troubleshooting Port Conflicts

DOT relies on several ports. If Docker Compose fails to bind a port, ensure they are free:

- **Port 82**: Appsmith (DOT UI)
- **Port 5432/5433**: PostgreSQL (Internal DOT DB)
- **Port 8083**: Apache Airflow UI
- **Port 8080**: Apache Superset

**Resolution**: If a port is in use (e.g., local Postgres on 5432), modify the left-side (host) port in `docker-compose.yml` (e.g., `5433:5432`).

---

## Useful Database Queries

Connect to `dot_db` using `psql` or DBeaver to run these queries for advanced insights.

### 1. Statistics on Failed Tests

Get a simple count of failures grouped by test type:

```sql
SELECT
   tr.run_id,
   ct.test_type,
   COUNT(*)
FROM
   dot.test_results tr
JOIN 
   dot.configured_tests ct ON tr.test_id = ct.test_id
GROUP BY
   tr.run_id,
   ct.test_type
ORDER BY
   ct.test_type;
```

### 2. Viewing Raw Data for Failed Tests

The `dot.test_results` column `view_name` provides the DB view holding the failed data. You can query the underlying data for each failed test using this built-in function:

```sql
SELECT 
   tr.test_id,
   tr.status,
   dot.get_test_result_data_record(
       ce.entity_name, 
       tr.id_column_name, 
       tr.id_column_value,
       'public_tests'
   )
FROM
   dot.scenarios s
JOIN dot.configured_tests ct ON s.scenario_id = ct.scenario_id
JOIN dot.configured_entities ce ON ce.entity_id = ct.entity_id
JOIN dot.test_results tr ON tr.test_id = ct.test_id
LIMIT 10;
```
*(Change `'public_tests'` to your actual source schema if using Airflow).*
