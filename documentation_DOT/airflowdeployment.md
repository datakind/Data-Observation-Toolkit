# Deploying DOT to Airflow
This setup serves as a proof-of-concept to demonstrate how Airflow can be configured to run DOT across multiple databases. It is designed to copy data from the **data** database back into the **DOT** database. In a production environment, the flow would instead transfer data from the source production database into the data_ schema of the DOT database. This configuration assumes you have already completed the Docker environment setup, as outlined in the previous section.

## Configuring/Building Airflow Docker environment

#### 🌟 Optional but Highly Recommended 🌟

If you wish to include the user interface (UI) while building the containers for DOT, you will need to add the following code snippet. This snippet can be found in the `docker-compose.yml` file, specifically on lines 31-38. Copy the code and insert it into the `docker-compose-with-airflow.yml` file, ensuring that the code is placed below line 92. Make sure to maintain the proper indentation.

```yaml
appsmith:
  image: index.docker.io/appsmith/appsmith-ce
  container_name: appsmith
  ports:
    - "82:80"
    - "446:443"
  volumes:
    - ./appsmith/stacks:/appsmith-stacks
```
Additionally, in the docker-compose-with-airflow.yml file, remove line 61 as it is redundant. Set the configuration AIRFLOW__CORE__LOAD_EXAMPLES to False as shown below:
```yaml
AIRFLOW__CORE__LOAD_EXAMPLES: 'False'
```
🌟🌟

## Step-by-Step Instructions to Set Up Airflow and Run DOT with Docker
1. Navigate to the Docker directory:
   ```bash
   cd ./docker
   ```
2. Set the PostgreSQL password environment variable:
  ```bash
  export POSTGRES_PASSWORD=<THE PASSWORD YOU USED WHEN BUILDING DOT>
  ```
  Replace <THE PASSWORD YOU USED WHEN BUILDING DOT> with the actual password.

3.  Build the Docker containers using ```docker-compose-with-airflow.yml```:
   ```bash
    docker compose -f docker-compose-with-airflow.yml build
   ```
  _**Note** in case you get an error related to ssh-agent, be sure to use the following:_
      ```eval $(ssh-agent)  ==> for windows users   Or   eval ssh-agent  ==> for Mac/Linux users
      ```
4.  Initialize the Airflow containers:
   ```bash
    docker compose -f docker-compose-with-airflow.yml up airflow-init
   ```
5.  Start the containers in detached mode:
   ```bash
   docker compose -f docker-compose-with-airflow.yml up -d
   ```
6.  Access the Airflow worker container:
   ```bash
   docker exec -it docker-airflow-worker-1 /bin/bash
   ```
7.  Navigate to the dot directory and run the installation script:
   ```bash
    cd /app/dot && ./install_dot.sh
   ```

These steps will build and initialize your Docker containers, set up Airflow, and install DOT in the appropriate environment.

**Notes:**
- Make sure to replace `<THE PASSWORD YOU USED WHEN BUILDING DOT>` with the actual password used during setup.
- If you face any issues with the container names (like `docker-airflow-worker-1`), check the container name using the `docker ps` command to confirm the exact name.
-  _**If using Docker on AWS, you might need to use docker-compose instead of docker compose.**_


## Airflow Docker Environment Management
You might need to use `docker-compose` on some hosts.

**Starting Airflow Docker Environment**
To start the Airflow Docker environment in detached mode, run:

```bash
docker compose -f docker-compose-with-airflow.yml up -d
```
**Stopping Airflow Docker Environment**

To stop the Airflow Docker containers, run:
```bash
docker compose -f docker-compose-with-airflow.yml stop
```

**Removing Airflow Docker Environment**

To remove the Airflow Docker environment and its associated volumes, run:
```bash
docker compose -f docker-compose-with-airflow.yml down -v
```
This will remove the containers and any volumes defined in the docker-compose-with-airflow.yml file, ensuring a clean environment.

## Running DOT in Airflow (Demo)

A Directed Acyclic Graph (DAG) is included that copies data from the uploaded DB dump into the DOT database (```data_ScanProject1``` schema) and then runs the toolkit against this data. Follow these steps to execute the DAG:

- Open your browser and navigate to [http://localhost:8083/](http://localhost:8083/).
- Log in with the credentials: 'airflow' / 'airflow'. as shown below:

   <figure style="text-align:center;">
      <figcaption></figcaption>
      <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/f3759185cdec418275d1f7c84114234e1aa5d27b/images/airflow_lgin.png" alt="dot_acrh" />
   </figure>

- In the top menu, click on DAGs on the top menu, you should see a detail view panel for the Dags as shown below:
   <figure style="text-align:center;">
      <figcaption></figcaption>
      <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/f3759185cdec418275d1f7c84114234e1aa5d27b/images/airflow_interface.png" alt="dot_acrh" />
   </figure>

- Use the search box in the top-right corner to search for dot (press Enter twice to ensure it registers).
- Toggle the ```run_dot_project``` DAG to Active (using the toggle on the far left of the row).

   <figure style="text-align:center;">
      <figcaption></figcaption>
      <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/f3759185cdec418275d1f7c84114234e1aa5d27b/images/DAG_list.png" alt="dot_acrh" />
   </figure>

- Click the Play icon under Actions to start the run.

To monitor the progress and view logs:

- Click on one of the status circles under Runs (e.g., running or completed).
- Click on the top Dag Id.
- Select a task and then click Log to view the logs.

To debug a task using the Airflow CLI (e.g., if you encounter the object ```ancview_danger_sign error```):
Open a terminal and execute the following command to access the Airflow worker container:
```bash
docker exec -it docker-airflow-worker-1 /bin/bash
```
Run the following Airflow command to test the task:
```bash
airflow tasks test run_dot_project sync_object_flight_data 2022-03-01
```
To run just the DOT stage:
```bash
airflow tasks test run_dot_project run_dot 2022-03-01
```


If you need to [set up the database for DOT](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/b70d3e044858387443698354b0c4253a6b618b17/documentation_DOT/configuringDOTdb.md) or [configure Appsmith](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/d9845f8228bb147af7f28f7a300a68012e9b51ed/documentation_DOT/developingappsmith.md), check out the guide for setting up the DOT Database and the guide for configuring Appsmith. These resources will provide step-by-step instructions for both tasks.