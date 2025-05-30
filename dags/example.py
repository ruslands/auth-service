from datetime import datetime

from integration.airflow.job_wrapper import job_wrapper

from airflow import DAG
from airflow.operators.python import PythonOperator


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "start_date": datetime(2023, 1, 1),
}

with DAG(
    dag_id="example",
    default_args=default_args,
    description="example",
    catchup=False,
    max_active_runs=1,
    tags=["example"],
    is_paused_upon_creation=True,
    schedule_interval="1 * * * *",
):
    PythonOperator(
        task_id="job_wrapper_runner",
        python_callable=job_wrapper("jobs.example.main.lambda_handler"),
    )
