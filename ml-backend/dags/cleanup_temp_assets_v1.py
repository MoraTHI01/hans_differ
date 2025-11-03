from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.configuration import conf
from airflow.operators.dummy import DummyOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator, BranchPythonOperator


now = pendulum.now(tz="UTC")
now_to_the_hour = (now - timedelta(0, 0, 0, 0, 0, 3)).replace(minute=0, second=0, microsecond=0)
START_DATE = now_to_the_hour

default_args = {
    "owner": "airflow",
    "description": "Cleanup assetdb-temp assets-temp bucket",
    "depend_on_past": False,
    "start_date": START_DATE,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# DAG name is the dag_id and needs to contain a version string at the end.
# The version part is starting with "_v" and uses semantic versioning
# A new major version will result in a new hans python file, e.g. "cleanup_temp_assets_v2.py"
# A new TaskGroup which is introduced will increase the minor version, e.g. "cleanup_temp_assets_v1.1.0"
# Fixes will increase the last part of the version number, e.g. "cleanup_temp_assets_v1.0.1"
# Limit active DAG runs to 1 to not cleanup in parallel,
# see https://www.astronomer.io/guides/airflow-scaling-workers/ and
# https://airflow.apache.org/docs/apache-airflow/stable/faq.html#how-to-improve-dag-performance
DAG_NAME = "cleanup_temp_assets_v1.0.0"
with DAG(DAG_NAME, default_args=default_args, schedule_interval=None, catchup=False, max_active_runs=1) as dag:

    start = EmptyOperator(task_id=dag.dag_id + "_cleanup_temp_assets_start")

    from modules.operators.storage import op_cleanup_assetdbtemp_assets_temp

    cleanup_task = op_cleanup_assetdbtemp_assets_temp(dag, dag.dag_id, "cleanup_temp_assets")

    end = EmptyOperator(task_id=dag.dag_id + "_cleanup_temp_assets_end")

    start >> cleanup_task >> end
