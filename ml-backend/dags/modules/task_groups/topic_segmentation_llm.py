#!/usr/bin/env python
"""
Airflow task groups for summarization.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2023, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import pendulum

from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.utils.task_group import TaskGroup
from airflow.operators.empty import EmptyOperator


def topic_segmentation(
    parent_dag, dag_group_name_download_media_files, dag_group_name_asr_engine, container_id, config={}
):
    """
    Generate a summarization TaskGroup to be used in a DAG.
    Summarization of the lecture transcripts to a short summary and perform topic segmentation.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download_media_files task group
    :param str dag_group_name_asr_engine: Task group name for asr_engine task group
    :param str container_id: Container Id for DockerOperator
    :param str config: Configuration for used asr engine with keys e.g. use_gpu

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    use_nlp_translate_remote = False
    if "use_nlp_translate_remote" in config:
        use_nlp_translate_remote = config["use_nlp_translate_remote"]
    llm_configs = {}
    if "llm_configs" in config:
        llm_configs = config["llm_configs"]
    with TaskGroup("topic_segmentation") as task_group:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        # Topic Segmentation Tasks

        # Create urn with new uuid for topic segmentation result on assetdb-temp
        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        t0 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "topic_result_de_urn", "topic_result_de_urn", ".json"
        )

        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        t1 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "topic_result_en_urn", "topic_result_en_urn", ".json"
        )

        # Create topic segmentation
        from modules.operators.llm_remote import op_llm_remote_prompt

        t2 = op_llm_remote_prompt(
            dag=parent_dag,
            dag_id=parent_dag.dag_id,
            task_id_suffix="topic_segmentation",
            mode="topic",
            context_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_asr_engine, "op_create_new_urn_on_assetdbtemp", "subtitle_en_urn"
            ),
            context_data_key="subtitle_en_urn",
            download_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            download_meta_urn_key="meta_urn",
            upload_llm_result_data=inject_xcom_data(
                parent_dag.dag_id, "topic_segmentation", "op_create_new_urn_on_assetdbtemp", "topic_result_en_urn"
            ),
            upload_llm_result_urn_key="topic_result_en_urn",
            llm_configs=llm_configs,
        )

        # Create url "topic_result_en_url" using previous urn "topic_result_en_urn" on assetdb-temp for download
        from modules.operators.storage import op_create_url_by_xcom

        t3 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "topic_result_en_url",
            "topic_result_en_url",
            inject_xcom_data(
                parent_dag.dag_id, "topic_segmentation", "op_create_new_urn_on_assetdbtemp", "topic_result_en_urn"
            ),
            "topic_result_en_urn",
            "download",
        )

        # Translation of topic_result_en_urn to topic_result_de_urn

        # Create url "topic_result_de_url" using previous urn "topic_result_de_urn" on assetdb-temp for upload
        from modules.operators.storage import op_create_url_by_xcom

        t4 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "topic_result_de_url_upload",
            "topic_result_de_url_upload",
            inject_xcom_data(
                parent_dag.dag_id, "topic_segmentation", "op_create_new_urn_on_assetdbtemp", "topic_result_de_urn"
            ),
            "topic_result_de_urn",
            "upload",
        )

        if use_nlp_translate_remote is False:
            # Translate short summary English to German
            from modules.operators.docker_nlp import op_docker_nlp_translate_local

            t5 = op_docker_nlp_translate_local(
                parent_dag.dag_id,
                "trl_topic_segmentation",
                container_id,
                inject_xcom_data(
                    parent_dag.dag_id, "topic_segmentation", "op_create_url_by_xcom", "topic_result_en_url"
                ),
                "topic_result_en_url",
                "de",
                inject_xcom_data(
                    parent_dag.dag_id, "topic_segmentation", "op_create_url_by_xcom", "topic_result_de_url_upload"
                ),
                "topic_result_de_url_upload",
                config,
            )
            t5.doc_md = """\
              #NLP Translation
              Translate ShortSummaryResult json or TopicResult json to target language
              and save it in assetdb-temp
              """
        else:
            # Translate short summary English to German
            from modules.operators.nlp_translate import op_nlp_translate_remote

            t5 = op_nlp_translate_remote(
                dag=parent_dag,
                dag_id=parent_dag.dag_id,
                task_id_suffix="trl_topic_segmentation",
                source_language="en",
                target_language="de",
                download_data=inject_xcom_data(
                    parent_dag.dag_id, "topic_segmentation", "op_create_new_urn_on_assetdbtemp", "topic_result_en_urn"
                ),
                download_data_key="topic_result_en_urn",
                upload_data=inject_xcom_data(
                    parent_dag.dag_id, "topic_segmentation", "op_create_new_urn_on_assetdbtemp", "topic_result_de_urn"
                ),
                upload_data_key="topic_result_de_urn",
                llm_configs=llm_configs,
            )
            t5.doc_md = """\
              #NLP Translation
              Translate ShortSummaryResult json or TopicResult json to target language
              and save it in assetdb-temp
              """

        # Create url "short_summary_result_de_url" using previous urn "short_summary_result_de_urn" on assetdb-temp for download
        from modules.operators.storage import op_create_url_by_xcom

        t6 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "topic_result_de_url",
            "topic_result_de_url",
            inject_xcom_data(
                parent_dag.dag_id, "topic_segmentation", "op_create_new_urn_on_assetdbtemp", "topic_result_de_urn"
            ),
            "topic_result_de_urn",
            "download",
        )

        t0 >> t1 >> t2 >> t3 >> t4 >> t5 >> t6

    return task_group
