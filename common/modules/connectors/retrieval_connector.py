#!/usr/bin/env python
"""
Connector to a hans retrieval service running on slurm
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"

import json
import requests
from urllib3.exceptions import RequestError, NewConnectionError

from connectors.connector import Connector
from llm.message import Message


class RetrievalConnector(Connector):
    """
    Handle retrieval service connections.
    """

    def __init__(
        self,
        retrieval_server,
        retrieval_port,
        retrieval_user,
        retrieval_password,
        orchestrator_server,
        orchestrator_port,
        orchestrator_user,
        orchestrator_password,
        orchestrator_retrieval_route,
        use_orchestrator,
    ):
        """
        Initialization

        :param str retrieval_server: retrieval service server name
        :param str retrieval_port: retrieval service port address
        :param str retrieval_user: retrieval service user
        :param str retrieval_password: retrieval service password
        :param str orchestrator_server: orchestrator server name
        :param str orchestrator_port: orchestrator port address
        :param str orchestrator_user: orchestrator user
        :param str orchestrator_password: orchestrator password
        :param str orchestrator_retrieval_route: Route to retrieval service via orchestrator
        :param bool use_orchestrator: Flag, if orchestrator is used
        """
        self.use_orchestrator = use_orchestrator
        self.orchestrator_retrieval_route = orchestrator_retrieval_route
        if self.use_orchestrator:
            self.server = orchestrator_server
            self.port = orchestrator_port
            self.user = orchestrator_user
            self.password = orchestrator_password
            self.pre_url = "http://" + self.server + ":" + self.port + "/" + self.orchestrator_retrieval_route
        else:
            self.server = retrieval_server
            self.port = retrieval_port
            self.user = retrieval_user
            self.password = retrieval_password
            self.pre_url = "http://" + self.server + ":" + self.port
        self.headers = {"Content-Type": "application/json"}
        super().__init__(__class__.__name__)

    def connect(self):
        """
        Connect to retrieval service
        """
        return self.check_health()

    def disconnect(self):
        """
        Disconnect from retrieval service
        """
        self.logger.info("disconnected")
        return True

    def _gen_payload(self, prompt, context, contextUuid, k=4):
        """
        Generate payload for request to retrieval service

        :param str prompt: the user message (prompt)
        :param str context: the context (transcript)
        :param str contextUuid: uuid of the context (media item uuid)
        :param int k: The number of most relevant documents to return, default for us is 4.

        :returns dict payload
        """
        return {"text": prompt, "context": context, "k": k, "uuid": contextUuid}

    def _create_retrieval_result(self, message_data: Message, sentence_list: list):
        """
        Parses retrieval service response and creates RetrievalResult
        """
        final_text = ""
        for i, elem in enumerate(sentence_list):
            final_text = final_text + "- [" + str(i) + "] " + elem + "\\n"
        final_message = message_data.model_dump()
        final_message["context"] = final_text
        result = {"data": [{"type": "RetrievalResult", "result": [final_message]}]}
        return result

    def check_health(self):
        """
        Check retrieval service for health
        """
        try:
            if self.use_orchestrator:
                url = "http://" + self.server + ":" + self.port + "/check_retrieval_service"
            else:
                url = self.pre_url + "/health"
            print(f"Health check retrieval: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise HTTPError for bad status codes
            if response.status_code == 200:
                if self.use_orchestrator:
                    json_data = json.loads(response.content)
                    # print(f'json_data {json_data}')
                    if json_data["running"] and json_data["started"]:
                        print(f"Health check retrieval - True")
                        return True
                    else:
                        print(f"Health check retrieval - False - Reason: {json_data['reason']}")
                        return False
                else:
                    return True
            else:
                return False
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
        ) as err:
            self.logger.error(err)
            return False

    def request_service(self):
        """
        Request retrieval service run up
        """
        try:
            if self.use_orchestrator:
                url = "http://" + self.server + ":" + self.port + "/demand_retrieval_service"
                print(f"Request retrieval service via: {url}")
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()  # Raise HTTPError for bad status codes
                if response.status_code == 200:
                    return True
                else:
                    return None
            else:
                return self.check_health()
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
        ) as err:
            self.logger.error(err)
            return None

    def post_retrieval(self, message_data: Message):
        """
        Post message to retrieval service
        """
        url = self.pre_url + "/query"
        print(f"Sending request to retrieval: {url}")
        payload = self._gen_payload(message_data.content[0].content, message_data.context, message_data.contextUuid)
        response = requests.post(url, data=json.dumps(payload), headers=self.headers)
        print("Response status code:", response.status_code)
        # print("Response content:", response.content)
        sentence_list = list(response.json()["result"])
        return self._create_retrieval_result(message_data, sentence_list)
