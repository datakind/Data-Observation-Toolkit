# Configuring the DOT Database
After configuring the environment as described in the previous sections, you can proceed to set up the DOT database for your environment. This setup will enable you to continue working with the data or view the results of the available data. The database schema is defined as follows:

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
