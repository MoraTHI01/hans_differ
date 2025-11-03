#!/usr/bin/env python
"""
Connector to a hans llm service running on slurm with
https://github.com/predibase/lorax
based on https://github.com/huggingface/text-generation-inference
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
import tiktoken
from openai import OpenAI
from pydantic import BaseModel, Field
from urllib3.exceptions import RequestError, NewConnectionError

from api.modules.connectors.connector import Connector
from api.modules.message import Message, MessageHistory, MessageContent, TextContent
from api.modules.prompt_base import PromptBase
from api.modules.responses import ErrorResponse

from tokenizers import normalizers
from tokenizers.normalizers import NFD, StripAccents


class LlmConnector(Connector):
    """
    Handle llm connections.
    See https://huggingface.github.io/text-generation-inference
    """

    def __init__(
        self,
        llm_server,
        llm_port,
        llm_user,
        llm_password,
        llm_model_id,
        llm_max_new_tokens,
        orchestrator_server,
        orchestrator_port,
        orchestrator_user,
        orchestrator_password,
        orchestrator_llm_route,
        use_orchestrator,
    ):
        """
        Initialization

        :param str llm_server: llm server name
        :param str llm_port: llm port address
        :param str llm_user: llm user
        :param str llm_password: llm password
        :param str llm_model_id: llm model id
        :param str orchestrator_server: orchestrator server name
        :param str orchestrator_port: orchestrator port address
        :param str orchestrator_user: orchestrator user
        :param str orchestrator_password: orchestrator password
        :param str orchestrator_llm_route: Route to llm service via orchestrator
        :param bool use_orchestrator: Flag, if orchestrator is used
        """
        self.max_new_tokens = llm_max_new_tokens
        self.use_orchestrator = use_orchestrator
        self.orchestrator_llm_route = orchestrator_llm_route
        self.llm_model_id = llm_model_id
        self.token_limit = 6120  # 10240 7168 6120
        if self.use_orchestrator:
            self.server = orchestrator_server
            self.port = orchestrator_port
            self.user = orchestrator_user
            self.password = orchestrator_password
            self.pre_url_raw = "http://" + self.server + ":" + self.port + "/" + self.orchestrator_llm_route
            self.pre_url = self.pre_url_raw + "/v1"
        else:
            self.server = llm_server
            self.port = llm_port
            self.user = llm_user
            self.password = llm_password
            self.pre_url_raw = "http://" + self.server + ":" + self.port
            self.pre_url = self.pre_url_raw + "/v1"

        self.client = OpenAI(api_key="EMPTY", base_url=self.pre_url)

        self.prompts = PromptBase(self.llm_model_id)

        self.headers = {"Content-Type": "application/json"}
        super().__init__(__class__.__name__)

    def connect(self):
        """
        Connect to llm
        """
        return self.check_health()

    def disconnect(self):
        """
        Disconnect from llm
        """
        self.logger.info("disconnected")
        return True

    def _gen_messages(
        self, system_prompt, user_prompt: TextContent, history: list[MessageHistory] = [], context_sentence=None
    ):
        """Create openai compat message array"""
        messages = [{"role": "system", "content": system_prompt.strip()}]
        for history_item in history:
            if history_item.isUser is True:
                messages.append({"role": "user", "content": history_item.content[0].text})
            else:
                messages.append({"role": "assistant", "content": history_item.content[0].text})
        user_content = user_prompt.text

        if context_sentence is not None and len(context_sentence) > 0:
            user_content += " " + context_sentence

        messages.append({"role": "user", "content": user_content})
        # print(json.dumps({"messages": messages}), flush=True)
        return messages

    def _gen_prompt(self, message_data: Message, message_content: MessageContent = None):
        """
        Generate prompt for llm

        :param Message message_data: message of the user to be sent
        :param MessageContent message_content: Overwrite used message content for translation mode

        :returns dict messages
        """
        if message_data.context is not None:
            message_data.context = self.shorten_context_data(message_data.context)

        curr_message_content = message_data.content[0]
        if message_content is not None:
            curr_message_content = message_content
        curr_user_prompt = curr_message_content.content[0]
        curr_user_prompt.text = curr_user_prompt.text.replace("\\n", " ").strip()

        system_prompt = self.prompts.base_system_prompt.replace("[INST] ", "")

        if message_data.actAsTutor is True:
            system_prompt = system_prompt + self.prompts.tutor_system_prompt

        if message_data.useContextAndCite is True or message_data.useContext is True:
            if message_data.useContextAndCite is True:
                system_prompt = system_prompt + self.prompts.cite_addon
            elif message_data.useContext is True:
                system_prompt = system_prompt + self.prompts.context_addon

        if curr_message_content.language == "en":
            system_prompt = system_prompt + self.prompts.language_system_prompt_en
        elif curr_message_content.language == "de":
            if message_data.useTranslate is True:
                # If translation service is used we use English only
                system_prompt = system_prompt + self.prompts.language_system_prompt_en
            else:
                system_prompt = system_prompt + self.prompts.language_system_prompt_de

        context_sentence = None
        if message_data.useContextAndCite is True or message_data.useContext is True:
            clean_context = (
                message_data.context.replace("\\\\\\\\n", "\\n")
                .replace("\\\\n\\\\n", "\\n\\n")
                .replace("\\\\n", "\\n")
                .replace("\\\n\\\n", "\\n\\n")
                .replace("\\\n", "\\n")
                .replace('\\"', " ")
                .replace('"', " ")
                .strip()
            )
            # clean_context = ''.join(filter(lambda x: x in string.printable, clean_context)).strip()
            # clean_context = self._encode_urls_in_text(clean_context)
            if message_data.useContextAndCite is True:
                context_sentence = (
                    "Give appropriate citations refering to the following "
                    + self.prompts.prompt_context_tag
                    + f" sections: {clean_context}"
                )
            else:
                context_sentence = "Use the following " + self.prompts.prompt_context_tag + f": {clean_context}"

        return self._gen_messages(system_prompt, curr_user_prompt, message_data.history, context_sentence)

    def _query_llm(self, messages, schema=None, stream=False):
        """
        Query llm with messages
        """
        if stream is True:
            print("Ask llm use streaming", flush=True)
            if schema is None:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=self.llm_model_id,  # optional: specify an adapter ID here
                    max_tokens=self.max_new_tokens,
                    n=1,
                    timeout=360.0,
                    temperature=0.15,
                    stream=stream,
                )
            else:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=self.llm_model_id,  # optional: specify an adapter ID here
                    max_tokens=4096,
                    n=1,
                    timeout=360.0,
                    # tgi uses grammar={"type": "json", "value": Animals.schema()} as usual parameter
                    # https://huggingface.co/docs/text-generation-inference/basic_tutorials/using_guidance#grammar-and-constraints-
                    response_format={"type": "json", "value": dict(schema)},
                    frequency_penalty=0.3,
                    temperature=0.15,
                    stream=stream,
                )
            return response
        else:
            print("Ask llm", flush=True)
            if schema is None:
                start_time = time.time()
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=self.llm_model_id,  # optional: specify an adapter ID here
                    max_tokens=self.max_new_tokens,
                    n=1,
                    timeout=360.0,
                    temperature=0.15,
                )
                end_time = time.time()
                el_time = end_time - start_time
                print(f"Elapsed time llm generation: {el_time:.2f} seconds", flush=True)
            else:
                start_time = time.time()
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=self.llm_model_id,  # optional: specify an adapter ID here
                    max_tokens=4096,
                    n=1,
                    # tgi uses grammar={"type": "json", "value": Animals.schema()} as usual parameter
                    # https://huggingface.co/docs/text-generation-inference/basic_tutorials/using_guidance#grammar-and-constraints-
                    response_format={"type": "json", "value": dict(schema)},
                    frequency_penalty=0.3,
                    temperature=0.15,
                    timeout=360.0,
                )
                end_time = time.time()
                el_time = end_time - start_time
                print(f"Elapsed time llm generation: {el_time:.2f} seconds", flush=True)
            if len(response.choices) > 0:
                return response.choices[0].message.content
        return None

    def _create_llm_result(self, message_data: Message, response_text, language=None) -> dict:
        """
        Parses llm response and creates LlmResult
        """
        curr_language = message_data.content[0].language
        if language is not None:
            curr_language = language
        result = {
            "data": [
                {
                    "type": "LlmResult",
                    "result": [
                        {
                            "content": [
                                {"language": curr_language, "content": [{"type": "text", "text": response_text}]}
                            ],
                            "isUser": False,
                            "context": message_data.context,
                            "contextUuid": message_data.contextUuid,
                            "useContext": message_data.useContext,
                            "useContextAndCite": message_data.useContextAndCite,
                            "useVision": message_data.useVision,
                            "useVisionSurroundingSlides": message_data.useVisionSurroundingSlides,
                            "useVisionSnapshot": message_data.useVisionSnapshot,
                            "snapshot": message_data.snapshot,
                            "actAsTutor": message_data.actAsTutor,
                            "useTranslate": message_data.useTranslate,
                            "stream": message_data.stream,
                        }
                    ],
                }
            ]
        }
        return result

    def check_health(self):
        """
        Check llm webservice for health
        """
        try:
            if self.use_orchestrator:
                url = "http://" + self.server + ":" + self.port + "/check_llm_service"
            else:
                url = self.pre_url_raw + "/health"
            print(f"Health check llm: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise HTTPError for bad status codes
            if response.status_code == 200:
                if self.use_orchestrator:
                    json_data = json.loads(response.content)
                    # print(f'json_data {json_data}')
                    if json_data["running"] and json_data["started"]:
                        print(f"Health check llm - True")
                        return True
                    else:
                        print(f"Health check llm - False - Reason: {json_data['reason']}")
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
        Request llm service run up
        """
        try:
            if self.use_orchestrator:
                url = "http://" + self.server + ":" + self.port + "/demand_llm_service"
                print(f"Request llm service via: {url}")
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

    def get_info(self):
        """
        Get llm webservice info
        """
        try:
            url = self.pre_url_raw + "/info"
            print(f"Get info from llm: {url}")
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

    def post_llm(self, message_data: Message, schema=None) -> dict:
        """
        Post message to llm webservice
        """
        print(f"Sending request to llm: {self.pre_url}")
        # print(f"Context: {message_data.context}")
        # print(f"History: {message_data.history}")
        if message_data.useTranslate is True:
            for message_content in message_data.content:
                if message_content.language == "en":
                    messages = self._gen_prompt(message_data, message_content)
                    response = self._query_llm(messages, schema, message_data.stream)
                    return self._create_llm_result(message_data, response, message_content.language)
        else:
            messages = self._gen_prompt(message_data)
            response = self._query_llm(messages, schema, message_data.stream)
            return self._create_llm_result(message_data, response)

    def post_llm_stream(self, message_data: Message, schema=None):
        """
        Post message to llm webservice with streaming
        """
        print(f"Sending request to llm using streaming: {self.pre_url}")
        # print(f"Context: {message_data.context}")
        # print(f"History: {message_data.history}")
        if message_data.useTranslate is True:
            for message_content in message_data.content:
                if message_content.language == "en":
                    messages = self._gen_prompt(message_data, message_content)
                    response = self._query_llm(messages, schema, message_data.stream)
                    if message_data.stream is True:
                        start_time = time.time()
                        final_text_response = ""
                        for chunk in response:
                            if chunk.choices[0].delta.content is not None:
                                final_text_response += chunk.choices[0].delta.content
                                yield chunk.choices[0].delta.content
                        end_time = time.time()
                        el_time = end_time - start_time
                        print(f"Elapsed time llm generation streaming: {el_time:.2f} seconds", flush=True)
                        return self._create_llm_result(message_data, final_text_response, message_content.language)
        else:
            messages = self._gen_prompt(message_data)
            response = self._query_llm(messages, schema, message_data.stream)
            if message_data.stream is True:
                start_time = time.time()
                final_text_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        final_text_response += chunk.choices[0].delta.content
                        yield chunk.choices[0].delta.content
                end_time = time.time()
                el_time = end_time - start_time
                print(f"Elapsed time llm generation streaming: {el_time:.2f} seconds", flush=True)
                return self._create_llm_result(message_data, final_text_response)

    def calc_token_len(self, text):
        """
        Give an approx. number of tokens
        """
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        num_tokens = len(encoding.encode(text))
        return num_tokens

    def remove_sentences(self, text, val=7):
        """
        Remove every x sentences from text
        """
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences_shrink = [item for i, item in enumerate(sentences) if (i + 1) % val != 0]
        return " ".join(sentences_shrink)

    def remove_word(self, text, val=7):
        """
        Remove words x sentences from text
        """
        words = text.split(" ")
        words_shrink = [item for i, item in enumerate(words) if (i + 1) % val != 0]
        return " ".join(words_shrink)

    def tokenizers_normalize_text(self, text):
        """
        Normalize text using tokenizers
        """
        normalizer = normalizers.Sequence([NFD(), StripAccents()])
        return normalizer.normalize_str(text)

    def shorten_context_data(self, context_data: str) -> str:
        """
        shrink token size by removing stop words from text if approx. token size is too big
        """
        # print(f"context_data before ascii: {context_data}")
        context_data_tk_len = self.calc_token_len(context_data)
        print(f"Token length before ascii: {context_data_tk_len}")
        context_data = (
            self.tokenizers_normalize_text(context_data).encode("ascii", "ignore").decode().replace("\n", " ")
        )
        # print(f"context_data ascii: {context_data}")
        context_data_tk_len = self.calc_token_len(context_data)
        print(f"Token length ascii: {context_data_tk_len}")
        context_data_tk_len_prev = context_data_tk_len
        stop_now = False
        if context_data_tk_len > self.token_limit:
            while context_data_tk_len > self.token_limit and not stop_now:
                context_data = self.remove_sentences(context_data)
                context_data_tk_len = self.calc_token_len(context_data)
                print(f"Token length after remove sentences: {context_data_tk_len}")
                if context_data_tk_len_prev > context_data_tk_len:
                    context_data_tk_len_prev = context_data_tk_len
                else:
                    stop_now = True
        if stop_now is True:
            if context_data_tk_len > self.token_limit:
                while context_data_tk_len > self.token_limit:
                    context_data = self.remove_word(context_data)
                    context_data_tk_len = self.calc_token_len(context_data)
                    print(f"Token length after remove sentences: {context_data_tk_len}")

        # print(f"context_data final: {context_data}")
        context_data_tk_len = self.calc_token_len(context_data)
        print(f"Token length final: {context_data_tk_len}")
        return context_data
