#!/usr/bin/env python
"""
Docker operators for NLP.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from airflow import DAG
from airflow.operators.docker_operator import DockerOperator


def op_docker_nlp_text_normalization(
    dag_id,
    task_id_suffix,
    containerid,
    asr_data,
    asr_data_key,
    asr_locale_data,
    asr_locale_key,
    upload_data,
    upload_data_key,
):
    """
    Provides DockerOperator for NLP text normalization.
    Creates a transcript from raw audio and saves it as asr_result.json in assetdb-temp.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id, e.g. transcript
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str asr_data: XCOM Data which contains download url for asr_result.json.
    :param str asr_data_key: XCOM Data key to used to determine the download url.
    :param str asr_locale_data: XCOM Data which contains the asr locale.
    :param str asr_locale_key: XCOM Data key to used to determine the asr locale.
    :param str upload_data: XCOM Data which contains upload url.
    :param str upload_data_key: XCOM Data key to used to determine the upload url.

    :return: DockerOperator NLP text normalization
    """
    from datetime import timedelta
    from modules.operators.docker_helper import get_docker_url, gen_container_name, gen_image_name
    from modules.operators.xcom import gen_task_id

    docker_command = "./normalize.sh -d " + asr_data_key + " -l " + asr_locale_key + " -u " + upload_data_key + " -v"

    return DockerOperator(
        task_id=gen_task_id(dag_id, "op_docker_nlp_text_normalization", task_id_suffix),
        image=gen_image_name("nlp-text-normalization"),
        container_name=gen_container_name("nlp-text-normalization", containerid),
        api_version="auto",
        # Useful for debugging
        auto_remove="success",
        privileged=True,
        execution_timeout=timedelta(seconds=86400),
        command=docker_command,
        environment={"DOWNLOAD_DATA": asr_data, "UPLOAD_DATA": upload_data, "ASR_LOCALE": asr_locale_data},
        docker_url=get_docker_url(),
        network_mode="container:hans-ml-backend-assetdb-temp",
    )


def op_docker_nlp_translate_local(
    dag_id,
    task_id_suffix,
    containerid,
    download_data,
    download_data_key,
    target_locale,
    upload_data,
    upload_data_key,
    config={},
):
    """
    Provides DockerOperator for NLP translation.
    Creates a transcript from raw audio and saves it as asr_result.json in assetdb-temp.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id, e.g. transcript
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str download_data: XCOM Data which contains download url for llm json result.
    :param str download_data_key: XCOM Data key to used to determine the download url.
    :param str target_locale: Target locale for translation, could be 'de' or 'en'.
    :param str upload_data: XCOM Data which contains upload url.
    :param str upload_data_key: XCOM Data key to used to determine the upload url.
    :param str config: Configuration with supported keys: use_gpu.

    :return: DockerOperator NLP translation
    """
    from datetime import timedelta
    from docker.types import DeviceRequest
    from modules.operators.docker_helper import get_docker_url, gen_container_name, gen_image_name
    from modules.operators.xcom import gen_task_id

    use_gpu = False
    if "use_gpu" in config:
        use_gpu = config["use_gpu"]

    docker_command = (
        "./translate.sh -d " + download_data_key + " -l " + target_locale + " -u " + upload_data_key + " -v"
    )

    if use_gpu is True:
        docker_command = docker_command + " -g"
        return DockerOperator(
            task_id=gen_task_id(dag_id, "op_docker_nlp_translate_local", task_id_suffix),
            image=gen_image_name("nlp-translate-local"),
            container_name=gen_container_name("nlp-translate-local", containerid),
            api_version="auto",
            # Useful for debugging
            auto_remove="success",
            privileged=True,
            execution_timeout=timedelta(seconds=172800),
            command=docker_command,
            environment={"DOWNLOAD_DATA": download_data, "UPLOAD_DATA": upload_data},
            docker_url=get_docker_url(),
            network_mode="container:hans-ml-backend-assetdb-temp",
            # count 1 means one gpu, -1 means all gpu's
            # or use specific list of device_ids=["0,1,2,3,4,5,6,7"], device_ids=[gen_next_gpu_id()]
            # https://stackoverflow.com/questions/71429711/how-to-run-a-docker-container-with-specific-gpus-using-docker-sdk-for-python
            device_requests=[DeviceRequest(count=1, capabilities=[["gpu"]])],
        )
    return DockerOperator(
        task_id=gen_task_id(dag_id, "op_docker_nlp_translate_local", task_id_suffix),
        image=gen_image_name("nlp-translate-local"),
        container_name=gen_container_name("nlp-translate-local", containerid),
        api_version="auto",
        # Useful for debugging
        auto_remove="success",
        privileged=True,
        execution_timeout=timedelta(seconds=172800),
        command=docker_command,
        environment={"DOWNLOAD_DATA": download_data, "UPLOAD_DATA": upload_data},
        docker_url=get_docker_url(),
        network_mode="container:hans-ml-backend-assetdb-temp",
    )
