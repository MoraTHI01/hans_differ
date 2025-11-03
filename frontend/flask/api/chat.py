#!/usr/bin/env python
"""Provide chat based on llm provided by hans ml services
See:
https://luolingchun.github.io/flask-openapi3/v2.x/Usage/Request/#body
https://luolingchun.github.io/flask-openapi3/v2.x/Quickstart/#async-api
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import json
import re
from flask import Flask, Response, stream_with_context
from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field

from api.modules.metadata_provider import metadata_provider
from api.modules.connectors.connector_provider import connector_provider
from api.modules.responses import ErrorForbidden, ErrorNotFound, UnauthorizedResponse, RefreshAuthenticationRequired
from api.modules.responses import ErrorResponse, JsonResponse
from api.modules.security import SecurityConfiguration, SecurityMetaData
from api.modules.message import Message
from api.modules.schema import MultipleChoiceQuestion


chat_api_bp = APIBlueprint(
    "chat",
    __name__,
    abp_security=SecurityConfiguration().get_security(),
    abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
)

ml_services_status_tag = Tag(name="Check ml services status", description="Check status of hans ml services")

ml_services_info_tag = Tag(name="Fetch ml services info", description="Fetch info of hans ml services")

message_request_tag = Tag(name="Request message", description="Message request to hans ml services")
message_stream_request_tag = Tag(
    name="Request message and stream server sent events",
    description="Message request to hans ml services, response with server sent events",
)
message_request_multiple_choice_question_tag = Tag(
    name="Request multiple choice question",
    description="Message request to hans ml services for a multiple choice question",
)


class MessageRequest(BaseModel):
    """API template for retrieving media metadata"""

    uuid: str = Field(None, description="UUID of message")
    data: Message = Field(None, description="Message object")


# REQUESTS FROM FRONTEND


@chat_api_bp.post("/adaptMessageContext", tags=[message_request_tag])
@jwt_required()
def message_adapt_context(body: MessageRequest):
    """Adapt message context"""
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    # Protect api from access of airflow ml-backend users
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    # Context is empty so do vector search
    ending = "\\n"
    con_len = len(body.data.context)
    if con_len < 1 or (con_len > 1 and "- [1]" in body.data.context):
        # Connect to embedding connector and embed user query to vector
        embedding_connector = connector_provider.get_embedding_connector()
        if not embedding_connector.connect():
            return ErrorResponse.create_custom("Error while connecting to text embedding service!")
        query_vector = embedding_connector.post_embedding(body.data)

        # Connect to opensearch connector and get most similar text chunks for user query
        opensearch_connector = connector_provider.get_opensearch_connector()
        if not opensearch_connector.connect():
            return ErrorResponse.create_custom("Error while connecting to text opensearch service!")
        lecture_id = body.data.contextUuid
        search_results = opensearch_connector.vector_search_in_specific_lectures(
            query_vector, lecture_ids=[lecture_id], num_results=4
        )
        slides_vector_index = opensearch_connector.slides_vector_index
        search_results_images = opensearch_connector.vector_search_in_specific_lectures(
            query_vector, lecture_ids=[lecture_id], num_results=4, index=slides_vector_index
        )

        final_text = ""
        skip_other_images = False
        if body.data.useVision is True or body.data.useVisionSnapshot is True:
            media_item = metadata_provider.get_media_metadata(body.data.contextUuid, "uuid")
            assetdb_connector = connector_provider.get_assetdb_connector()
            assetdb_connector.connect()
            vllm_connector = connector_provider.get_vllm_connector()
            if not vllm_connector.connect():
                return ErrorResponse.create_custom("Error while connecting to vllm webservice!")
            (image_context_str, _) = vllm_connector.gen_image_context(body.data, assetdb_connector, media_item)
            if len(image_context_str) > 0:
                final_text = image_context_str
                skip_other_images = True

        # Prepare response, incl. retrieved texts with citation hints []
        if skip_other_images is False:
            for n, search_res in enumerate(search_results):
                text = search_res["text"].strip()
                final_text += f" - [{str(n)}] {text} {ending}"
            for n, search_res in enumerate(search_results_images):
                text = search_res["text"].strip()
                # use real pagenumber derived from chunk index to find and load slide in frontend vue
                page = str(search_res["chunk_index"] + 1 + 100)
                final_text += f" - [{page}] {text} {ending}"
        final_message = body.data.model_dump()
        final_message["context"] = final_text
        result = {"data": [{"type": "RetrievalResult", "result": [final_message]}]}
        # print(json.dumps(result))
        return JsonResponse.create_json_string_response(json.dumps(result))
    else:
        # Context is not empty use selected context
        final_message = body.data.model_dump()
        curr_context = body.data.context.strip()
        final_message["context"] = f" - [0] {curr_context} {ending}"
        result = {"data": [{"type": "RetrievalResult", "result": [final_message]}]}
        # print(json.dumps(result))
        return JsonResponse.create_json_string_response(json.dumps(result))


@chat_api_bp.post("/translateMessage", tags=[message_request_tag])
@jwt_required()
def message_translate(body: MessageRequest):
    """Translate a message"""
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    # Protect api from access of airflow ml-backend users
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    translation_connector = connector_provider.get_translation_connector()
    if not translation_connector.connect():
        return ErrorResponse.create_custom("Error while connecting to translation service!")
    result = translation_connector.post_translation(body.data)
    print("TranslationResult")
    if result is None:
        return ErrorResponse.create_custom("Error while parsing message content for translation service!")
    # print(json.dumps(result))
    return JsonResponse.create_json_string_response(json.dumps(result))


@chat_api_bp.post("/sendMessage", tags=[message_request_tag])
@jwt_required()
def message_send(body: MessageRequest):
    """Fetch markers of urn and provide to vue"""
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    # Protect api from access of airflow ml-backend users
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    if body.data.useVision is True or body.data.useVisionSnapshot is True:
        media_item = metadata_provider.get_media_metadata(body.data.contextUuid, "uuid")
        assetdb_connector = connector_provider.get_assetdb_connector()
        assetdb_connector.connect()
        vllm_connector = connector_provider.get_vllm_connector()
        if not vllm_connector.connect():
            return ErrorResponse.create_custom("Error while connecting to vllm webservice!")
        result = vllm_connector.post_vllm(body.data, assetdb_connector, media_item)
        print("VLlmResult")
    else:
        llm_connector = connector_provider.get_llm_connector()
        if not llm_connector.connect():
            return ErrorResponse.create_custom("Error while connecting to llm webservice!")
        # print(json.dumps(llm_connector.get_info()))
        result = llm_connector.post_llm(body.data)
        print("LlmResult")
    # print(json.dumps(result))
    return JsonResponse.create_json_string_response(json.dumps(result))


@chat_api_bp.post("/sendMessageStream", tags=[message_stream_request_tag])
@jwt_required()
def message_send_stream(body: MessageRequest):
    """Fetch markers of urn and provide to vue"""
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    # Protect api from access of airflow ml-backend users
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    if body.data.useVision is True or body.data.useVisionSnapshot is True:
        media_item = metadata_provider.get_media_metadata(body.data.contextUuid, "uuid")
        assetdb_connector = connector_provider.get_assetdb_connector()
        assetdb_connector.connect()
        vllm_connector = connector_provider.get_vllm_connector()
        if not vllm_connector.connect():
            return ErrorResponse.create_custom("Error while connecting to vllm webservice!")
        return Response(
            stream_with_context(vllm_connector.post_vllm_stream(body.data, assetdb_connector, media_item)),
            content_type="text/event-stream",
        )
    else:
        llm_connector = connector_provider.get_llm_connector()
        if not llm_connector.connect():
            return ErrorResponse.create_custom("Error while connecting to llm webservice!")
        return Response(stream_with_context(llm_connector.post_llm_stream(body.data)), content_type="text/event-stream")


@chat_api_bp.post("/sendMultipleChoiceQuestionRequest", tags=[message_request_multiple_choice_question_tag])
@jwt_required()
def message_multiple_choice_question_request(body: MessageRequest):
    """Fetch markers of urn and provide to vue"""
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    # Protect api from access of airflow ml-backend users
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    llm_connector = connector_provider.get_llm_connector()
    if not llm_connector.connect():
        return ErrorResponse.create_custom("Error while connecting to llm webservice!")
    # print(json.dumps(llm_connector.get_info()))
    result = llm_connector.post_llm(body.data, MultipleChoiceQuestion.model_json_schema())
    print("LlmMultipleChoiceQuestionResult")
    # print(json.dumps(result))
    return JsonResponse.create_json_string_response(json.dumps(result))


@chat_api_bp.get("/ml-service-status", tags=[ml_services_status_tag])
@jwt_required()
def get_status():
    """Fetch ml service status and provide to vue"""
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    # Protect api from access of airflow ml-backend users
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    # Disabled: Protect api from access of everybody, only the following roles are allowed:
    # if not sec_meta_data.check_user_has_roles(["admin", "developer", "lecturer"]):
    #    return ErrorForbidden.create()
    llm_connector = connector_provider.get_llm_connector()
    vllm_connector = connector_provider.get_vllm_connector()
    translation_connector = connector_provider.get_translation_connector()
    embedding_connector = connector_provider.get_embedding_connector()
    request_llm_service = llm_connector.request_service()
    request_vllm_service = vllm_connector.request_service()
    request_translation_service = translation_connector.request_service()
    request_embedding_service = embedding_connector.request_service()
    if (request_llm_service or request_vllm_service) and request_translation_service and request_embedding_service:
        result = {"status": "RUNNING"}
    else:
        result = {"status": "STARTUP"}
    return JsonResponse.create_json_string_response(json.dumps(result))


@chat_api_bp.get("/ml-service-info", tags=[ml_services_info_tag])
@jwt_required()
def get_info():
    """Fetch ml service info and provide to vue"""
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    if not sec_meta_data.check_identity_is_valid():
        return UnauthorizedResponse.create()
    # Protect api from access of airflow ml-backend users
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    llm_connector = connector_provider.get_llm_connector()
    llm_info = llm_connector.get_info()
    vllm_connector = connector_provider.get_vllm_connector()
    vllm_info = vllm_connector.get_info()
    translation_connector = connector_provider.get_translation_connector()
    translation_info = translation_connector.get_info()
    embedding_connector = connector_provider.get_embedding_connector()
    embedding_info = embedding_connector.get_info()
    info_result = {
        "type": "MLServiceInfoResult",
        "services": [
            {"type": "llm", "result_index": 0, "info": llm_info},
            {"type": "vllm", "result_index": 1, "info": vllm_info},
            {"type": "embedding", "result_index": 2, "info": embedding_info},
            {"type": "translation", "result_index": 3, "info": translation_info},
        ],
    }

    return JsonResponse.create_json_string_response(json.dumps(info_result))
