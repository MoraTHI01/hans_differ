#!/usr/bin/env python
"""
Airflow task groups for text normalization.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import pendulum

from airflow import DAG
from airflow.exceptions import AirflowConfigException
from airflow.utils.task_group import TaskGroup


def nlp_text_normalization(parent_dag, dag_group_name_asr_engine, container_id):
    """
    Generate a nlp_text_normalization TaskGroup to be used in a DAG.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_asr_engine: Task group name for asr_engine task group
    :param str container_id: Container Id for DockerOperator

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """

    with TaskGroup("nlp_text_normalization") as group7:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        # Create urn with new uuid for transcript on assetdb-temp
        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        t0 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "transcript_urn", "transcript_urn", ".json"
        )

        # Create url "transcript_url_upload" using previous urn "transcript_urn" on assetdb-temp
        from modules.operators.storage import op_create_url_by_xcom

        t1 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "transcript_url_upload",
            "transcript_url_upload",
            inject_xcom_data(
                parent_dag.dag_id, "nlp_text_normalization", "op_create_new_urn_on_assetdbtemp", "transcript_urn"
            ),
            "transcript_urn",
            "upload",
        )

        from modules.operators.docker_nlp import op_docker_nlp_text_normalization

        t2 = op_docker_nlp_text_normalization(
            parent_dag.dag_id,
            "transcript",
            container_id,
            inject_xcom_data(parent_dag.dag_id, dag_group_name_asr_engine, "op_create_url_by_xcom", "asr_result_url"),
            "asr_result_url",
            inject_xcom_data(
                parent_dag.dag_id, dag_group_name_asr_engine, "op_get_single_data_from_xcom_json", "asr_locale"
            ),
            "asr_locale",
            inject_xcom_data(
                parent_dag.dag_id, "nlp_text_normalization", "op_create_url_by_xcom", "transcript_url_upload"
            ),
            "transcript_url_upload",
        )
        t2.doc_md = """\
          #NLP Text Normalization
          Create transcript from asr_result.json file by adding
          capitalization, punctuation and number conversion
          and save it in assetdb-temp
          """

        # Create url "transcript_url" using previous urn "transcript_urn" on assetdb-temp for download
        from modules.operators.storage import op_create_url_by_xcom

        t3 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "transcript_url",
            "transcript_url",
            inject_xcom_data(
                parent_dag.dag_id, "nlp_text_normalization", "op_create_new_urn_on_assetdbtemp", "transcript_urn"
            ),
            "transcript_urn",
            "download",
        )

        t0 >> t1 >> t2 >> t3

    return group7
