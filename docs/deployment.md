# DOT Deployment Guide

This guide covers all deployment and setup instructions for the Data Observation Toolkit (DOT). Whether you are running DOT locally via Docker, or deploying it to a production environment using Apache Airflow and AWS EC2, you will find the steps here.

## Table of Contents
- [The Not-So-Quick Start: Manual Docker Build](#the-not-so-quick-start-manual-docker-build)
- [Setting up the DOT User Interface (Appsmith)](#setting-up-the-dot-user-interface-appsmith)
- [Deploying with Apache Airflow](#deploying-with-apache-airflow)
  - [Incremental Data Synchronization](#incremental-data-synchronization)
- [Connecting Airflow to an External Database](#connecting-airflow-to-an-external-database)
- [Migrating to AWS EC2](#migrating-to-aws-ec2)

---

## The Not-So-Quick Start: Manual Docker Build

If you wish to build DOT yourself rather than using the automated quick start script:

1. Save a postgres password to your local environment:
   ```bash
   export POSTGRES_PASSWORD=<some password you decide>
   ```
2. Open a terminal and change directory into the `docker` sub-directory of DOT: 
   ```bash
   cd ./docker
   ```
3. Build the docker containers: 
   ```bash
   docker compose build
   ```
4. Start them: 
   ```bash
   docker compose up -d
   ```

Your environment is now running! (For execution instructions, refer to [execution.md](./execution.md)).

> **Note:** When running tests manually via `python run_everything.py --project_id`, DOT reads database connections from `./docker/dot/dot_config.yml`. The block key in that file must be `{project_id}_db`, and for a manual deployment, the `schema` value must be your real target schema, not an Airflow-generated name. See the [Database Connection Registry](./architecture_and_troubleshooting.md#database-connection-registry-dot_configyml).

---

## Setting up the DOT User Interface (Appsmith)

> ⚠️ **Important:** While the `run_demo.py` script launches a UI, the Appsmith Docker image used behind the scenes in that demo script is pulled from a public repository and is currently unreliable. For a fully working and stable UI, you **must** build the containers manually using `docker-compose.yml` (as shown in the section above) and then manually configure the UI using the steps below.

To set up the DOT User Interface:

1. Go to [http://localhost:82/](http://localhost:82)
2. Register to create a login.
3. Once created, click **'Build my own'** on the next popup.
4. Click the Appsmith icon top-left to go back to the homepage.
5. Top-right next to the new button, click on the **'...'** and select **Import**.
6. Select **Import from file** and navigate to `./docker/appsmith/DOT App V2.json` in your cloned repository.
7. Enter details for the database connection:
   - `Host address`: `dot-db`
   - `Port`: `5432`
   - `Database name`: `dot_db`
   - `Authentication > User name`: `postgres`
   - `Authentication > Password`: `<THE PASSWORD YOU USED WHEN BUILDING DOT>`
8. Click the **'Deploy'** button top-right to run in end-user mode.

*Note: If you want to remove Appsmith information on the deployed app, add `?embed=True` at the end of the deployed app URL.*

### Developing the Appsmith UI

Clicking **Edit** on the imported app gives you the ability to modify it. See the [Appsmith documentation](https://docs.appsmith.com) for full details.

Key things to note:
- All validation, defaulting, and tooltips are controlled via the database as much as possible (see the **Queries** section within Appsmith).
- The `test_parameters` JSON field generates a form dynamically. This was configured once — be aware that clicking **Regenerate** will remove many custom settings. New fields should be added manually. You may be able to reinstate logic in bulk by editing the raw Appsmith app JSON file.

### Updating to the Latest Version of Appsmith

> ⚠️ **Warning:** These steps will remove your saved configuration and app. Make a backup of the Appsmith JSON export before proceeding.

Appsmith regularly releases bug fixes and enhancements. To update manually:

1. From `./docker`, stop the Appsmith container:
   ```bash
   docker compose -f docker-compose-with-appsmith-ui.yml stop
   ```
2. Remove the old container:
   ```bash
   docker rm appsmith
   ```
3. In a clean directory, pull the latest Appsmith compose file:
   ```bash
   curl -L https://bit.ly/32jBNin -o $PWD/docker-compose.yml
   ```
4. Pull and restart:
   ```bash
   docker-compose pull && docker-compose rm -fsv appsmith && docker-compose up -d
   ```
5. Back in `./docker`, restart the DOT environment:
   ```bash
   docker compose -f docker-compose-with-appsmith-ui.yml up -d
   ```

---

## Deploying with Apache Airflow

For production environments, DOT uses Apache Airflow to orchestrate data extraction and synchronization. The Airflow worker image is pre-baked with all DOT dependencies.

### 1. Building and Starting the Airflow Environment

> 🎥 **Video:** [Initial setup and running the containers](../videos/01_docker_setup_and_containers.mp4)

1. Navigate to the `docker` directory:
   ```bash
   cd ./docker
   ```
2. Start the ssh-agent (if using ssh keys for source DB access):
   ```bash
   eval `ssh-agent`
   ```
3. Set your PostgreSQL password:
   ```bash
   export POSTGRES_PASSWORD=<Your DOT DB Password>
   ```
5. Initialize Airflow:
   ```bash
   docker compose -f docker-compose-with-airflow.yml up airflow-init
   ```
6. Start the Airflow environment:
   ```bash
   docker compose -f docker-compose-with-airflow.yml up -d
   ```

### 2. Setup Database Schemas

> 🎥 **Video:** [Creating dot_data (demo), connecting to the DB, viewing the database](../videos/02_database_setup_dbeaver.mp4)

Before configuring Airflow, you must define a target database where source data will be extracted into schemas. 

> **Note:** In our demo (and the video above), we use `dot_data` as a placeholder target database, which we create by simply copying `dot_db`. When setting this up for your own environments, replace `dot_data` with your actual target database.

To follow along with the demo and create the placeholder database, open a SQL session (using `psql` or DBeaver) against your Postgres instance and run:

```sql
SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity 
WHERE pg_stat_activity.datname = 'dot_db' AND pid <> pg_backend_pid();

CREATE DATABASE dot_data WITH TEMPLATE dot_db OWNER postgres;
```

### 3. Configure Airflow Connections

> 🎥 **Video:** [Setting up the connections and dot_projects.json](../videos/03_airflow_connections_and_projects.mp4)

Access the Airflow UI at [http://localhost:8083/](http://localhost:8083/) (login: `airflow` / `airflow`). Navigate to **Admin > Connections** and set up the following:

**Source Database Connection:**
- **Conn Id**: The name of your source connection (e.g., `postgres` or your actual target database name, shown as `dot_data` in the demo). This must exactly match the `source_connid` specified in your `dot_projects.json`.
- **Conn Type**: `Postgres`
- **Host**: `dot_db` (or your external database host).
- **Login**: `postgres` (or your DB username).
- **Password**: Your database password.
- **Port**: `5432` (or your DB port).
- *Note: Do **NOT** populate the Schema or Database fields here. They are dynamically injected at runtime based on the project configuration.*

**DOT Internal Database Connection:**
Ensure the `dot_db` connection is configured to point to the internal DOT PostgreSQL database (where test definitions and results live).

### 4. Define the Project Configuration (`dot_projects.json`)

The central registry for all Airflow extractions is `docker/airflow/dags/dot_projects.json`. For each project, you must define:

- `project_id`: The project identifier (e.g., `ScanProject1`).
- `source_connid`: Must match the Conn Id you just created in Airflow.
- `source_schema`: The specific schema to extract data from (defaults to `public`).
- `earliest_date_to_sync`: Fixed date cutoff. Required on every project. It is applied only to objects that set `date_field`.
- `objects`: The tables or views to copy. Each entry needs `object` and `id_field`. Add `date_field` on an entry to load that object incrementally.

#### Incremental Data Synchronization

Each object defines its own load mode independently. The `earliest_date_to_sync` field does not determine the mode — the presence or absence of `date_field` on each object does.

**Full replace (no `date_field`):**
Airflow copies the entire source object, drops the existing target table (`DROP TABLE ... CASCADE`), and loads the fresh copy in its place. In the demo, `airport_data` is loaded this way.

**Incremental append (`date_field` set):**
Airflow extracts only rows on or after the project cutoff:

```sql
SELECT * FROM <source_schema>.<object>
WHERE <date_field> >= '<earliest_date_to_sync>'
```

The cutoff is always the `earliest_date_to_sync` value defined in `dot_projects.json` — it is not dynamically updated to the latest timestamp already stored in the target. The comparison is inclusive (rows on that date are included).

Before appending, if the target table already exists, Airflow deletes any rows in the target whose `id_field` value appears in the incoming batch, then appends the new batch. This means a source row that was updated and still falls on or after the cutoff date will be replaced in the target. However, a row that was deleted from the source, or a correction made to a row older than the cutoff, will remain in the target unchanged. Use full replace when your source data deletes rows or corrects older records.

> **Note:** `date_field` and `id_field` are set per object in `dot_projects.json`. They are not read from `dot.configured_entities`.

**Example `dot_projects.json` entry:**
```json
{
  "project_id": "ScanProject1",
  "source_connid": "dot_data",
  "source_schema": "public",
  "earliest_date_to_sync": "2021-10-02",
  "objects": [
    {
      "object": "airport_data",
      "id_field": "uuid"
    },
    {
      "object": "flight_data",
      "id_field": "uuid",
      "date_field": "departure_time"
    }
  ]
}
```

In this example, `airport_data` is fully replaced on every run. `flight_data` is loaded incrementally: only rows with a `departure_time` on or after `2021-10-02` are extracted, and any existing target rows with matching `uuid` values are deleted before the new batch is appended.

### 5. Define the Database Connections (`dot_config.yml`)

While Airflow uses the connections above and `dot_projects.json` to know *where to extract data from*, the testing engine needs to know *how to connect* to the databases to run tests. This is configured in `./docker/dot/dot_config.yml`. It uses the `POSTGRES_PASSWORD` environment variable you set earlier. 

For each project, you must define:
- **`{project_id}_db` block**: Add a block whose key is the project id plus `_db`. A project id of `ScanProject1` requires `ScanProject1_db`. This must match the `project_id` in `docker/airflow/dags/dot_projects.json`.
- **`schema`**: Set that block's `schema` to the schema Airflow loaded, named `data_<source_connid>_<source_schema>`. With the demo connection id `dot_data`, `ScanProject1` uses `data_dot_data_public` and `EduProject` uses `data_dot_data_education`.

For full details on the registry, see the [Database Connection Registry](./architecture_and_troubleshooting.md#database-connection-registry-dot_configyml).

*(To learn how to execute this DAG, refer to [execution.md](./execution.md)).*

---

## Connecting Airflow to an External Database

The demo copies data from `dot_data`, a database created inside the DOT Postgres container. To sync from your own Postgres database, including a Postgres-compatible host such as Supabase, point the Airflow **source** connection at that database. The sync path uses Postgres.

> **Note:** Keep the Airflow UI off the public internet. Use a firewall, a strong password, or a VPN or SSH tunnel before connecting Airflow to a database outside your machine.

### Steps

1. **Create the Airflow source connection.** In the Airflow UI (**Admin > Connections**), add a new connection for your external database. Enter the external host, port, and credentials here. Leave the **Schema** and **Database** fields blank — the schema is read from `source_schema` in `dot_projects.json` at runtime by the `get_object` task.

2. **Point `dot_projects.json` at that connection.** Set `source_connid` to the Conn Id you created in step 1, and set `source_schema` to the schema you want to copy from (for example, `public`). Copy the file to `./docker/airflow/dags/` if it is not already there.

3. **Keep the `{project_id}_db` block pointed at the DOT database.** In `./docker/dot/dot_config.yml`, this block is used by dbt and Great Expectations after the data has been copied. Its `host` should remain the DOT Postgres instance, and its `schema` should be the destination schema Airflow created, formatted as `data_<source_connid>_<source_schema>`. Do not set the external host or source schema in this block. For details, see the [Database Connection Registry](./architecture_and_troubleshooting.md#database-connection-registry-dot_configyml).

4. **Start Airflow.** From `./docker`, initialize and start the stack:
   ```bash
   docker compose -f docker-compose-with-airflow.yml up airflow-init
   docker compose -f docker-compose-with-airflow.yml up -d
   ```

5. **Add another project.** To add a second project, add a new entry under `dot_projects` in `dot_projects.json` and a corresponding `{project_id}_db` block in `dot_config.yml`.

### What to set on the Airflow source connection

| Field | What to use |
| :--- | :--- |
| **Conn Id** | Must match `source_connid` in `dot_projects.json` |
| **Conn Type** | `Postgres` |
| **Host** | The external database hostname or IP |
| **Login / Password** | Credentials for that database |
| **Port** | The database port (default `5432` for Postgres) |
| **Schema / Database** | Leave **blank**. DOT applies `source_schema` at runtime. |

## Migrating to AWS EC2

To deploy DOT on an AWS EC2 instance for a more permanent setup:

### Provisioning & Setup

1. **Provision an Instance**: Recommend provisioning an Ubuntu instance (`t3.medium` or larger) on AWS EC2.
2. **Install Dependencies**: SSH into your instance and install Docker and Docker Compose.
3. **Clone Repository**: Clone the DOT repository to your instance.
4. **Environment Variables**: Set the `POSTGRES_PASSWORD` environment variable as you would locally.
5. **Build & Run**: Follow the Airflow Deployment steps above to build and start the containers.

### Secure Access (SSH Port Forwarding)

To securely access the UIs without exposing ports to the public internet, use SSH port forwarding from your local machine:

```bash
ssh -i <your-key.pem> -L 82:localhost:82 -L 8083:localhost:8083 -L 8080:localhost:8080 ubuntu@<ec2-ip>
```

For environments where you don't use SSH keys for authentication (keyless login):

```bash
ssh -L 82:localhost:82 -L 8083:localhost:8083 -L 8080:localhost:8080 -L 5433:localhost:5433 username@<remote-ip>
```

Once the tunnel is established, you can access the services locally:
- **Appsmith (DOT UI)**: [http://localhost:82](http://localhost:82)
- **Airflow**: [http://localhost:8083](http://localhost:8083)
- **Superset**: [http://localhost:8080](http://localhost:8080)
- **Database Client**: Connect via `localhost` on port `5433`.
