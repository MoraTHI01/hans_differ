from typing import Optional

from airflow.operators.docker_operator import DockerOperator


def op_docker_topic_segmentation(
    dag_id,
    task_id_suffix,
    containerid,
    download_data,
    download_data_key,
    upload_data_topic_result,
    upload_data_key_topic_result,
    config: Optional[dict] = None,
) -> DockerOperator:
    """
    Provides DockerOperator for topic segmentation using an unsupervised, BERT-based algorithm.
    Creates a topic result file from the vtt file and saves it as topic_result.json in assetdb-temp.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id, values: asr_result, transcript
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str download_data: XCOM Data which contains download urls.
    :param str download_data_key: XCOM Data key to used to determine the download url.

    :param str upload_data_topic_result: XCOM Data which contains upload url for topic result file.
    :param str upload_data_key_topic_result: XCOM Data key to used to determine the upload url.

    :param str config: Configuration for used openai with keys: num_cpus, ram_limit_docker, use_gpu
                       asr_model 'large-v2' or 'medium', default: 'large-v2'.

    :return: DockerOperator for performing topic segmentation
    """
    from datetime import timedelta
    from docker.types import DeviceRequest
    from modules.operators.docker_helper import get_docker_url, gen_container_name, gen_image_name
    from modules.operators.xcom import gen_task_id

    # configure number of cpus/threads, large-v2 model needs ~10GB (V)RAM
    config = dict() if config is None else config
    num_cpus = config.get("num_cpus", 4)
    ram_limit_docker = config.get("ram_limit_docker", "10g")
    use_gpu = config.get("use_gpu", False)
    embedding_model = config.get("embedding_model", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

    docker_command = (
        f"./segment.sh -m {embedding_model} -d {download_data_key}"
        f" -u {upload_data_key_topic_result} {'-g' if use_gpu else ''}"
    )

    device_requests = [DeviceRequest(count=1, capabilities=[["gpu"]])] if use_gpu else None

    return DockerOperator(
        task_id=gen_task_id(dag_id, "op_docker_topic_segmentation", task_id_suffix),
        image=gen_image_name("topic-segmentation"),
        container_name=gen_container_name("topic-segmentation", containerid),
        api_version="auto",
        # Useful for debugging
        auto_remove="success",
        privileged=True,
        execution_timeout=timedelta(seconds=172800),
        command=docker_command,
        environment={"DOWNLOAD_DATA": download_data, "UPLOAD_DATA": upload_data_topic_result},
        docker_url=get_docker_url(),
        network_mode="container:hans-ml-backend-assetdb-temp",
        cpus=num_cpus,
        mem_limit=ram_limit_docker,
        # count 1 means one gpu, -1 means all gpu's
        # or use specific list of device_ids=["0,1,2,3,4,5,6,7"], device_ids=[gen_next_gpu_id()]
        # https://stackoverflow.com/questions/71429711/how-to-run-a-docker-container-with-specific-gpus-using-docker-sdk-for-python
        device_requests=device_requests,
    )
