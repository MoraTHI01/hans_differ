#!/usr/bin/env python
"""
Docker operators for ASR.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from airflow import DAG
from airflow.operators.docker_operator import DockerOperator


def op_docker_asr_engine_remote_mod9(
    dag_id,
    task_id_suffix,
    containerid,
    download_data,
    download_data_key,
    asr_locale_data,
    asr_locale_key,
    upload_data_asr_result_de,
    upload_data_key_asr_result_de,
    upload_data_asr_result_en,
    upload_data_key_asr_result_en,
    upload_data_transcript_de,
    upload_data_key_transcript_de,
    upload_data_transcript_en,
    upload_data_key_transcript_en,
    upload_data_subtitle_de,
    upload_data_key_subtitle_de,
    upload_data_subtitle_en,
    upload_data_key_subtitle_en,
    config={},
):
    """
    Provides DockerOperator for ASR using mod9 engine on a remote server.
    Creates a transcript from raw audio and saves it as asr_result.json in assetdb-temp.
    Creates a subtitles VTT from raw audio and saves it as subtitle.vtt.txt in assetdb-temp.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id, values: asr_result, transcript
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str download_data: XCOM Data which contains download urls.
    :param str download_data_key: XCOM Data key to used to determine the download url.
    :param str asr_locale_data: XCOM Data which contains the asr locale.
    :param str asr_locale_key: XCOM Data key to used to determine the asr locale.

    :param str upload_data_asr_result_de: XCOM Data which contains upload url for asr_result_de file.
    :param str upload_data_key_asr_result_de: XCOM Data key to used to determine the upload url.

    :param str upload_data_asr_result_en: XCOM Data which contains upload url for asr_result_en file.
    :param str upload_data_key_asr_result_en: XCOM Data key to used to determine the upload url.

    :param str upload_data_transcript_de: XCOM Data which contains upload url for transcript_de file.
    :param str upload_data_key_transcript_de: XCOM Data key to used to determine the upload url.

    :param str upload_data_transcript_en: XCOM Data which contains upload url for transcript_en file.
    :param str upload_data_key_transcript_en: XCOM Data key to used to determine the upload url.

    :param str upload_data_subtitle_de: XCOM Data which contains upload url for subtitle_de file.
    :param str upload_data_key_subtitle_de: XCOM Data key to used to determine the upload url.

    :param str upload_data_subtitle_en: XCOM Data which contains upload url for subtitle_en file.
    :param str upload_data_key_subtitle_en: XCOM Data key to used to determine the upload url.

    :param str config: Configuration for used mod9

    :return: DockerOperator Remote ASR mod9 engine
    """
    from datetime import timedelta
    from modules.operators.docker_helper import get_docker_url, gen_container_name, gen_image_name
    from modules.operators.connections import get_connection_config
    from modules.operators.xcom import gen_task_id

    conn_config = get_connection_config("asr_engine_remote_mod9")
    remote_host = conn_config["host"]
    remote_port = str(conn_config["port"])

    docker_command = "./recognize.sh -d " + download_data_key + " -l " + asr_locale_key
    docker_command = docker_command + " -u " + upload_data_key_asr_result_de
    docker_command = docker_command + " -t " + upload_data_key_transcript_de
    docker_command = docker_command + " -s " + upload_data_key_subtitle_de
    docker_command = docker_command + " -x " + upload_data_key_asr_result_en
    docker_command = docker_command + " -y " + upload_data_key_transcript_en
    docker_command = docker_command + " -z " + upload_data_key_subtitle_en
    docker_command = docker_command + " -r " + remote_host
    docker_command = docker_command + " -p " + remote_port

    return DockerOperator(
        # For asr_engine_remote we use always the same task_id_suffix:
        # asr_result for the raw asr_result
        # transcript for the transcript with e.g. punctuation
        task_id=gen_task_id(dag_id, "op_docker_asr_engine_remote", task_id_suffix),
        image=gen_image_name("asr-engine-remote-mod9"),
        container_name=gen_container_name("asr-engine-remote-mod9", containerid),
        api_version="auto",
        # Useful for debugging
        auto_remove="success",
        privileged=True,
        execution_timeout=timedelta(seconds=172800),
        command=docker_command,
        environment={
            "DOWNLOAD_DATA": download_data,
            "UPLOAD_DATA_ASR_RESULT_DE": upload_data_asr_result_de,
            "UPLOAD_DATA_ASR_RESULT_EN": upload_data_asr_result_en,
            "UPLOAD_DATA_TRANSCRIPT_DE": upload_data_transcript_de,
            "UPLOAD_DATA_TRANSCRIPT_EN": upload_data_transcript_en,
            "UPLOAD_DATA_SUBTITLE_DE": upload_data_subtitle_de,
            "UPLOAD_DATA_SUBTITLE_EN": upload_data_subtitle_en,
            "ASR_LOCALE": asr_locale_data,
        },
        docker_url=get_docker_url(),
        network_mode="container:hans-ml-backend-assetdb-temp",
    )


def op_docker_asr_engine_remote_whisper_s2t(
    dag_id,
    task_id_suffix,
    containerid,
    download_data,
    download_data_key,
    asr_locale_data,
    asr_locale_key,
    upload_data_asr_result_de,
    upload_data_key_asr_result_de,
    upload_data_asr_result_en,
    upload_data_key_asr_result_en,
    upload_data_transcript_de,
    upload_data_key_transcript_de,
    upload_data_transcript_en,
    upload_data_key_transcript_en,
    upload_data_subtitle_de,
    upload_data_key_subtitle_de,
    upload_data_subtitle_en,
    upload_data_key_subtitle_en,
    config={},
):
    """
    Provides DockerOperator for ASR using whisper-s2t end-to-end ASR on remote system.
    Creates a transcript from raw audio and saves it as asr_result.json in assetdb-temp.
    Creates a subtitles VTT from raw audio and saves it as subtitle.vtt.txt in assetdb-temp.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id, values: asr_result, transcript
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str download_data: XCOM Data which contains download urls.
    :param str download_data_key: XCOM Data key to used to determine the download url.
    :param str asr_locale_data: XCOM Data which contains the asr locale.
    :param str asr_locale_key: XCOM Data key to used to determine the asr locale.

    :param str upload_data_asr_result_de: XCOM Data which contains upload url for asr_result_de file.
    :param str upload_data_key_asr_result_de: XCOM Data key to used to determine the upload url.

    :param str upload_data_asr_result_en: XCOM Data which contains upload url for asr_result_en file.
    :param str upload_data_key_asr_result_en: XCOM Data key to used to determine the upload url.

    :param str upload_data_transcript_de: XCOM Data which contains upload url for transcript_de file.
    :param str upload_data_key_transcript_de: XCOM Data key to used to determine the upload url.

    :param str upload_data_transcript_en: XCOM Data which contains upload url for transcript_en file.
    :param str upload_data_key_transcript_en: XCOM Data key to used to determine the upload url.

    :param str upload_data_subtitle_de: XCOM Data which contains upload url for subtitle_de file.
    :param str upload_data_key_subtitle_de: XCOM Data key to used to determine the upload url.

    :param str upload_data_subtitle_en: XCOM Data which contains upload url for subtitle_en file.
    :param str upload_data_key_subtitle_en: XCOM Data key to used to determine the upload url.

    :param str config: Configuration for used whisper-s2t with keys:
                       use_orchestrator, default: False
                       batch_size 8, 16, 32, 64, default: 8
                       asr_model 'large-v2' or 'large-v3', default: 'large-v3'.

    :return: DockerOperator Remote ASR whisper-s2t engine
    """
    from datetime import timedelta
    from modules.operators.docker_helper import get_docker_url, gen_container_name, gen_image_name
    from modules.operators.connections import get_connection_config
    from modules.operators.xcom import gen_task_id

    use_orchestrator = False
    asr_model = "large-v3"
    # configure batch size depending on VRAM,
    # RTX 2080 Ti set batch size to 8, A100 40GB set it to 48
    batch_size = 8
    if "asr_model" in config:
        asr_model = config["asr_model"]
    if "batch_size" in config:
        batch_size = config["batch_size"]
    if "use_orchestrator" in config:
        use_orchestrator = config["use_orchestrator"]

    conn_config = get_connection_config("transcription_remote")
    remote_host = conn_config["host"]
    remote_port = str(conn_config["port"])
    remote_connection = remote_host + ":" + remote_port
    if use_orchestrator is True:
        remote_connection = remote_connection + "/asr_service"
    docker_command = "./recognize.sh -m " + asr_model
    docker_command = docker_command + " -b " + str(int(batch_size))
    docker_command = docker_command + " -d " + download_data_key + " -l " + asr_locale_key
    docker_command = docker_command + " -u " + upload_data_key_asr_result_de
    docker_command = docker_command + " -t " + upload_data_key_transcript_de
    docker_command = docker_command + " -s " + upload_data_key_subtitle_de
    docker_command = docker_command + " -x " + upload_data_key_asr_result_en
    docker_command = docker_command + " -y " + upload_data_key_transcript_en
    docker_command = docker_command + " -z " + upload_data_key_subtitle_en
    docker_command = docker_command + " -c " + remote_connection

    return DockerOperator(
        # For asr_engine_remote we use always the same task_id_suffix:
        # asr_result for the raw asr_result
        # transcript for the transcript with e.g. punctuation
        task_id=gen_task_id(dag_id, "op_docker_asr_engine_remote", task_id_suffix),
        image=gen_image_name("asr-engine-remote-whisper-s2t"),
        container_name=gen_container_name("asr-engine-remote-whisper-s2t", containerid),
        api_version="auto",
        # Useful for debugging
        auto_remove="success",
        privileged=True,
        execution_timeout=timedelta(seconds=172800),
        command=docker_command,
        environment={
            "DOWNLOAD_DATA": download_data,
            "UPLOAD_DATA_ASR_RESULT_DE": upload_data_asr_result_de,
            "UPLOAD_DATA_ASR_RESULT_EN": upload_data_asr_result_en,
            "UPLOAD_DATA_TRANSCRIPT_DE": upload_data_transcript_de,
            "UPLOAD_DATA_TRANSCRIPT_EN": upload_data_transcript_en,
            "UPLOAD_DATA_SUBTITLE_DE": upload_data_subtitle_de,
            "UPLOAD_DATA_SUBTITLE_EN": upload_data_subtitle_en,
            "ASR_LOCALE": asr_locale_data,
        },
        docker_url=get_docker_url(),
        network_mode="container:hans-ml-backend-assetdb-temp",
    )


def op_docker_asr_engine_local_openai(
    dag_id,
    task_id_suffix,
    containerid,
    download_data,
    download_data_key,
    asr_locale_data,
    asr_locale_key,
    upload_data_asr_result_de,
    upload_data_key_asr_result_de,
    upload_data_asr_result_en,
    upload_data_key_asr_result_en,
    upload_data_transcript_de,
    upload_data_key_transcript_de,
    upload_data_transcript_en,
    upload_data_key_transcript_en,
    upload_data_subtitle_de,
    upload_data_key_subtitle_de,
    upload_data_subtitle_en,
    upload_data_key_subtitle_en,
    config={},
):
    """
    Provides DockerOperator for ASR using OpenAI whisper end-to-end ASR on local system.
    Creates a transcript from raw audio and saves it as asr_result.json in assetdb-temp.
    Creates a subtitles VTT from raw audio and saves it as subtitle.vtt.txt in assetdb-temp.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id, values: asr_result, transcript
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str download_data: XCOM Data which contains download urls.
    :param str download_data_key: XCOM Data key to used to determine the download url.
    :param str asr_locale_data: XCOM Data which contains the asr locale.
    :param str asr_locale_key: XCOM Data key to used to determine the asr locale.

    :param str upload_data_asr_result_de: XCOM Data which contains upload url for asr_result_de file.
    :param str upload_data_key_asr_result_de: XCOM Data key to used to determine the upload url.

    :param str upload_data_asr_result_en: XCOM Data which contains upload url for asr_result_en file.
    :param str upload_data_key_asr_result_en: XCOM Data key to used to determine the upload url.

    :param str upload_data_transcript_de: XCOM Data which contains upload url for transcript_de file.
    :param str upload_data_key_transcript_de: XCOM Data key to used to determine the upload url.

    :param str upload_data_transcript_en: XCOM Data which contains upload url for transcript_en file.
    :param str upload_data_key_transcript_en: XCOM Data key to used to determine the upload url.

    :param str upload_data_subtitle_de: XCOM Data which contains upload url for subtitle_de file.
    :param str upload_data_key_subtitle_de: XCOM Data key to used to determine the upload url.

    :param str upload_data_subtitle_en: XCOM Data which contains upload url for subtitle_en file.
    :param str upload_data_key_subtitle_en: XCOM Data key to used to determine the upload url.

    :param str config: Configuration for used openai with keys: num_cpus, ram_limit_docker, use_gpu
                       asr_model 'large-v2' or 'medium', default: 'large-v2'.

    :return: DockerOperator Remote ASR mod9 engine
    """
    from datetime import timedelta
    from docker.types import DeviceRequest
    from modules.operators.docker_helper import get_docker_url, gen_container_name, gen_image_name
    from modules.operators.xcom import gen_task_id

    # configure number of cpus/threads, large-v2 model needs ~10GB (V)RAM
    num_cpus = 4.0
    ram_limit_docker = "10g"
    use_gpu = False
    asr_model = "large-v2"
    if "num_cpus" in config:
        num_cpus = config["num_cpus"]
    if "ram_limit_docker" in config:
        ram_limit_docker = config["ram_limit_docker"]
    if "use_gpu" in config:
        use_gpu = config["use_gpu"]
    if "asr_model" in config:
        asr_model = config["asr_model"]

    docker_command = "./recognize.sh -c " + str(int(num_cpus)) + " -m " + asr_model
    docker_command = docker_command + " -d " + download_data_key + " -l " + asr_locale_key
    docker_command = docker_command + " -u " + upload_data_key_asr_result_de
    docker_command = docker_command + " -t " + upload_data_key_transcript_de
    docker_command = docker_command + " -s " + upload_data_key_subtitle_de
    docker_command = docker_command + " -x " + upload_data_key_asr_result_en
    docker_command = docker_command + " -y " + upload_data_key_transcript_en
    docker_command = docker_command + " -z " + upload_data_key_subtitle_en

    if use_gpu is True:
        docker_command = docker_command + " -g"
        return DockerOperator(
            # For asr_engine_remote we use always the same task_id_suffix:
            # asr_result for the raw asr_result
            # transcript for the transcript with e.g. punctuation
            task_id=gen_task_id(dag_id, "op_docker_asr_engine_local", task_id_suffix),
            image=gen_image_name("asr-engine-local-openai"),
            container_name=gen_container_name("asr-engine-local-openai", containerid),
            api_version="auto",
            # Useful for debugging
            auto_remove="success",
            privileged=True,
            execution_timeout=timedelta(seconds=172800),
            command=docker_command,
            environment={
                "DOWNLOAD_DATA": download_data,
                "UPLOAD_DATA_ASR_RESULT_DE": upload_data_asr_result_de,
                "UPLOAD_DATA_ASR_RESULT_EN": upload_data_asr_result_en,
                "UPLOAD_DATA_TRANSCRIPT_DE": upload_data_transcript_de,
                "UPLOAD_DATA_TRANSCRIPT_EN": upload_data_transcript_en,
                "UPLOAD_DATA_SUBTITLE_DE": upload_data_subtitle_de,
                "UPLOAD_DATA_SUBTITLE_EN": upload_data_subtitle_en,
                "ASR_LOCALE": asr_locale_data,
            },
            docker_url=get_docker_url(),
            network_mode="container:hans-ml-backend-assetdb-temp",
            cpus=num_cpus,
            mem_limit=ram_limit_docker,
            # count 1 means one gpu, -1 means all gpu's
            # or use specific list of device_ids=["0,1,2,3,4,5,6,7"], device_ids=[gen_next_gpu_id()]
            # https://stackoverflow.com/questions/71429711/how-to-run-a-docker-container-with-specific-gpus-using-docker-sdk-for-python
            device_requests=[DeviceRequest(count=1, capabilities=[["gpu"]])],
        )
    return DockerOperator(
        # For asr_engine_remote we use always the same task_id_suffix:
        # asr_result for the raw asr_result
        # transcript for the transcript with e.g. punctuation
        task_id=gen_task_id(dag_id, "op_docker_asr_engine_local", task_id_suffix),
        image=gen_image_name("asr-engine-local-openai"),
        container_name=gen_container_name("asr-engine-local-openai", containerid),
        api_version="auto",
        # Useful for debugging
        auto_remove="success",
        privileged=True,
        execution_timeout=timedelta(seconds=172800),
        command=docker_command,
        environment={
            "DOWNLOAD_DATA": download_data,
            "UPLOAD_DATA_ASR_RESULT_DE": upload_data_asr_result_de,
            "UPLOAD_DATA_ASR_RESULT_EN": upload_data_asr_result_en,
            "UPLOAD_DATA_TRANSCRIPT_DE": upload_data_transcript_de,
            "UPLOAD_DATA_TRANSCRIPT_EN": upload_data_transcript_en,
            "UPLOAD_DATA_SUBTITLE_DE": upload_data_subtitle_de,
            "UPLOAD_DATA_SUBTITLE_EN": upload_data_subtitle_en,
            "ASR_LOCALE": asr_locale_data,
        },
        docker_url=get_docker_url(),
        network_mode="container:hans-ml-backend-assetdb-temp",
        cpus=num_cpus,
        mem_limit=ram_limit_docker,
    )


def op_docker_asr_engine_local_whisper_s2t(
    dag_id,
    task_id_suffix,
    containerid,
    download_data,
    download_data_key,
    asr_locale_data,
    asr_locale_key,
    upload_data_asr_result_de,
    upload_data_key_asr_result_de,
    upload_data_asr_result_en,
    upload_data_key_asr_result_en,
    upload_data_transcript_de,
    upload_data_key_transcript_de,
    upload_data_transcript_en,
    upload_data_key_transcript_en,
    upload_data_subtitle_de,
    upload_data_key_subtitle_de,
    upload_data_subtitle_en,
    upload_data_key_subtitle_en,
    config={},
):
    """
    Provides DockerOperator for ASR using whisper-s2t end-to-end ASR on local system.
    Creates a transcript from raw audio and saves it as asr_result.json in assetdb-temp.
    Creates a subtitles VTT from raw audio and saves it as subtitle.vtt.txt in assetdb-temp.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id, values: asr_result, transcript
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str download_data: XCOM Data which contains download urls.
    :param str download_data_key: XCOM Data key to used to determine the download url.
    :param str asr_locale_data: XCOM Data which contains the asr locale.
    :param str asr_locale_key: XCOM Data key to used to determine the asr locale.

    :param str upload_data_asr_result_de: XCOM Data which contains upload url for asr_result_de file.
    :param str upload_data_key_asr_result_de: XCOM Data key to used to determine the upload url.

    :param str upload_data_asr_result_en: XCOM Data which contains upload url for asr_result_en file.
    :param str upload_data_key_asr_result_en: XCOM Data key to used to determine the upload url.

    :param str upload_data_transcript_de: XCOM Data which contains upload url for transcript_de file.
    :param str upload_data_key_transcript_de: XCOM Data key to used to determine the upload url.

    :param str upload_data_transcript_en: XCOM Data which contains upload url for transcript_en file.
    :param str upload_data_key_transcript_en: XCOM Data key to used to determine the upload url.

    :param str upload_data_subtitle_de: XCOM Data which contains upload url for subtitle_de file.
    :param str upload_data_key_subtitle_de: XCOM Data key to used to determine the upload url.

    :param str upload_data_subtitle_en: XCOM Data which contains upload url for subtitle_en file.
    :param str upload_data_key_subtitle_en: XCOM Data key to used to determine the upload url.

    :param str config: Configuration for used whisper-s2t with keys: num_cpus, ram_limit_docker, use_gpu
                       batch_size 8, 16, 32, 64, default: 8
                       asr_model 'large-v2' or 'large-v3', default: 'large-v3'.

    :return: DockerOperator Remote ASR mod9 engine
    """
    from datetime import timedelta
    from docker.types import DeviceRequest
    from modules.operators.docker_helper import get_docker_url, gen_container_name, gen_image_name
    from modules.operators.xcom import gen_task_id

    # configure number of cpus/threads, large-v3 model needs ~10GB (V)RAM
    num_cpus = 4.0
    ram_limit_docker = "10g"
    use_gpu = False
    asr_model = "large-v3"
    # configure batch size depending on VRAM,
    # RTX 2080 Ti set batch size to 8, A100 40GB set it to 48
    batch_size = 8
    if "num_cpus" in config:
        num_cpus = config["num_cpus"]
    if "ram_limit_docker" in config:
        ram_limit_docker = config["ram_limit_docker"]
    if "use_gpu" in config:
        use_gpu = config["use_gpu"]
    if "asr_model" in config:
        asr_model = config["asr_model"]
    if "batch_size" in config:
        batch_size = config["batch_size"]

    docker_command = "./recognize.sh -c " + str(int(num_cpus)) + " -m " + asr_model
    docker_command = docker_command + " -b " + str(int(batch_size))
    docker_command = docker_command + " -d " + download_data_key + " -l " + asr_locale_key
    docker_command = docker_command + " -u " + upload_data_key_asr_result_de
    docker_command = docker_command + " -t " + upload_data_key_transcript_de
    docker_command = docker_command + " -s " + upload_data_key_subtitle_de
    docker_command = docker_command + " -x " + upload_data_key_asr_result_en
    docker_command = docker_command + " -y " + upload_data_key_transcript_en
    docker_command = docker_command + " -z " + upload_data_key_subtitle_en

    if use_gpu is True:
        docker_command = docker_command + " -g"
        return DockerOperator(
            # For asr_engine_remote we use always the same task_id_suffix:
            # asr_result for the raw asr_result
            # transcript for the transcript with e.g. punctuation
            task_id=gen_task_id(dag_id, "op_docker_asr_engine_local", task_id_suffix),
            image=gen_image_name("asr-engine-local-whisper-s2t"),
            container_name=gen_container_name("asr-engine-local-whisper-s2t", containerid),
            api_version="auto",
            # Useful for debugging
            auto_remove="success",
            privileged=True,
            execution_timeout=timedelta(seconds=172800),
            command=docker_command,
            environment={
                "DOWNLOAD_DATA": download_data,
                "UPLOAD_DATA_ASR_RESULT_DE": upload_data_asr_result_de,
                "UPLOAD_DATA_ASR_RESULT_EN": upload_data_asr_result_en,
                "UPLOAD_DATA_TRANSCRIPT_DE": upload_data_transcript_de,
                "UPLOAD_DATA_TRANSCRIPT_EN": upload_data_transcript_en,
                "UPLOAD_DATA_SUBTITLE_DE": upload_data_subtitle_de,
                "UPLOAD_DATA_SUBTITLE_EN": upload_data_subtitle_en,
                "ASR_LOCALE": asr_locale_data,
            },
            docker_url=get_docker_url(),
            network_mode="container:hans-ml-backend-assetdb-temp",
            cpus=num_cpus,
            mem_limit=ram_limit_docker,
            # count 1 means one gpu, -1 means all gpu's
            # or use specific list of device_ids=["0,1,2,3,4,5,6,7"], device_ids=[gen_next_gpu_id()]
            # https://stackoverflow.com/questions/71429711/how-to-run-a-docker-container-with-specific-gpus-using-docker-sdk-for-python
            device_requests=[DeviceRequest(count=1, capabilities=[["gpu"]])],
        )
    return DockerOperator(
        # For asr_engine_remote we use always the same task_id_suffix:
        # asr_result for the raw asr_result
        # transcript for the transcript with e.g. punctuation
        task_id=gen_task_id(dag_id, "op_docker_asr_engine_local", task_id_suffix),
        image=gen_image_name("asr-engine-local-whisper-s2t"),
        container_name=gen_container_name("asr-engine-local-whisper-s2t", containerid),
        api_version="auto",
        # Useful for debugging
        auto_remove="success",
        privileged=True,
        execution_timeout=timedelta(seconds=172800),
        command=docker_command,
        environment={
            "DOWNLOAD_DATA": download_data,
            "UPLOAD_DATA_ASR_RESULT_DE": upload_data_asr_result_de,
            "UPLOAD_DATA_ASR_RESULT_EN": upload_data_asr_result_en,
            "UPLOAD_DATA_TRANSCRIPT_DE": upload_data_transcript_de,
            "UPLOAD_DATA_TRANSCRIPT_EN": upload_data_transcript_en,
            "UPLOAD_DATA_SUBTITLE_DE": upload_data_subtitle_de,
            "UPLOAD_DATA_SUBTITLE_EN": upload_data_subtitle_en,
            "ASR_LOCALE": asr_locale_data,
        },
        docker_url=get_docker_url(),
        network_mode="container:hans-ml-backend-assetdb-temp",
        cpus=num_cpus,
        mem_limit=ram_limit_docker,
    )
