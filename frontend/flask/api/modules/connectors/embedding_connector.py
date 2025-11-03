#!/usr/bin/env python
"""
Connector to a text embedding service running on slurm
"""

import json
import time
from typing import List, Dict, Any
import requests
from urllib3.exceptions import RequestError, NewConnectionError

from api.modules.connectors.connector import Connector
from api.modules.message import Message


class EmbeddingConnector(Connector):
    """
    Handle text embedding service connections.
    """

    def __init__(
        self,
        embedding_server,
        embedding_port,
        embedding_user,
        embedding_password,
        orchestrator_server,
        orchestrator_port,
        orchestrator_user,
        orchestrator_password,
        orchestrator_embedding_route,
        use_orchestrator,
    ):
        """
        Initialization

        :param str embedding_server: embedding service server name
        :param str embedding_port: embedding service port address
        :param str embedding_user: embedding service user
        :param str embedding_password: embedding service password
        :param str orchestrator_server: orchestrator server name
        :param str orchestrator_port: orchestrator port address
        :param str orchestrator_user: orchestrator user
        :param str orchestrator_password: orchestrator password
        :param str orchestrator_embedding_route: Route to embedding service via orchestrator
        :param bool use_orchestrator: Flag, if orchestrator is used
        """
        self.use_orchestrator = use_orchestrator
        self.orchestrator_embedding_route = orchestrator_embedding_route
        if self.use_orchestrator:
            self.server = orchestrator_server
            self.port = orchestrator_port
            self.user = orchestrator_user
            self.password = orchestrator_password
            self.pre_url = "http://" + self.server + ":" + self.port + "/" + self.orchestrator_embedding_route
        else:
            self.server = embedding_server
            self.port = embedding_port
            self.user = embedding_user
            self.password = embedding_password
            self.pre_url = "http://" + self.server + ":" + self.port
        self.headers = {"Content-Type": "application/json"}
        super().__init__(__class__.__name__)

    def connect(self):
        """
        Connect to embedding service
        """
        return self.check_health()

    def disconnect(self):
        """
        Disconnect from embedding service
        """
        self.logger.info("disconnected")
        return True

    def _gen_payload(self, texts: List[str] | str):
        """
        Generate payload for request to embedding service

        :param str prompt: the user message (prompt)
        :param str context: the context (transcript)
        :param str contextUuid: uuid of the context (media item uuid)
        :param int k: The number of most relevant documents to return, default for us is 4.

        :returns dict payload
        """
        return {"inputs": texts}

    def _create_embedding_result(self, message_data: Message, sentence_list: list):
        """
        Parses embedding service response and creates EmbeddingResult
        """
        final_text = ""
        for i, elem in enumerate(sentence_list):
            final_text = final_text + "- [" + str(i) + "] " + elem + "\\n"
        final_message = message_data.model_dump()
        final_message["context"] = final_text
        result = {"data": [{"type": "EmbeddingResult", "result": [final_message]}]}
        return result

    def check_health(self):
        """
        Check embedding service for health
        """
        try:
            if self.use_orchestrator:
                url = "http://" + self.server + ":" + self.port + "/check_embedding_service"
            else:
                url = self.pre_url + "/health"
            print(f"Health check embedding: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise HTTPError for bad status codes
            if response.status_code == 200:
                if self.use_orchestrator:
                    json_data = json.loads(response.content)
                    # print(f'json_data {json_data}')
                    if json_data["running"] and json_data["started"]:
                        print(f"Health check embedding - True")
                        return True
                    else:
                        print(f"Health check embedding - False - Reason: {json_data['reason']}")
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
        Request embedding service run up
        """
        try:
            if self.use_orchestrator:
                url = "http://" + self.server + ":" + self.port + "/demand_embedding_service"
                print(f"Request embedding service via: {url}")
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

    def post_embedding(self, message_data: Message):
        """
        Post message to embedding service
        """
        url = self.pre_url + "/embed"
        print(f"Sending request to embedding: {url}")
        payload = {"inputs": [message_data.content[0].content[0].text]}
        print("Embed", flush=True)
        start_time = time.time()
        response = requests.post(url, data=json.dumps(payload), headers=self.headers)
        end_time = time.time()
        el_time = end_time - start_time
        print(f"Elapsed time for embed: {el_time:.2f} seconds", flush=True)
        # print("Response status code:", response.status_code)
        # print("Response content:", response.content)
        embeddings_data = response.json()[0]
        return embeddings_data
        # return self._create_embedding_result(message_data, sentence_list)

    def get_info(self):
        """
        Get translation webservice info
        """
        try:
            url = self.pre_url + "/info"
            print(f"Get info from embedding model: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise HTTPError for bad status codes
            if response.status_code == 200:
                json_data = response.json()
                # Handle if the model is stored on local disk
                # "/data/models--mistralai--Mistral-7B-Instruct-v0.2/snapshots/41b61a33a24838"
                if "/models--" in json_data["model_id"]:
                    data_path_arr = json_data["model_id"].split("/models--")
                    modelid_snapshot_sha = data_path_arr[1].split("/")
                    json_data["model_id"] = modelid_snapshot_sha[0].replace("--", "/")
                    json_data["model_sha"] = modelid_snapshot_sha[2]
                json_data["max_new_tokens"] = json_data["max_input_length"]
                json_data["max_total_tokens"] = json_data["max_batch_tokens"]
                return json_data
            else:
                return None
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
        ) as err:
            self.logger.error(err)
            return None
