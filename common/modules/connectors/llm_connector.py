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
from openai import OpenAI
from pydantic import BaseModel, Field
from urllib3.exceptions import RequestError, NewConnectionError

from connectors.connector import Connector
from llm.message import Message, MessageHistory, MessageContent, TextContent
from llm.prompt_base import PromptBase


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
        llm_config,
        orchestrator_server,
        orchestrator_port,
        orchestrator_user,
        orchestrator_password,
        orchestrator_llm_route,
        use_orchestrator,
        reasoning=False,
    ):
        """
        Initialization

        :param str llm_server: llm server name
        :param str llm_port: llm port address
        :param str llm_user: llm user
        :param str llm_password: llm password
        :param str llm_model_id: llm model id
        :param str llm_config: llm model configuration
        :param str orchestrator_server: orchestrator server name
        :param str orchestrator_port: orchestrator port address
        :param str orchestrator_user: orchestrator user
        :param str orchestrator_password: orchestrator password
        :param str orchestrator_llm_route: Route to llm service via orchestrator
        :param bool use_orchestrator: Flag, if orchestrator is used
        :param bool reasoning: Flag, if reasoning is used
        """
        self.use_orchestrator = use_orchestrator
        self.reasoning = reasoning
        self.orchestrator_llm_route = orchestrator_llm_route
        self.llm_model_id = llm_model_id
        self.llm_config = llm_config
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

        self.client = OpenAI(api_key=llm_password, base_url=self.pre_url)

        self.prompt_base = PromptBase()

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
        curr_message_content = message_data.content[0]
        if message_content is not None:
            curr_message_content = message_content
        curr_user_prompt = curr_message_content.content[0]
        curr_user_prompt.text = curr_user_prompt.text.replace("\\n", " ").strip()

        lang = curr_message_content.language
        if message_data.useTranslate is True:
            # Prompt everything in english
            lang = "en"

        if self.reasoning is True:
            system_prompt = self.prompt_base.get_reasoning_system_prompt(lang=lang)
        else:
            system_prompt = self.prompt_base.get_base_system_prompt(lang=lang)

        if message_data.actAsTutor is True:
            system_prompt = system_prompt + self.prompt_base.get_tutor_system_prompt(lang=lang)

        if message_data.useContextAndCite is True or message_data.useContext is True:
            if message_data.useContextAndCite is True:
                if message_data.useChannelContext is True:
                    system_prompt = system_prompt + self.prompt_base.get_channel_cite_addon(lang=lang)
                else:
                    system_prompt = system_prompt + self.prompt_base.get_cite_addon(lang=lang)
            elif message_data.useContext is True:
                if message_data.useChannelContext is True:
                    system_prompt = system_prompt + self.prompt_base.get_channel_context_addon(lang=lang)
                else:
                    system_prompt = system_prompt + self.prompt_base.get_context_addon(lang=lang)

        if lang == "en":
            system_prompt = system_prompt + self.prompt_base.get_force_language_english_addon(lang=lang)
        elif lang == "de":
            system_prompt = system_prompt + self.prompt_base.get_force_language_german_addon(lang=lang)

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
                context_sentence = self.prompt_base.get_cite_prompt(context=clean_context, lang=lang)
            else:
                context_sentence = self.prompt_base.get_context_prompt(context=clean_context, lang=lang)

        return self._gen_messages(system_prompt, curr_user_prompt, message_data.history, context_sentence)

    def query_llm(self, messages, schema=None, stream=False, custom_config: dict = None):
        """
        Query llm with messages
        """
        curr_config = self.llm_config
        if custom_config is not None:
            for key in custom_config.keys():
                curr_config[key] = custom_config[key]

        if stream is True:
            print("Ask llm use streaming", flush=True)
            if schema is None:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=self.llm_model_id,  # optional: specify an adapter ID here
                    max_tokens=curr_config["max_new_tokens"],
                    n=1,
                    timeout=curr_config["timeout"],
                    temperature=curr_config["temperature"],
                    stream=stream,
                )
            else:
                if self.llm_config["engine"].lower() in ["tgi", "openai"]:
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.llm_model_id,  # optional: specify an adapter ID here
                        max_tokens=4096,
                        n=1,
                        timeout=curr_config["timeout"],
                        # TGI compliant https://huggingface.co/docs/text-generation-inference/basic_tutorials/using_guidance#constrain-with-pydantic
                        response_format={"type": "json", "value": dict(schema)},
                        frequency_penalty=curr_config["frequency_penalty"],
                        temperature=curr_config["temperature"],
                        stream=stream,
                    )
                elif self.llm_config["engine"].lower() == "vllm":
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.llm_model_id,  # optional: specify an adapter ID here
                        max_tokens=4096,
                        n=1,
                        timeout=curr_config["timeout"],
                        # VLLM compliant
                        extra_body={"guided_json": dict(schema)},
                        frequency_penalty=curr_config["frequency_penalty"],
                        temperature=curr_config["temperature"],
                        stream=stream,
                    )
                else:
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.llm_model_id,  # optional: specify an adapter ID here
                        max_tokens=4096,
                        n=1,
                        timeout=curr_config["timeout"],
                        # TGI compliant https://huggingface.co/docs/text-generation-inference/basic_tutorials/using_guidance#constrain-with-pydantic
                        response_format={"type": "json", "value": dict(schema)},
                        frequency_penalty=curr_config["frequency_penalty"],
                        temperature=curr_config["temperature"],
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
                    max_tokens=curr_config["max_new_tokens"],
                    n=1,
                    timeout=curr_config["timeout"],
                    temperature=curr_config["temperature"],
                )
                end_time = time.time()
                el_time = end_time - start_time
                print(f"Elapsed time llm generation: {el_time:.2f} seconds", flush=True)
            else:
                start_time = time.time()
                if self.llm_config["engine"].lower() in ["tgi", "openai"]:
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.llm_model_id,  # optional: specify an adapter ID here
                        max_tokens=4096,
                        n=1,
                        # TGI compliant https://huggingface.co/docs/text-generation-inference/basic_tutorials/using_guidance#constrain-with-pydantic
                        response_format={"type": "json", "value": dict(schema)},
                        frequency_penalty=curr_config["frequency_penalty"],
                        temperature=curr_config["temperature"],
                        timeout=curr_config["timeout"],
                    )
                elif self.llm_config["engine"].lower() == "vllm":
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.llm_model_id,  # optional: specify an adapter ID here
                        max_tokens=4096,
                        n=1,
                        # VLLM compliant
                        extra_body={"guided_json": dict(schema)},
                        frequency_penalty=curr_config["frequency_penalty"],
                        temperature=curr_config["temperature"],
                        timeout=curr_config["timeout"],
                    )
                else:
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.llm_model_id,  # optional: specify an adapter ID here
                        max_tokens=4096,
                        n=1,
                        # TGI compliant https://huggingface.co/docs/text-generation-inference/basic_tutorials/using_guidance#constrain-with-pydantic
                        response_format={"type": "json", "value": dict(schema)},
                        frequency_penalty=curr_config["frequency_penalty"],
                        temperature=curr_config["temperature"],
                        timeout=curr_config["timeout"],
                    )
                end_time = time.time()
                el_time = end_time - start_time
                print(f"Elapsed time llm generation: {el_time:.2f} seconds", flush=True)
            if len(response.choices) > 0:
                if self.reasoning is True:
                    if hasattr(response.choices[0].message, "reasoning_content"):
                        return response.choices[0].message.reasoning_content
                    else:
                        return response.choices[0].message.content
                else:
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
                            "reasoning": message_data.reasoning,
                            "mediaContextUuids": message_data.mediaContextUuids,
                            "documentContextUuids": message_data.documentContextUuids,
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
        if self.llm_config["engine"].lower() in ["vllm", "openai"]:
            # reasoning model is a vllm inference engine instance
            model_sha = "unknown"
            max_new_tokens = 16384
            model_dtype = "float16"
            max_total_tokens = 32768
            try:
                model_list = self.client.models.list()
                for model in model_list.data:
                    if model.id == self.llm_model_id:
                        if "FP8-dynamic" in model.root:
                            model_dtype = "FP8 W8A8"
                        else:
                            model_dtype = "float16"
                        max_total_tokens = model.max_model_len
                        max_new_tokens = int(max_total_tokens / 2.0)
            except (
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.RequestException,
            ) as err:
                self.logger.error(err)
                return None
            return {
                "model_id": self.llm_model_id,
                "model_sha": model_sha,
                "model_dtype": model_dtype,
                "max_new_tokens": max_new_tokens,
                "max_total_tokens": max_total_tokens,
            }
        else:
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
                    json_data["max_new_tokens"] = self.llm_config["max_new_tokens"]
                    json_data["model_dtype"] = "float16"
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
        if self.reasoning is True:
            print(f"Sending request to reasoning llm: {self.pre_url}")
        else:
            print(f"Sending request to llm: {self.pre_url}")
        # print(f"Context: {message_data.context}")
        # print(f"History: {message_data.history}")
        if message_data.useTranslate is True:
            for message_content in message_data.content:
                if message_content.language == "en":
                    messages = self._gen_prompt(message_data, message_content)
                    response = self.query_llm(messages, schema, message_data.stream)
                    return self._create_llm_result(message_data, response, message_content.language)
        else:
            messages = self._gen_prompt(message_data)
            response = self.query_llm(messages, schema, message_data.stream)
            return self._create_llm_result(message_data, response)

    def post_llm_stream(self, message_data: Message, schema=None):
        """
        Post message to llm webservice with streaming
        """
        if self.reasoning is True:
            print(f"Sending request to reasoning llm using streaming: {self.pre_url}")
        else:
            print(f"Sending request to llm using streaming: {self.pre_url}")
        # print(f"Context: {message_data.context}")
        # print(f"History: {message_data.history}")
        if message_data.useTranslate is True:
            for message_content in message_data.content:
                if message_content.language == "en":
                    messages = self._gen_prompt(message_data, message_content)
                    response = self.query_llm(messages, schema, message_data.stream)
                    if message_data.stream is True:
                        start_time = time.time()
                        final_text_response = ""
                        for chunk in response:
                            if self.reasoning is True:
                                if hasattr(chunk.choices[0].delta, "reasoning_content"):
                                    final_text_response += chunk.choices[0].delta.reasoning_content
                                    yield chunk.choices[0].delta.reasoning_content
                                else:
                                    if chunk.choices[0].delta.content is not None:
                                        final_text_response += chunk.choices[0].delta.content
                                        yield chunk.choices[0].delta.content
                            else:
                                if chunk.choices[0].delta.content is not None:
                                    final_text_response += chunk.choices[0].delta.content
                                    yield chunk.choices[0].delta.content
                        end_time = time.time()
                        el_time = end_time - start_time
                        print(f"Elapsed time llm generation streaming: {el_time:.2f} seconds", flush=True)
                        return self._create_llm_result(message_data, final_text_response, message_content.language)
        else:
            messages = self._gen_prompt(message_data)
            response = self.query_llm(messages, schema, message_data.stream)
            if message_data.stream is True:
                start_time = time.time()
                final_text_response = ""
                for chunk in response:
                    if self.reasoning is True:
                        if hasattr(chunk.choices[0].delta, "reasoning_content"):
                            final_text_response += chunk.choices[0].delta.reasoning_content
                            yield chunk.choices[0].delta.reasoning_content
                        else:
                            if chunk.choices[0].delta.content is not None:
                                final_text_response += chunk.choices[0].delta.content
                                yield chunk.choices[0].delta.content
                    else:
                        if chunk.choices[0].delta.content is not None:
                            final_text_response += chunk.choices[0].delta.content
                            yield chunk.choices[0].delta.content
                end_time = time.time()
                el_time = end_time - start_time
                print(f"Elapsed time llm generation streaming: {el_time:.2f} seconds", flush=True)
                return self._create_llm_result(message_data, final_text_response)
