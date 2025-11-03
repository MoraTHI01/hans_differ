#!/usr/bin/env python
"""
Airflow task groups for download.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import pendulum

from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.utils.task_group import TaskGroup


def download_media_files(parent_dag):
    """
    Generate a download_media_files TaskGroup to be used in a DAG.

    :param DAG parent_dag: Parent DAG instance

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    with TaskGroup("download_media_files") as group0:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        # Transfer files from backend databases to local assetdb-temp database
        # Provide input files via xcom
        from modules.operators.transfer import op_download_and_store_local

        t0 = op_download_and_store_local(
            parent_dag,
            parent_dag.dag_id,
            "download",
            "{{ dag_run.conf['metaUrn'] }}",
            "{{ dag_run.conf['input'] }}",
            "{{ dag_run.conf['output'] }}",
        )

        t0

    return group0
