from airflow import DAG
from airflow.operators import BashOperator
fromasf airflow.models import Variable


with DAG(
    dag_id = 'dot_orchestrator',
    catchup = False,
    tags = ['learn']
) as dag:

    run_dot = BashOperator(
        task_id = "run_dot",
        env = {"POSTGRES_PASSWORD": Variable.get('POSTGRES_PASSWORD', default_var='postgres')},
        bash_command = "cd /app/dot && eval `ssh-agent` && python run_everything.py --project_id EduProject"
)
