#!/usr/bin/env python
"""
Airflow task groups for slides processing.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"

from airflow.utils.task_group import TaskGroup


def slides_processor(parent_dag, dag_group_name_download_media_files, config={}) -> TaskGroup:
    """
    Generate a slides_processor TaskGroup to be used in a DAG.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download media files task group

    :param str config: Configuration for used asr engine with keys e.g. use_gpu

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    dpi = 150
    if "dpi" in config:
        dpi = config["dpi"]
    llm_configs = {}
    if "llm_configs" in config:
        llm_configs = config["llm_configs"]

    with TaskGroup("slides_processor") as group3:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        # Create urn with new uuid for topic result on assetdb-temp
        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        # Create urn with new uuid for slides images on assetdb-temp
        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        t0 = op_create_new_urn_on_assetdbtemp(parent_dag, parent_dag.dag_id, "slides_images_urn", "slides_images_urn")

        from modules.operators.slides_to_images import op_slides_to_images

        t1 = op_slides_to_images(
            parent_dag,
            parent_dag.dag_id,
            "create_slides_images",
            inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            "slides_urn",
            inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            "slides_filename",
            inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            "meta_urn",
            inject_xcom_data(
                parent_dag.dag_id, "slides_processor", "op_create_new_urn_on_assetdbtemp", "slides_images_urn"
            ),
            "slides_images_urn",
            dpi,
        )
        t1.doc_md = """\
          #Convert PDF to PNG and store in vector format json
          Creates a images of slides file and saves them in vector slides format json on assetdb-temp.
          """

        from modules.operators.vllm_remote import op_vllm_remote_prompt

        t2 = op_vllm_remote_prompt(
            parent_dag,
            parent_dag.dag_id,
            "extract_slide_text_embed",
            "ocr",
            inject_xcom_data(
                parent_dag.dag_id, "slides_processor", "op_create_new_urn_on_assetdbtemp", "slides_images_urn"
            ),
            "slides_images_urn",
            inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            "meta_urn",
            "not_needed_for_mode",
            "not_needed_for_mode",
            llm_configs,
        )
        t2.doc_md = """\
          #OCR text from vector format jsons and create meta jsons
          Extracts the text and embedds is to vector format jsons and adds an additional meta json including e.g. detected urls in text and saves or updates them on assetdb-temp.
          """

        t0 >> t1 >> t2

    return group3
