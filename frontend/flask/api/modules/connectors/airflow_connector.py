#!/usr/bin/env python
"""
Connector to ml-backend airflow.
See https://github.com/apache/airflow-client-python
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import airflow_client.client as airflow_api
from airflow_client.client.api import dag_run_api, dag_api
from airflow_client.client.model.dag_run import DAGRun
from airflow_client.client.model.list_dag_runs_form import ListDagRunsForm
from urllib3.exceptions import RequestError, NewConnectionError

from api.modules.connectors.connector import Connector


class AirflowConnector(Connector):
    """
    Handle airflow connections.
    See https://github.com/apache/airflow-client-python
    """

    def __init__(self, server, port, postfix, user, password):
        """
        Initialization

        :param str server: airflow server name
        :param str port: airflow server port address
        :param str postfix: airflow server postfix,
          e.g. /hans-ml-backend if behind reverse proxy, default: /
        :param str user: airflow user
        :param str password: airflow password
        """
        self.client = None
        self.server = server
        self.port = port
        self.postfix = postfix
        self.user = user
        self.password = password

        # needed as airflow does not accept at the end of postfix /
        # for nginx rev proxy setup
        if self.postfix[-1] != "/":
            self.postfix += "/"

        # Configure HTTP basic authorization: Basic
        self.configuration = airflow_api.Configuration(
            host=f"http://{self.server}:{self.port}{self.postfix}api/v1", username=self.user, password=self.password
        )
        super().__init__(__class__.__name__)

    def connect(self):
        """
        Connect to Airflow
        """
        try:
            self.client = airflow_api.ApiClient(self.configuration)
            if self.get_dags() is not None:
                self.logger.info("connected")
                return True
            else:
                return False
        except (airflow_api.ApiException, RequestError, ConnectionError, NewConnectionError) as err:
            self.logger.error(err)
            return False

    def disconnect(self):
        """
        Disconnect from Airflow
        """
        self.client = None
        self.logger.info("disconnected")
        return True

    def get_dags(self):
        """
        Get all DAG's

        :return: DAGCollection if successful, None otherwise
        """
        try:
            api_instance = dag_api.DAGApi(self.client)
            limit = 100
            offset = 0
            only_active = False

            api_response = api_instance.get_dags(limit=limit, offset=offset, only_active=only_active)

            self.logger.info(api_response)
            return api_response
        except (airflow_api.ApiException, RequestError, ConnectionError, NewConnectionError) as err:
            self.logger.error(err)
            return None

    def get_running_dags(self):
        """
        Get all running DAG's

        :return: DAGRunCollection if successful, None otherwise
        """
        try:
            api_instance = dag_run_api.DAGRunApi(self.client)
            list_dag_runs_form = ListDagRunsForm(page_offset=0, page_limit=100)
            api_response = api_instance.get_dag_runs_batch(list_dag_runs_form)
            self.logger.info(api_response)
            return api_response
        except (airflow_api.ApiException, RequestError, ConnectionError, NewConnectionError) as err:
            self.logger.error(err)
            return None

    def post_dag_run(self, dag_name, dag_uuid, dag_config):
        """
        Post a new DAG run to the airflow instance on the ml-backend
        of given xcom data key with new output key

        :param str dag_name: Name of the airflow DAG to run
        :param array dag_uuid: UUID for the DAG run
        :param dict dag_config: JSON configuration for the DAG run

        :return: bool True if the DAG run was triggered successful, otherwise False
        """
        try:
            api_instance = dag_run_api.DAGRunApi(self.client)
            dag_run = DAGRun(dag_run_id=str(dag_uuid), conf=dag_config)
            # Trigger a new DAG run
            api_response = api_instance.post_dag_run(dag_name, dag_run)
            self.logger.info(api_response)
            return True
        except (airflow_api.ApiException, RequestError, ConnectionError, NewConnectionError) as err:
            self.logger.error(err)
            return False
