#!/usr/bin/env python
"""
Docker operators for media.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from airflow import DAG
from airflow.operators.docker_operator import DockerOperator


def op_docker_media_converter_audio(
    dag_id,
    task_id_suffix,
    containerid,
    download_data,
    download_data_keys,
    download_data_filename_keys,
    upload_data,
    upload_data_key,
):
    """
    Provides DockerOperator Media Converter Audio.
    Converts video or podcast file to wav and saves it in assetdb-temp.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str download_data: XCOM Data which contains download urls.
    :param str download_data_keys: XCOM Data keys used to determine the download url.
    :param str download_data_filename_keys: XCOM Data keys used to determine the filename.
    :param str upload_data: XCOM Data which contains upload url.
    :param str upload_data_key: XCOM Data key to used to determine the upload url.

    :return: DockerOperator Media Converter Audio
    """
    from modules.operators.docker_helper import get_docker_url, gen_container_name, gen_image_name
    from datetime import timedelta
    from modules.operators.xcom import gen_task_id

    return DockerOperator(
        task_id=gen_task_id(dag_id, "op_docker_media_converter_audio", task_id_suffix),
        image=gen_image_name("media-converter-audio"),
        container_name=gen_container_name("media-converter-audio", containerid),
        api_version="auto",
        # Useful for debugging
        auto_remove="success",
        privileged=True,
        execution_timeout=timedelta(seconds=86400),
        command="./convert.sh -d "
        + download_data_keys
        + " -f "
        + download_data_filename_keys
        + " -u "
        + upload_data_key
        + " -v",
        environment={"DOWNLOAD_DATA": download_data, "UPLOAD_DATA": upload_data},
        docker_url=get_docker_url(),
        network_mode="container:hans-ml-backend-assetdb-temp",
    )


def op_docker_media_converter_video(
    dag_id, task_id_suffix, containerid, download_data, download_data_key, urn_data, urn_data_key, config={}
):
    """
    Provides DockerOperator Media Converter Video.
    Converts video file to MPEG-DASH and saves all chunks and mpd file in assetdb-temp.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str download_data: XCOM Data which contains download urls.
    :param str download_data_key: XCOM Data key used to determine the download url.
    :param str urn_data: XCOM Data which contains urn for upload.
    :param str urn_data_key: XCOM Data key for the urn, used to determine the uuid of the urn.
    :param str config: Configuration for used openai with keys: num_cpus, ram_limit_docker, use_gpu,
                       resolution 'full-hd' or 'hd', default: 'hd'.

    :return: DockerOperator Media Converter Video
    """
    import json
    from datetime import timedelta
    from docker.types import DeviceRequest
    from modules.operators.docker_helper import get_docker_url, gen_container_name, gen_image_name
    from modules.operators.xcom import gen_task_id
    from modules.operators.connections import get_assetdb_temp_config

    # configure number of cpus/threads, large-v2 model needs ~10GB (V)RAM
    num_cpus = 4.0
    ram_limit_docker = "10g"
    use_gpu = False
    resolution = "hd"
    preview = False

    if "num_cpus" in config:
        num_cpus = config["num_cpus"]
    if "ram_limit_docker" in config:
        ram_limit_docker = config["ram_limit_docker"]
    if "use_gpu" in config:
        use_gpu = config["use_gpu"]
    if "resolution" in config:
        resolution = config["resolution"].lower()
    if "preview" in config:
        preview = config["preview"]

    converter_cmd = "./convert.sh -d "
    converter_cmd += download_data_key
    converter_cmd += " -p "
    converter_cmd += urn_data_key
    converter_cmd += " -r "
    converter_cmd += resolution
    converter_cmd += " -t "
    converter_cmd += str(int(num_cpus))
    converter_cmd += " -u"
    converter_cmd += " -v"
    if preview is True:
        converter_cmd += " -s"

    if use_gpu is True:
        return DockerOperator(
            task_id=gen_task_id(dag_id, "op_docker_media_converter_video_gpu", task_id_suffix),
            image=gen_image_name("media-converter-video-gpu"),
            container_name=gen_container_name("media-converter-video-gpu", containerid),
            api_version="auto",
            # Disable auto_remove here while debugging
            auto_remove="success",
            privileged=True,
            execution_timeout=timedelta(seconds=86400),
            command=converter_cmd,
            environment={
                "URN_DATA": urn_data,
                "DOWNLOAD_DATA": download_data,
                "ASSETDB_TEMP_CONFIG": json.dumps(get_assetdb_temp_config()),
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
        task_id=gen_task_id(dag_id, "op_docker_media_converter_video", task_id_suffix),
        image=gen_image_name("media-converter-video"),
        container_name=gen_container_name("media-converter-video", containerid),
        api_version="auto",
        # Disable auto_remove here while debugging
        auto_remove="success",
        privileged=True,
        execution_timeout=timedelta(seconds=86400),
        # Without cpu parameter to use all available cpu's => ffmpeg auto mode
        command=converter_cmd,
        environment={
            "URN_DATA": urn_data,
            "DOWNLOAD_DATA": download_data,
            "ASSETDB_TEMP_CONFIG": json.dumps(get_assetdb_temp_config()),
        },
        docker_url=get_docker_url(),
        network_mode="container:hans-ml-backend-assetdb-temp",
    )


def op_docker_media_thumbnail_image(
    dag_id,
    task_id_suffix,
    containerid,
    download_data,
    download_data_key,
    download_data_filename_key,
    upload_data,
    upload_data_key,
    resolution="hd",
):
    """
    Provides DockerOperator Media Thumbnail Image.
    Creates a thumbnail image of a video file and saves it in assetdb-temp.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str download_data: XCOM Data which contains download urls.
    :param str download_data_key: XCOM Data key used to determine the download url.
    :param str download_data_filename_key: XCOM Data key used to determine the filename.
    :param str upload_data: XCOM Data which contains upload url.
    :param str upload_data_key: XCOM Data key to used to determine the upload url.
    :param str resolution: Resolution of the thumbnail, 'full-hd' or 'hd', default: 'hd'.

    :return: DockerOperator Media Thumbnail Image
    """
    import json
    from modules.operators.docker_helper import get_docker_url, gen_container_name, gen_image_name
    from modules.operators.xcom import gen_task_id
    from modules.operators.connections import get_assetdb_temp_config

    return DockerOperator(
        task_id=gen_task_id(dag_id, "op_docker_media_thumbnail_image", task_id_suffix),
        image=gen_image_name("media-thumbnail-image"),
        container_name=gen_container_name("media-thumbnail-image", containerid),
        api_version="auto",
        # Useful for debugging
        auto_remove="success",
        privileged=True,
        command="./convert.sh -d "
        + download_data_key
        + " -f "
        + download_data_filename_key
        + " -r "
        + resolution
        + " -u "
        + upload_data_key
        + " -v",
        environment={
            "DOWNLOAD_DATA": download_data,
            "UPLOAD_DATA": upload_data,
            "ASSETDB_TEMP_CONFIG": json.dumps(get_assetdb_temp_config()),
        },
        docker_url=get_docker_url(),
        network_mode="container:hans-ml-backend-assetdb-temp",
    )
