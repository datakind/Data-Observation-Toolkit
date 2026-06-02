from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from datetime import datetime

with DAG(
    dag_id = 'dot_orchestrator',
    schedule_interval = '@daily',
    start_date = datetime(2026, 6, 1),
    catchup = False,
    tags = ['learn']
) as dag:

    run_dot = BashOperator(
        task_id = "run_dot",
        bash_command = "cd /app/dot && eval `ssh-agent` && python run_everything.py --project_id EduProject"
)
