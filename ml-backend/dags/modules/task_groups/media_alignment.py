#!/usr/bin/env python
"""
Airflow task groups for Video-to-Slide (VTS) Alignment.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"

from airflow.utils.task_group import TaskGroup


def media_alignment(
    parent_dag,
    dag_group_name_download_media_files,
    dag_group_name_asr_engine,
    dag_group_name_slides_processor,
    config={},
) -> TaskGroup:
    """
    Generate a media_alignment TaskGroup to be used in a DAG.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download media files task group
    :param str dag_group_name_asr_engine: Task group name for asr engine task group
    :param str dag_group_name_slides_processor: Task group name for slides processor task group

    :param dict config: Configuration

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    mode = "local"
    if "mode" in config:
        mode = config["mode"].lower()

    alignment_config = {}
    if mode == "local" and "local_config" in config:
        alignment_config = config["local_config"]
    elif mode == "remote" and "remote_config" in config:
        alignment_config = config["remote_config"]

    llm_configs = {}
    if "llm_configs" in config:
        llm_configs = config["llm_configs"]

    with TaskGroup("media_alignment") as group10:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        if mode == "local":
            from modules.operators.vts_alignment_local import op_vts_alignment_local

            t1 = op_vts_alignment_local(
                parent_dag,
                parent_dag.dag_id,
                "align_video_to_slides",
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "video_url",
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "video_filename",
                inject_xcom_data(
                    parent_dag.dag_id,
                    dag_group_name_slides_processor,
                    "op_create_new_urn_on_assetdbtemp",
                    "slides_images_urn",
                ),
                "slides_images_urn",
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_asr_engine, "op_get_single_data_from_xcom_json", "asr_locale"
                ),
                "asr_locale",
                inject_xcom_data(
                    parent_dag.dag_id,
                    dag_group_name_asr_engine,
                    "op_create_new_urn_on_assetdbtemp",
                    "transcript_de_urn",
                ),
                "transcript_de_urn",
                inject_xcom_data(
                    parent_dag.dag_id,
                    dag_group_name_asr_engine,
                    "op_create_new_urn_on_assetdbtemp",
                    "transcript_en_urn",
                ),
                "transcript_en_urn",
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "meta_urn",
                config=alignment_config,
            )
            t1.doc_md = """\
              #Video-to-Slide (VTS) Alignment local using tesseract and text embeddings only
              """
        else:
            from modules.operators.vts_alignment_remote import op_vts_alignment_remote

            t1 = op_vts_alignment_remote(
                parent_dag,
                parent_dag.dag_id,
                "align_video_to_slides",
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "video_url",
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "video_filename",
                inject_xcom_data(
                    parent_dag.dag_id,
                    dag_group_name_slides_processor,
                    "op_create_new_urn_on_assetdbtemp",
                    "slides_images_urn",
                ),
                "slides_images_urn",
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_asr_engine, "op_get_single_data_from_xcom_json", "asr_locale"
                ),
                "asr_locale",
                inject_xcom_data(
                    parent_dag.dag_id,
                    dag_group_name_asr_engine,
                    "op_create_new_urn_on_assetdbtemp",
                    "transcript_de_urn",
                ),
                "transcript_de_urn",
                inject_xcom_data(
                    parent_dag.dag_id,
                    dag_group_name_asr_engine,
                    "op_create_new_urn_on_assetdbtemp",
                    "transcript_en_urn",
                ),
                "transcript_en_urn",
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "meta_urn",
                config=alignment_config,
                llm_configs=llm_configs,
            )
            t1.doc_md = """\
              #Video-to-Slide (VTS) Alignment remote using vision language model and multilingual multimodal embeddings
              """

        t1

    return group10
