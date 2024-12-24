# Setting Up Superset in Docker
As of the time of writing, the setup for Apache Superset is not fully automated. However, once your Docker containers are up and running for the first time, follow these steps to complete the setup.

## Initial Superset Setup
1.	**Create an Admin User**
First, create an admin user for Superset using the following Docker command:
 ```bash
docker exec -it superset superset fab create-admin --username admin --firstname Superset --lastname Admin --email admin@superset.com --password admin
  ```
2.	**Upgrade the Database**
Run the database migration to ensure the database schema is up to date:
```bash
 docker exec -it superset superset db upgrade
  ```
3.	**Initialize Superset**
Finally, initialize Superset by running:
```bash
docker exec -it superset superset init
 ```
You can safely ignore any warnings about ```CACHE_TYPE``` being null.
## Accessing Superset
Once the setup is complete, you can access the Superset UI by opening the following URL in a web browser:
[http://localhost:8080/login/](http://localhost:8080/login/)

**Note:** Some users have found that Google Chrome works better with Superset compared to Safari.
- **Login Credentials:** Use the following credentials to log in: 
- **Username:** admin
- **Password:** admin

## Connecting to the DOT Database

After logging into Superset, follow these steps to connect Superset to the DOT database:
1.	**Navigate to the Databases Menu**
In the top menu, click on **Data > Databases.**
2.	**Add a New Database**
On the right-hand side of the screen, click the **+ Database** button.
3.	**Choose PostgreSQL**
Select **PostgreSQL** as the database type.
4.	**Enter Database Connection Parameters**
Fill in the following connection details for the DOT database:
- 	**Host:** dot_db
- 	**Database:** dot_db
-  **Display Name:** dot_db
- 	**Port:** 5432
- 	**User:** postgres
- 	**Password:** [THE PASSWORD YOU USED WHEN BUILDING DOT]

## Creating Datasets in Superset

Once the database connection is established, you can begin creating datasets for the DOT tables:
1.	**Navigate to the Datasets Menu**
  In the top menu, click **Data > Datasets.**
2.	**Add a New Dataset**
  Click the **+ DATASET** button.

**Select Tables from the DOT Database**
Choose the table(s) you want to work with, such as ```test_results ```, from the DOT database.

## Creating Charts
Now that you have datasets available, you can proceed to create charts using Superset. For detailed instructions, refer to the official [Superset chart creation guide](https://superset.apache.org/docs/creating-charts-dashboards/first-dashboard#adding-a-new-table).

## Important Notes
**Export Dashboards:** If you're using Superset in a Docker environment, it's essential to export your dashboards periodically. This ensures you don't lose your work if you need to rebuild the Docker environment.

---


# Running the DOT in Airflow (Connecting to External Databases)

This section outlines the process for using a local Airflow environment to connect to external databases for both data and the Data Observation Toolkit (DOT). Please note that the instructions provided here are for illustrative purposes only. In a production setting, it's crucial to ensure that Airflow is securely configured, with network security measures in place (e.g., firewalls, strong passwords, etc.) and proper isolation from the internet.

### Steps to Configure Airflow with External Databases:
1.	**Edit the DOT Configuration**
 
    Begin by modifying the ```./dot/dot_config.yml``` file. Set the appropriate connection parameters for your external dot_db. This configuration ensures that the DOT is able to communicate with your specific database instance.

2.	**Add Data Database Connections**

    Create a section in the ```dot_config.yml``` file to define the connection parameters for your external data databases. Ensure that all connection details—such as host, port, username, password, and database name—are correctly specified.

4.	**Deploy DAG JSON File**

    If you have an existing DAG JSON file (e.g., dot_projects.json), deploy it by placing it into the ```./airflow/dags``` directory. This allows Airflow to recognize and manage your DOT-related tasks.

5.	**Configure Airflow Docker Environment**

    Be sure to have  completed [Deploying DOT to Airflow]( https://github.com/wvelebanks/Data-Observation-Toolkit/blob/72a3bb7a36fbfc69b621180fd52034dc99d1ee86/documentation_DOT/airflowdeployment.md) section these steps ensure that Airflow is correctly configured and ready to execute DAGs.

7.	**Update Airflow with External Database Configurations**

    For the next steps ensure you use the connection values for your external databases, as defined in the ```dot_config.yml``` file. These configurations are essential for ensuring that the DOT can properly interact with the external data sources.

8.	**Configure DOT Tests and the DAG JSON File**

    You will need to adjust the configuration of DOT tests and the DAG JSON file to align with your specific installation and data setup. This ensures that the tests are properly executed within the context of your Airflow environment.

### Adding More Projects to Airflow

  If you are configuring Airflow in a production environment, be sure to modify the ```./docker/dot/dot_config.yml``` file to accommodate additional projects. Furthermore, you can extend the list of projects by adding entries to the projects array in the Airflow configuration JSON. This allows you to easily scale and manage multiple data projects within your Airflow environment.

---