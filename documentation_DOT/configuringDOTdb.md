# Configuring the DOT Database
After configuring either [Docker Environment to Run DOT](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/e95231bdaf4c8410633b298ac246173b061dbe52/documentation_DOT/setuandrunDOTonDocker.md) or 	[Deploying DOT to Airflow](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/72a3bb7a36fbfc69b621180fd52034dc99d1ee86/documentation_DOT/airflowdeployment.md), you can proceed to set up the DOT database for your environment. This setup will enable you to continue working with the data or view the results of the available data. The database schema is defined as follows:

<figure style="text-align:center;">
  <figcaption>DOT Database Schema</figcaption>
  <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/9a7d950ae63b8ecf064d7070c8b184abf298c417/images/db_schema.png" alt="dot_db_schema" /> </figure>

## Tables in the DOT Database
The DOT database schema includes the following tables:
| Table                     | Description                                                                                                                               |
| :------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------- |
| projects                  | Defines the projects for which DOT can be executed. Typically, a project is associated with a single source database containing the data. |
| configured_entities       | Stores entities, which are views of underlying data that DOT will test.                                                                   |
| entity_categories         | Categorizes each entity, such as "Pre-natal care." Useful for segmenting DOT results by category                                          |
| configured_tests          | Specifies the tests to be executed for each project.                                                                                      |
| scenarios                 | Represents the DOT Taxonomy scenario for each test.                                                                                       |
| test_types                | Defines the available test types for each test, e.g., null, unique, custom SQL.                                                           |
| scenario_test_types       | Lists the applicable test types for each scenario.                                                                                        |
| test_parameters_interface | JSON object defining interface parameters required for each test type. (Note: Not currently used, but will be in future versions.)        |
| run_log                   | Logs DOT runs, including start/stop times and failure messages.                                                                           |
| test_results              | Main test results table, indicating any test failures.                                                                                    |
| test_results_summary      | Aggregates the test results for each run.                                                                                                 |
| remediation_log           | Tracks remediation actions. (Note: Not yet implemented.)                                                                                  |

The **test_results** table contains fields that link back to the data tested. This data can come from a fixed table or view, or even a custom SQL query. Additionally, a useful Postgres function exists that retrieves a JSON record of the data tested, as discussed in the section **'Seeing the raw data for failed tests'** above.

Your test results will be in the dot-db container. You can view the results by opening a shell in the dot-db container:
   ```bash
   docker exec -it dot-db /bin/bash
   ```

Then running the psql client locally in that container:
   ```bash
   psql -U postgres -d dot_db
   ```


##  To set up DB connection to the DOT Database
You can use a database client (like [DBeaver](https://dbeaver.io)), and use the following configuration to start the database:
  - **host=** localhost
  - **port=** 5433
  - **database=** dot_db
  - **user=** postgres
  - **password=** `<THE PASSWORD YOU USED WHEN BUILDING DOT>`

**Note:** The host and port are set in the [docker-compose.yml](./docker/docker-compose.yml)
To see some raw results you can run ```SELECT * from dot.test_results LIMIT 100; ```. Some more advanced queries are provided in the **Advance Topics sections** for you to experiment further functionality.


##  To set up the connection to the DOT Database on Airflow
1.	Connect to the DOT DB as mentioned above in section
2.	Go to: [http://localhost:8083/](http://localhost:8083/)  and log in with airflow/airflow
3.	Next, create a copy of the DOT DB to be used as the source database. Open a SQL query editor session and run the following queries ...
   ```bash
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = 'dot_db' AND pid <> pg_backend_pid();
   ```
   ```bash
   CREATE DATABASE dot_data WITH TEMPLATE dot_db OWNER postgres;
   ```
In top menu select **Admin > Connections, click on the (+)** Enter the Docker DOT DB details as follows:
  -  **Conn Id:** dot_db
  -  **Conn Type:** Postgres
  -  **Host:** dot_db
  -	 **Schema:** dot
  -  **Login:** postgres
  -  **Password:** [THE PASSWORD YOU USED WHEN BUILDING DOT]
  -  **Port:** 5432

Set up new connection in Airflow as follows:
- **Conn Id:** dot_data
- **Conn Type:** Postgres
- **Host:** dot_db
- **Schema:** public
- **Login:** postgres
- **Password:** [THE PASSWORD YOU USED WHEN BUILDING DOT]
- **Port:** 5432

---

# Useful DOT Database Queries
The following queries can be helpful for visualizing the DOT DB schema and extracting key insights from the data. These queries can assist in monitoring and analyzing the performance of your DOT setup, especially with respect to failed tests.
### Statistics on failed tests
```sql
SELECT  tr.run_id, ct.test_type, COUNT(*)
FROM  dot.test_results tr,  dot.configured_tests ct
WHERE tr.test_id = ct.test_id
GROUP BY  tr.run_id, ct.test_type
ORDER BY ct.test_type
   ```
Same query, but with test description and entity names added in the grouping:
```sql
SELECT  tr.run_id, tr.view_name, ct.test_type, ct.description, ce.entity_name, COUNT(*)
FROM dot.test_results tr, dot.configured_tests ct, dot.configured_entities ce
WHERE tr.test_id = ct.test_id AND ce.entity_id = ct.entity_id
GROUP BY tr.run_id, tr.view_name, ct.test_type, ct.description, ce.entity_name
ORDER BY tr.run_id, tr.view_name, ct.test_type, ct.description, ce.entity_name
```
### Linking DOT Data scenarios with configured tests
```sql
SELECT  s.*, ct.*
FROM dot.scenarios s, dot.configured_tests ct
WHERE s.scenario_id=ct.scenario_id
```
### Linking configured tests to test results
```sql
SELECT  s.*, ct.*, ce.entity_name, tr.*
FROM dot.scenarios s, dot.configured_tests ct, dot.test_results_summary tr, dot.configured_entities ce
WHERE s.scenario_id=ct.scenario_id AND tr.test_id=ct.test_id AND ce.entity_id = ct.entity_id
LIMIT 10
```

# Viewing test results

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

#### Deactivating all tests except one dbt and one great expectation
```sql
UPDATE dot.configured_tests
SET test_activated=false
WHERE test_id NOT IN ('7db8742b-c20b-3060-93e2-614e35da2d4b','0f26d515-a70f-3758-8266-8da326d90eb6')
```
The raw data for failed tests can be accessed through the ```dot.test_results``` table. The view_name column specifies the name of the database view that contains the data for the failed tests. Additionally, the ```id_column_name``` and ```id_column_value``` columns indicate the respective columns in the database entity view that correspond to the tested data. Finally, you can retrieve the underlying data for each test by querying the ```get_dot_data_record``` function.

```sql
SELECT  tr.test_id, tr.status, dot.get_test_result_data_record(ce.entity_name, tr.id_column_name, tr.id_column_value,'public_tests')
FROM dot.scenarios s, dot.configured_tests ct, dot.configured_entities ce, dot.test_results tr
WHERE  s.scenario_id=ct.scenario_id AND tr.test_id=ct.test_id AND ce.entity_id=ct.entity_id
LIMIT 10
```
Where the function parameters are:

- Test entity name
- Test result ID column name (in entity view)
- Test Result ID column value
- Test results schema name

This returns a json record for the data that was tested.
**Note:** If using the airflow environment, change ```public_tests``` to the schema where the data is, for example ```data_flights_db```.