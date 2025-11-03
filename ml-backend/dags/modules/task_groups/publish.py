#!/usr/bin/env python
"""
Airflow task groups for publishing all Artefacts to databases on HAnS backend.
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


def publish_artefacts(
    parent_dag,
    dag_group_name_download_media_files,
    download_artefacts,
    artefacts,
    media_artefact,
    multiple_files_artefacts,
    meta_artefact,
    time_started,
):
    """
    Generate a publish_artefacts TaskGroup to be used in a DAG.
    Publishes all given artefacts on backend.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for
    download_media_files task group
    :param list(str) download_artefacts: List of download artefacts to be published
    :param list(str) artefacts: List of artefacts to be published
    :param Artefact media_artefact: Artefact which contains the media data for publishing
    :param Artefact multiple_files_artefacts: List of artefacts which contains the media thumbnails data, and slides images data
    :param Artefact meta_artefact: Artefact which contains the meta data for publishing
    :param str time_started: Start time of the DAG

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    from uuid import uuid4

    uuid_final = str(uuid4())

    with TaskGroup("publish_artefacts") as group9:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data
        from modules.operators.transfer import op_download_and_store_remote, op_publish
        from modules.operators.transfer import gen_artefacts_xcom_data
        from modules.operators.transfer import gen_publish_artefacts_xcom_data

        start = EmptyOperator(task_id=parent_dag.dag_id + "_publish_start")

        dyn_end = EmptyOperator(task_id=parent_dag.dag_id + "_publish_dyn_end")

        # Add the publishing artefact operators dynamically into the DAG
        for artefact in download_artefacts:
            subtask = op_download_and_store_remote(
                parent_dag,
                parent_dag.dag_id,
                "publish_artefact_" + artefact.artefact_id,
                dag_group_name_download_media_files,
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "{{ dag_run.conf['output'] }}",
                artefact,
                uuid_final,
            )
            start.set_downstream(subtask)
            subtask.set_downstream(dyn_end)

        # Add the publishing artefact operators dynamically into the DAG
        for artefact in artefacts:
            subtask = op_download_and_store_remote(
                parent_dag,
                parent_dag.dag_id,
                "publish_artefact_" + artefact.artefact_id,
                dag_group_name_download_media_files,
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "{{ dag_run.conf['output'] }}",
                artefact,
                uuid_final,
            )
            start.set_downstream(subtask)
            subtask.set_downstream(dyn_end)

        # Add the publishing artefact operators dynamically into the DAG
        for multiple_file_artefact in multiple_files_artefacts:
            subtask = op_download_and_store_remote(
                parent_dag,
                parent_dag.dag_id,
                "publish_artefact_" + multiple_file_artefact.artefact_id,
                dag_group_name_download_media_files,
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "{{ dag_run.conf['output'] }}",
                multiple_file_artefact,
                uuid_final,
            )
            start.set_downstream(subtask)
            subtask.set_downstream(dyn_end)

        mediatask = op_download_and_store_remote(
            parent_dag,
            parent_dag.dag_id,
            "publish_artefact_" + media_artefact.artefact_id,
            dag_group_name_download_media_files,
            inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            "{{ dag_run.conf['output'] }}",
            media_artefact,
            uuid_final,
        )
        dyn_end.set_downstream(mediatask)

        publish_task = op_publish(
            parent_dag,
            parent_dag.dag_id,
            "publish_meta_artefacts",
            "{{ dag_run.conf['output'] }}",
            inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            artefacts,
            gen_publish_artefacts_xcom_data(parent_dag, "publish_artefacts", artefacts),
            download_artefacts,
            gen_publish_artefacts_xcom_data(parent_dag, "publish_artefacts", download_artefacts),
            media_artefact,
            gen_publish_artefacts_xcom_data(parent_dag, "publish_artefacts", [media_artefact]),
            multiple_files_artefacts,
            gen_publish_artefacts_xcom_data(parent_dag, "publish_artefacts", multiple_files_artefacts),
            meta_artefact,
            time_started,
        )
        mediatask.set_downstream(publish_task)

    return group9


def publish_update_artefacts(
    parent_dag,
    dag_group_name_download_media_files,
    download_artefacts,
    artefacts,
    meta_artefact,
    time_started,
    editing_progress,
):
    """
    Generate a publish_artefacts TaskGroup to be used in a DAG.
    Publishes all given artefacts on backend.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for
    download_media_files task group
    :param list(str) download_artefacts: List of download artefacts to be published
    :param list(str) artefacts: List of artefacts to be published
    :param Artefact meta_artefact: Artefact which contains the meta data for publishing
    :param str time_started: Start time of the DAG
    :param int editing_progress: Progress step on frontend to be set

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    from uuid import uuid4

    uuid_final = str(uuid4())

    with TaskGroup("publish_update_artefacts") as group9:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data
        from modules.operators.transfer import op_download_and_store_remote, op_publish_update
        from modules.operators.transfer import gen_artefacts_xcom_data
        from modules.operators.transfer import gen_publish_artefacts_xcom_data

        start = EmptyOperator(task_id=parent_dag.dag_id + "_publish_start")

        dyn_end = EmptyOperator(task_id=parent_dag.dag_id + "_publish_dyn_end")

        # Add the publishing artefact operators dynamically into the DAG
        for artefact in download_artefacts:
            subtask = op_download_and_store_remote(
                parent_dag,
                parent_dag.dag_id,
                "publish_artefact_" + artefact.artefact_id,
                dag_group_name_download_media_files,
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "{{ dag_run.conf['output'] }}",
                artefact,
                uuid_final + time_started,
            )
            start.set_downstream(subtask)
            subtask.set_downstream(dyn_end)

        # Add the publishing artefact operators dynamically into the DAG
        for artefact in artefacts:
            subtask = op_download_and_store_remote(
                parent_dag,
                parent_dag.dag_id,
                "publish_artefact_" + artefact.artefact_id,
                dag_group_name_download_media_files,
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "{{ dag_run.conf['output'] }}",
                artefact,
                uuid_final + time_started,
            )
            start.set_downstream(subtask)
            subtask.set_downstream(dyn_end)

        publish_task = op_publish_update(
            parent_dag,
            parent_dag.dag_id,
            "publish_meta_artefacts",
            "{{ dag_run.conf['output'] }}",
            inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            artefacts,
            gen_publish_artefacts_xcom_data(parent_dag, "publish_update_artefacts", artefacts),
            download_artefacts,
            gen_publish_artefacts_xcom_data(parent_dag, "publish_update_artefacts", download_artefacts),
            meta_artefact,
            time_started,
            editing_progress,
        )
        dyn_end.set_downstream(publish_task)

    return group9
