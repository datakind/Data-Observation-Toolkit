# DOT Execution Guide

This guide explains how to manually trigger the DOT pipeline to evaluate your data against the rules defined in your configuration, as well as how to trigger scheduled runs in Airflow. 

*(For instructions on setting up the Airflow connections and schemas, refer to [deployment.md](./deployment.md)).*

## Table of Contents
- [Manual Pipeline Execution](#manual-pipeline-execution)
- [Triggering the Airflow DAG](#triggering-the-airflow-dag)
- [Reviewing the Results](#reviewing-the-results)

---

## Manual Pipeline Execution

> ⚠️ **Important:** Manual execution is exclusively for the non-Airflow deployment. It will **not** work if your Docker containers are set up for Airflow orchestration. For instructions on the required non-Airflow environment, refer to [The Not-So-Quick Start: Manual Docker Build](./deployment.md#the-not-so-quick-start-manual-docker-build).

If you are using the manual deployment, you can trigger the pipeline from your terminal to evaluate your rules immediately:

1. Open a new terminal window on the machine hosting the Docker containers.
2. Access the running DOT container via bash:
   ```bash
   docker exec -it dot bash
   ```
3. Navigate to the internal application directory:
   ```bash
   cd /app/dot
   ```
4. Execute the pipeline for your target project. Be sure to replace `'ScanProject1'` with the actual name of your project (e.g., `'EduProject'`):
   ```bash
   python run_everything.py --project_id 'ScanProject1'
   ```
5. The terminal will output logs as `dbt` and Great Expectations evaluate the rules. When it completes, you will see a success message indicating the failures have been stored in `dot.test_results`.

---

## Triggering the Airflow DAG

If you have deployed DOT using Airflow (see [Deploying with Apache Airflow](./deployment.md#deploying-with-apache-airflow)), you can trigger the synchronization and testing pipeline directly from the UI.

> 🎥 **Video:** [Triggering the DAG and dot_config.yml](../videos/04_triggering_the_airflow_dag.mp4)
> *(To understand the `dot_config.yml` file mentioned in the video, see the [Database Connection Registry](./architecture_and_troubleshooting.md#database-connection-registry-dot_configyml)).*

1. Navigate to the Airflow UI (typically at `http://localhost:8083`).
2. Log in with your credentials (default: `airflow` / `airflow`).
3. Click on **DAGs** in the top navigation menu.
4. Use the search box to search for `dot`.
5. Toggle the `run_dot_project` DAG to **Active** using the switch on the left side of the row.
6. Click the **Play (Trigger DAG)** button under the *Actions* column to start the run.
7. You can monitor the progress by clicking on the DAG name and viewing the individual task logs.

---

## Reviewing the Results

Once the pipeline (either manual or Airflow) has finished executing, DOT writes the exact failing rows to the database.

1. Open the Appsmith DOT UI.
2. Open **Run monitoring** in the top bar. This shows the **Run log**.
3. Use the search box to find your project (for example, `ScanProject1` or `EduProject`).
4. Each row shows the run date, rows tested, rows failed, percent failed, and run status.
5. Click **View** in the Run results column to open that run.
