from datetime import datetime, timedelta

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
    "description": "Create HAnS channel package from assetdb-temp archive bucket",
    "depend_on_past": False,
    "start_date": START_DATE,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# DAG name is the dag_id and needs to contain a version string at the end.
# The version part is starting with "_v" and uses semantic versioning
# A new major version will result in a new hans python file, e.g. "create_hans_channel_package_v2.py"
# A new TaskGroup which is introduced will increase the minor version, e.g. "create_hans_channel_package_v1.1.0"
# Fixes will increase the last part of the version number, e.g. "create_hans_channel_package_v1.0.1"
# Limit active DAG runs to 1 to not create a channel package in parallel,
# see https://www.astronomer.io/guides/airflow-scaling-workers/ and
# https://airflow.apache.org/docs/apache-airflow/stable/faq.html#how-to-improve-dag-performance
DAG_NAME = "create_hans_channel_package_v1.0.0"
with DAG(DAG_NAME, default_args=default_args, schedule_interval=None, catchup=False, max_active_runs=1) as dag:
    now = datetime.now()
    time_started = now.strftime("%m_%d_%Y_%H_%M_%S")

    from uuid import uuid4

    uuid_channel_package = str(uuid4())

    # Used to create unique docker container id
    container_id = time_started

    start = EmptyOperator(task_id=dag.dag_id + "_create_hans_channel_package_start")

    from modules.operators.transfer import op_create_channel_package_upload_url

    upload_url_task = op_create_channel_package_upload_url(
        dag, dag.dag_id, "create_channel_package_url", "{{ dag_run.conf['output'] }}", uuid_channel_package
    )

    from modules.operators.xcom import inject_xcom_data
    from modules.operators.docker_package import op_docker_create_channel_package

    package_task = op_docker_create_channel_package(
        dag.dag_id,
        "create_channel_package",
        container_id,
        uuid_channel_package,
        inject_xcom_data(dag.dag_id, "", "op_create_channel_package_upload_url", "create_channel_package_url"),
        "{{ dag_run.conf['channel'] }}",
    )

    end = EmptyOperator(task_id=dag.dag_id + "_create_hans_channel_package_end")

    start >> upload_url_task >> package_task >> end
