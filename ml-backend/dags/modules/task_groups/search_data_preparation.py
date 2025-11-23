#!/usr/bin/env python
"""
Airflow task groups for search engine data preparation.
"""
__author__ = "Christopher Simic, Fabian Schneider, Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import pendulum

from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.utils.task_group import TaskGroup
from airflow.operators.empty import EmptyOperator


def search_data_preparation(
    parent_dag,
    dag_group_name_download_media_files,
    dag_group_name_asr_engine,
    dag_group_name_summarization,
    config: dict,
):
    """
    Generate a search_data_preparation TaskGroup to be used in a DAG.
    Global video search data preparation.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download_media_files task group
    :param str dag_group_name_asr_engine: Task group name for asr_engine task group
    :param str dag_group_name_summarization: Task group name for summarization task group
    :param str config: Configuration of docker operator (e.g. gpu usage)

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    llm_configs = {}
    if "llm_configs" in config:
        llm_configs = config["llm_configs"]

    with TaskGroup("search_data_preparation") as task_group:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        # Create urn with new uuid for opensearch_document on assetdb-temp
        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        t1 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "search_data_urn", "search_data_urn", ".json"
        )

        # Create opensearch document
        from modules.operators.opensearch import op_create_opensearch_document

        t2 = op_create_opensearch_document(
            dag=parent_dag,
            dag_id=parent_dag.dag_id,
            task_id_suffix="create_opensearch_document",
            asr_de_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_asr_engine, "op_create_new_urn_on_assetdbtemp", "asr_result_de_urn"
            ),
            asr_de_data_key="asr_result_de_urn",
            asr_en_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_asr_engine, "op_create_new_urn_on_assetdbtemp", "asr_result_en_urn"
            ),
            asr_en_data_key="asr_result_en_urn",
            asr_locale_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_asr_engine, "op_get_single_data_from_xcom_json", "asr_locale"
            ),
            asr_locale_key="asr_locale",
            download_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            download_meta_urn_key="meta_urn",
            opensearch_data=inject_xcom_data(
                parent_dag.dag_id, "search_data_preparation", "op_create_new_urn_on_assetdbtemp", "search_data_urn"
            ),
            opensearch_urn_key="search_data_urn",
        )

        # Create url "search_data_url" using previous urn "search_data_urn" on assetdb-temp for download
        from modules.operators.storage import op_create_url_by_xcom

        t3 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "search_data_url",
            "search_data_url",
            inject_xcom_data(
                parent_dag.dag_id, "search_data_preparation", "op_create_new_urn_on_assetdbtemp", "search_data_urn"
            ),
            "search_data_urn",
            "download",
        )

        # Opensearch vectors
        # Create urn with new uuid for opensearch_vectors on assetdb-temp
        t4 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "search_data_vectors_urn", "search_data_vectors_urn", ".json"
        )

        # Create opensearch vectors
        from modules.operators.opensearch_vectors import op_create_opensearch_vectors

        t5 = op_create_opensearch_vectors(
            dag=parent_dag,
            dag_id=parent_dag.dag_id,
            task_id_suffix="create_opensearch_vectors",
            transcript_en_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_asr_engine, "op_create_new_urn_on_assetdbtemp", "transcript_en_urn"
            ),
            transcript_en_data_key="transcript_en_urn",
            asr_locale_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_asr_engine, "op_get_single_data_from_xcom_json", "asr_locale"
            ),
            asr_locale_key="asr_locale",
            download_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            download_meta_urn_key="meta_urn",
            opensearch_data=inject_xcom_data(
                parent_dag.dag_id,
                "search_data_preparation",
                "op_create_new_urn_on_assetdbtemp",
                "search_data_vectors_urn",
            ),
            opensearch_urn_key="search_data_vectors_urn",
            llm_configs=llm_configs,
        )

        # Create url "search_data_vectors_url" using previous urn "search_data_vectors_urn" on assetdb-temp for download
        from modules.operators.storage import op_create_url_by_xcom

        t6 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "search_data_vectors_url",
            "search_data_vectors_url",
            inject_xcom_data(
                parent_dag.dag_id,
                "search_data_preparation",
                "op_create_new_urn_on_assetdbtemp",
                "search_data_vectors_urn",
            ),
            "search_data_vectors_urn",
            "download",
        )

        # todo: create video vector
        t7 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "search_summary_data_vector_urn", "search_summary_data_vector_urn", ".json"
        )

        # Create opensearch vectors
        from modules.operators.opensearch_summary_vector import op_create_opensearch_summary_vector

        t8 = op_create_opensearch_summary_vector(
            dag=parent_dag,
            dag_id=parent_dag.dag_id,
            task_id_suffix="create_opensearch_summary_vector",
            summary_data=inject_xcom_data(
                parent_dag.dag_id,
                dag_group_name_summarization,
                "op_create_new_urn_on_assetdbtemp",
                "summary_result_de_urn",
            ),
            summary_data_key="summary_result_de_urn",
            # asr_locale_data=inject_xcom_data(
            #     parent_dag.dag_id, dag_group_name_asr_engine, "op_get_single_data_from_xcom_json", "asr_locale"
            # ),
            # asr_locale_key="asr_locale",
            download_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            download_meta_urn_key="meta_urn",
            opensearch_data=inject_xcom_data(
                parent_dag.dag_id,
                "search_data_preparation",
                "op_create_new_urn_on_assetdbtemp",
                "search_summary_data_vector_urn",
            ),
            opensearch_urn_key="search_summary_data_vector_urn",
            llm_configs=llm_configs,
        )

        # Create url "search_summary_data_vector_url" using previous urn "search_summary_data_vector_urn" on assetdb-temp for download
        from modules.operators.storage import op_create_url_by_xcom

        t9 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "search_summary_data_vector_url",
            "search_summary_data_vector_url",
            inject_xcom_data(
                parent_dag.dag_id,
                "search_data_preparation",
                "op_create_new_urn_on_assetdbtemp",
                "search_summary_data_vector_urn",
            ),
            "search_summary_data_vector_urn",
            "download",
        )

        [
            t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7 >> t8 >> t9,
            _local_search_data_preparation(parent_dag, dag_group_name_download_media_files, dag_group_name_asr_engine),
        ]

    return task_group


def _local_search_data_preparation(parent_dag, dag_group_name_download_media_files, dag_group_name_asr_engine):
    """
    Generate a local_search_data_preparation TaskGroup to be used in a DAG.
    Local video search data preparation.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download_media_files task group
    :param str dag_group_name_asr_engine: Task group name for asr_engine task group

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """

    # new

    with TaskGroup("local_search_data_preparation") as task_group:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        # Create urn with new uuid for search_trie on assetdb-temp
        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        t4 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "local_search_data_de_urn", "local_search_data_de_urn", ".json"
        )

        t5 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "local_search_data_en_urn", "local_search_data_en_urn", ".json"
        )

        # Create local_search document
        from modules.operators.local_search import op_create_local_search_document

        t6 = op_create_local_search_document(
            dag=parent_dag,
            dag_id=parent_dag.dag_id,
            task_id_suffix="create_local_search_document",
            asr_de_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_asr_engine, "op_create_new_urn_on_assetdbtemp", "asr_result_de_urn"
            ),
            asr_de_data_key="asr_result_de_urn",
            asr_en_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_asr_engine, "op_create_new_urn_on_assetdbtemp", "asr_result_en_urn"
            ),
            asr_en_data_key="asr_result_en_urn",
            asr_locale_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_asr_engine, "op_get_single_data_from_xcom_json", "asr_locale"
            ),
            asr_locale_key="asr_locale",
            download_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            download_meta_urn_key="meta_urn",
            local_search_data_de=inject_xcom_data(
                parent_dag.dag_id,
                "search_data_preparation.local_search_data_preparation",
                "op_create_new_urn_on_assetdbtemp",
                "local_search_data_de_urn",
            ),
            local_search_de_urn_key="local_search_data_de_urn",
            local_search_data_en=inject_xcom_data(
                parent_dag.dag_id,
                "search_data_preparation.local_search_data_preparation",
                "op_create_new_urn_on_assetdbtemp",
                "local_search_data_en_urn",
            ),
            local_search_en_urn_key="local_search_data_en_urn",
        )

        # Create url "search_data_url" using previous urn "search_data_urn" on assetdb-temp for download
        from modules.operators.storage import op_create_url_by_xcom

        t7 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "local_search_data_de_url",
            "local_search_data_de_url",
            inject_xcom_data(
                parent_dag.dag_id,
                "search_data_preparation.local_search_data_preparation",
                "op_create_new_urn_on_assetdbtemp",
                "local_search_data_de_urn",
            ),
            "local_search_data_de_urn",
            "download",
        )

        t8 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "local_search_data_en_url",
            "local_search_data_en_url",
            inject_xcom_data(
                parent_dag.dag_id,
                "search_data_preparation.local_search_data_preparation",
                "op_create_new_urn_on_assetdbtemp",
                "local_search_data_en_urn",
            ),
            "local_search_data_en_urn",
            "download",
        )

        t4 >> t5 >> t6 >> t7 >> t8
