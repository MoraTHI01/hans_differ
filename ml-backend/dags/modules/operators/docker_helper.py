#!/usr/bin/env python
"""
Docker operators helpers.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


def gen_image_name(folder_name):
    """
    Provides a the image name for the docker image using the folder name below 'docker_jobs' folder

    :return: str image_name
    """
    return "airflow_docker_" + folder_name


def gen_container_name(image_name, container_id):
    """
    Provides a unique container name

    :return: str container_name
    """
    import uuid

    uid = uuid.uuid4()
    return "task___" + image_name + "_" + container_id + "_" + str(uid)


def get_docker_url():
    """
    Provides DockerOperator docker socket url depending on platform

    :return: str docker_url
    """
    import os

    docker_url_custom = "unix://var/run/docker.sock"
    current_platform = os.environ.get("HANS_HOST_PLATFORM", default="Linux").lower()
    if current_platform == "darwin" or current_platform == "wsl":
        # https://stackoverflow.com/questions/61186983/airflow-dockeroperator-connect-sock-connectself-unix-socket-filenotfounderror
        # https://onedevblog.com/how-to-fix-a-permission-denied-when-using-dockeroperator-in-airflow/
        docker_url_custom = "tcp://airflow-docker-proxy:2375"

    return docker_url_custom


def gen_next_gpu_id():
    """
    Dynamic increment gpu id in range 0 - 7 assuming system has 8 cards
    """
    # import subprocess
    from airflow.models import Variable

    previous_gpu_id = Variable.get("curr_gpu_id", default_var="0")
    if previous_gpu_id == "7":
        next_gpu_id = "0"
    else:
        next_gpu_id = str(int(previous_gpu_id) + 1)

    Variable.set("curr_gpu_id", next_gpu_id)
    return next_gpu_id
    # Alternative check free card with nvidia-smi pmon, didn't work:
    # for i in range(0,7):
    #    output = subprocess.check_output(args=f"nvidia-smi pmon -i {i} -s u -c 1 | tail -n 1", shell=True)
    #    filtered_output = output.decode(encoding='utf-8').replace(" ","").replace("-","")
    #    if filtered_output == str(i):
    #        return str(i)
    # return "0"
