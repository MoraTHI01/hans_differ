#!/usr/bin/env python
"""
Docker operators for packaging.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.python import PythonVirtualenvOperator


def op_docker_create_channel_package(
    dag_id, task_id_suffix, containerid, channel_package_uuid, channel_package_url, channel_data
):
    """
    Provides DockerOperator to download archive data and create a channel for HAnS.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id, e.g. transcript
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str channel_package_uuid: UUID of the channel package
    :param str channel_package_url: Url to upload the channel package
    :param str channel_data: DAG input json data from webfrontend

    :return: DockerOperator to download archive data and create a channel for HAnS.
    """
    import json
    from modules.operators.docker_helper import get_docker_url
    from modules.operators.xcom import gen_task_id
    from modules.operators.connections import get_assetdb_temp_config

    docker_command = './create_channel_package.sh -p "' + channel_package_uuid + '" -v'

    return DockerOperator(
        task_id=gen_task_id(dag_id, "op_docker_create_channel_package", task_id_suffix),
        image="airflow_docker_create-channel-package",
        container_name="task___create-channel-package_" + containerid,
        api_version="auto",
        # auto remove disabled to have more ways to fetch the channel package
        auto_remove="never",
        privileged=True,
        command=docker_command,
        environment={
            "UPLOAD_URL": channel_package_url,
            "CHANNEL_DATA": channel_data,
            "ASSETDB_TEMP_CONFIG": json.dumps(get_assetdb_temp_config()),
        },
        docker_url=get_docker_url(),
        network_mode="container:hans-ml-backend-assetdb-temp",
    )
