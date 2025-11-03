#!/usr/bin/env python
"""
Airflow task groups for archiving all Artefacts as a package on assetdb-temp archive bucket.
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
from airflow.models.baseoperator import chain
from airflow.operators.empty import EmptyOperator


def archive_artefacts(parent_dag, dag_group_name_download_media_files, download_artefacts, artefacts, time_started):
    """
    Generate a archive_artefacts TaskGroup to be used in a DAG.
    Archives all given artefacts on assetdb-temp archive bucket.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for
    download_media_files task group
    :param list(str) download_artefacts: List of download artefacts to be archived
    :param list(str) artefacts: List of artefacts to be archived
    :param str time_started: Start time of the DAG

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    from uuid import uuid4

    uuid_final = str(uuid4())

    with TaskGroup("archive_artefacts") as group10:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data
        from modules.operators.transfer import op_archive_artefacts

        start = EmptyOperator(task_id=parent_dag.dag_id + "_archive_start")

        archive_task = op_archive_artefacts(
            parent_dag,
            parent_dag.dag_id,
            "archive_artefacts",
            download_artefacts,
            inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            artefacts,
            uuid_final,
            time_started,
        )

        end = EmptyOperator(task_id=parent_dag.dag_id + "_archive_end")

        start >> archive_task >> end

    return group10
