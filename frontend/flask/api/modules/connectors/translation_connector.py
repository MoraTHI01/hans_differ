#!/usr/bin/env python
"""
Connector to a hans translation service running on slurm
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"

import json
import time
import re
import requests
from urllib3.exceptions import RequestError, NewConnectionError

from api.modules.connectors.connector import Connector
from api.modules.message import Message, MessageContent, TextContent


class TranslationConnector(Connector):
    """
    Handle translation service connections.
    """

    def __init__(
        self,
        translation_server,
        translation_port,
        translation_user,
        translation_password,
        orchestrator_server,
        orchestrator_port,
        orchestrator_user,
        orchestrator_password,
        orchestrator_translation_route,
        use_orchestrator,
    ):
        """
        Initialization

        :param str translation_server: translation service server name
        :param str translation_port: translation service port address
        :param str translation_user: translation service user
        :param str translation_password: translation service password
        :param str orchestrator_server: orchestrator server name
        :param str orchestrator_port: orchestrator port address
        :param str orchestrator_user: orchestrator user
        :param str orchestrator_password: orchestrator password
        :param str orchestrator_translation_route: Route to translation service via orchestrator
        :param bool use_orchestrator: Flag, if orchestrator is used
        """
        self.use_orchestrator = use_orchestrator
        self.orchestrator_translation_route = orchestrator_translation_route
        if self.use_orchestrator:
            self.server = orchestrator_server
            self.port = orchestrator_port
            self.user = orchestrator_user
            self.password = orchestrator_password
            self.pre_url = "http://" + self.server + ":" + self.port + "/" + self.orchestrator_translation_route
        else:
            self.server = translation_server
            self.port = translation_port
            self.user = translation_user
            self.password = translation_password
            self.pre_url = "http://" + self.server + ":" + self.port
        self.max_new_tokens = 512
        self.headers = {"Content-Type": "application/json"}
        super().__init__(__class__.__name__)

    def connect(self):
        """
        Connect to translation service
        """
        return self.check_health()

    def disconnect(self):
        """
        Disconnect from translation service
        """
        self.logger.info("disconnected")
        return True

    def _gen_payload(self, prompt):
        """
        Generate payload for request to translation service

        :param str prompt: the user message (prompt)

        :returns dict payload
        """
        return {"inputs": prompt, "parameters": {"max_new_tokens": self.max_new_tokens}}

    def _create_translation_result(self, message_data: Message):
        """
        Parses translation service response and creates TranslationResult
        """
        result = {"data": [{"type": "TranslationResult", "result": [message_data.model_dump()]}]}
        return result

    def check_health(self):
        """
        Check translation service health
        """
        try:
            if self.use_orchestrator:
                url = "http://" + self.server + ":" + self.port + "/check_translation_service"
            else:
                url = self.pre_url + "/health"
            print(f"Health check translation: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise HTTPError for bad status codes
            if response.status_code == 200:
                if self.use_orchestrator:
                    json_data = json.loads(response.content)
                    # print(f'json_data {json_data}')
                    if json_data["running"] and json_data["started"]:
                        print(f"Health check translation - True")
                        return True
                    else:
                        print(f"Health check translation - False - Reason: {json_data['reason']}")
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
        Request translation service run up
        """
        try:
            if self.use_orchestrator:
                url = "http://" + self.server + ":" + self.port + "/demand_translation_service"
                print(f"Request translation service via: {url}")
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

    def split_text_into_chunks(self, text, sentences_per_chunk=4):
        """
        Split text into sentence chunks
        """
        # List of known abbreviations with periods
        abbreviations = [
            "Mr.",
            "Mrs.",
            "Ms.",
            "Dr.",
            "Prof.",
            "Capt.",
            "Col.",
            "Gen.",
            "Rev.",
            "Lt.",
            "Sgt.",
            "St.",
            "Jr.",
            "Sr.",
            "Co.",
            "Inc.",
            "Ltd.",
            "etc.",
            "Hr.",
            "Fr.",
            "Herr",
            "Frau",
            "u.a.",
            "z.B.",
            "d.h.",
            "i.d.R.",
            "i.e.",
            "u.s.w.",
        ]
        # Define a regular expression pattern to match sentence endings
        sentence_endings = re.compile(r"([.!?])\s+")
        # Initialize an empty list to store sentences
        sentences = []
        start = 0
        # Iterate over the text to find sentence-ending punctuation
        for match in sentence_endings.finditer(text):
            # Extract the sentence-ending character and following space
            end_punct = match.group(1)
            next_char_index = match.end()
            # Get the potential sentence
            sentence = text[start:next_char_index].strip()
            # Check if the preceding token is an abbreviation
            if any(sentence.endswith(abbrev) for abbrev in abbreviations):
                continue
            # Otherwise, consider this a sentence boundary
            sentences.append(sentence)
            start = next_char_index
        # Add any remaining text as the last sentence
        remaining_text = text[start:].strip()
        if remaining_text:
            sentences.append(remaining_text)
        # Initialize the list to store chunks
        chunks = []
        # Group sentences into chunks of the specified number of sentences
        for i in range(0, len(sentences), sentences_per_chunk):
            chunk = " ".join(sentences[i : i + sentences_per_chunk])
            chunks.append(chunk)
        return chunks

    def translate_iter(self, url, content, source_language, target_language):
        """
        Translate long texts
        """
        partial_message = ""
        text_arr = self.split_text_into_chunks(content.strip(), 4)
        print("Translate sentences", flush=True)
        total_start_time = time.time()
        for idx, sentence in enumerate(text_arr):
            if len(sentence) > 0:
                prompt = "<2" + target_language + "> " + sentence
                payload = self._gen_payload(prompt)
                print("Translate", flush=True)
                start_time = time.time()
                response = requests.post(url, data=json.dumps(payload), headers=self.headers)
                end_time = time.time()
                el_time = end_time - start_time
                print(f"Elapsed time: {el_time:.2f} seconds", flush=True)
                # print("Response status code:", response.status_code)
                # print("Response content:", response.content)
                partial_message += response.json()["generated_text"].rsplit("</s>")[0] + " "
        total_end_time = time.time()
        total_el_time = total_end_time - total_start_time
        print(f"Elapsed time all sentences: {total_el_time:.2f} seconds", flush=True)
        return partial_message.strip()

    def post_translation(self, message_data: Message):
        """
        Post message to translation service
        """
        final_response_message = message_data
        if message_data.useTranslate is True:
            url = self.pre_url + "/generate"
            for messageContent in message_data.content:
                if messageContent.language == "de":
                    print(f"Sending request to translation service: {url}")
                    content_result = self.translate_iter(
                        url, messageContent.content[0].text, messageContent.language, "en"
                    )
                    curr_text_content = TextContent(type="text", text=content_result)
                    message_content = MessageContent(language="en", content=[curr_text_content])
                    final_response_message.content.append(message_content)
                    return self._create_translation_result(final_response_message)
                elif messageContent.language == "en":
                    print(f"Sending request to translation service: {url}")
                    content_result = self.translate_iter(
                        url, messageContent.content[0].text, messageContent.language, "de"
                    )
                    curr_text_content = TextContent(type="text", text=content_result)
                    message_content = MessageContent(language="de", content=[curr_text_content])
                    final_response_message.content.append(message_content)
                    return self._create_translation_result(final_response_message)
        return None

    def post_raw_translations(self, source_language: str, target_language: str, messages: [str]) -> [str]:
        url = self.pre_url + "/generate"
        return [self.translate_iter(url, message, source_language, target_language) for message in messages]

    def get_info(self):
        """
        Get translation webservice info
        """
        try:
            url = self.pre_url + "/info"
            print(f"Get info from translation model: {url}")
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
                json_data["max_new_tokens"] = self.max_new_tokens
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
