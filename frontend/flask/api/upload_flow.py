#!/usr/bin/env python
"""Upload raw media and slide files to backend """
__author__ = "Andreas Gerner"
__copyright__ = "Copyright 2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.1" # Version bumped
__status__ = "Draft"

import io
import json
from typing import List, Optional # MODIFICATION: Added Optional
from uuid import uuid4

from connectors.connector_provider import connector_provider
from connectors.config import get_hans_dag_output_connection_ids

from api.modules.metadata_provider import metadata_provider
from api.modules.responses import (
    UnauthorizedResponse,
    RefreshAuthenticationRequired,
    JsonResponse,
    ErrorResponse,
    ErrorForbidden,
    ErrorNotFound,
)
from api.modules.security import SecurityConfiguration, SecurityMetaData
from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field


upload_flow_api_bp = APIBlueprint(
    "upload_flow",
    __name__,
    abp_security=SecurityConfiguration().get_security(),
    abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
)

# --- Tags (unchanged) ---
my_lectures_tag = Tag(name="my lectures", description="Get lectures the current user has uploaded")
my_channels_tag = Tag(name="my channels", description="Get channels of the current user")
general_tag = Tag(name="update general", description="Update general information (title, summary)")
chapter_fragmentation_tag = Tag(
    name="update chapter fragmentation", description="Update fragmentation of chapters and regenerate their summaries"
)
chapters_tag = Tag(name="update chapters", description="Update title and summary of each chapter")
redo_tag = Tag(name="restart editing", description="Reset the editing progress to the first step")
delete_tag = Tag(name="delete video", description="Delete the uploaded video completely")
overwrite_edit_progress_tag = Tag(
    name="overwrite edit progress",
    description="Overwrtie edit status to finished to skip editing, dangerous as the questions and other content are not checked by a real person",
)
visibility_tag = Tag(name="change the visibility", description="Change the visibility of the selected video")


# --- MODIFICATION: Pydantic model updated for optional fields ---
class MediaItemsForChannel(BaseModel):
    """API template for retrieving media items. Channel filters are optional."""
    uuid: Optional[str] = Field(None, description="Optional: Uuid of the channel to filter by")
    course_acronym: Optional[str] = Field(None, description="Optional: Course acronym of the channel to filter by")


# --- MODIFICATION: Endpoint updated with conditional logic and new function call ---
@upload_flow_api_bp.get("/my-lectures", tags=[my_lectures_tag])
@jwt_required()
def get_own_lectures(query: MediaItemsForChannel):
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    if not sec_meta_data.check_identity_is_valid():
        return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin", "developer", "lecturer"]) or sec_meta_data.is_sso_user is True:
        return ErrorForbidden.create()

    if query.uuid and query.course_acronym:
        # New behavior: Call with channel filters if provided
        media_items = metadata_provider.search_uploaded_media(
            sec_meta_data, 
            channel_uuid=query.uuid, 
            channel_course_acronym=query.course_acronym
        )
    else:
        # Original behavior: Call without filters to get all lectures for the user
        media_items = metadata_provider.search_uploaded_media(sec_meta_data)

    if not media_items:
        return ErrorNotFound.create_custom("No media items found")
        
    media_items_filtered = sec_meta_data.filter_media_results(media_items, False)
    if media_items_filtered is None:
        return ErrorForbidden.create()
        
    if len(media_items_filtered) > 1:
        media_items_sorted = sorted(media_items_filtered, key=lambda x: x["title"])
        return JsonResponse.create(media_items_sorted)
    else:
        return JsonResponse.create(media_items_filtered)



@upload_flow_api_bp.get("/my-channels", tags=[my_channels_tag])
@jwt_required()
def get_own_channels():
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    if not sec_meta_data.check_identity_is_valid():
        return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin", "developer", "lecturer"]) or sec_meta_data.is_sso_user is True:
        return ErrorForbidden.create()

    channel_items = metadata_provider.search_user_channels(sec_meta_data)
    if not channel_items:
        return ErrorNotFound.create_custom("No channel items found")
        
    channel_items_filtered = sec_meta_data.filter_channel_results(channel_items)
    if channel_items_filtered is None:
        return ErrorForbidden.create()
        
    if len(channel_items_filtered) > 1:
        channel_items_sorted = sorted(channel_items_filtered, key=lambda x: x["course_acronym"])
        return JsonResponse.create(channel_items_sorted)
    else:
        return JsonResponse.create(channel_items_filtered)


class GeneralRequest(BaseModel):
    uuid: str = Field(None, description="Identifier of the media item")
    title: str = Field(None, description="New title of the specified media item")
    language: str = Field(None, description="Spoken language identifier, supported identifiers: 'en', 'de'")
    short_summary: str = Field(None, description="New short summary for the specified media item")
    summary: str = Field(None, description="New summary for the specified media item")


@upload_flow_api_bp.put("/general", tags=[general_tag])
@jwt_required()
def put_summary(body: GeneralRequest):
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    if not sec_meta_data.check_identity_is_valid():
        return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin", "developer", "lecturer"]) or sec_meta_data.is_sso_user is True:
        return ErrorForbidden.create()

    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()

    urn_meta_data = f"metadb:meta:post:id:{body.uuid}"
    meta_data = mongo_connector.get_metadata(urn_meta_data)

    meta_data["title"] = body.title

    short_summary_urn = meta_data["short_summary_result_de" if body.language == "de" else "short_summary_result_en"]
    save_to_summary_file(short_summary_urn, body.language, body.short_summary)

    summary_urn = meta_data["summary_result_de" if body.language == "de" else "summary_result_en"]
    save_to_summary_file(summary_urn, body.language, body.summary)

    if body.language == "de":
        translation_connector = connector_provider.get_translation_connector()
        if not translation_connector.connect():
            return ErrorResponse.create_custom("Error while connecting to translation service!")

        result = translation_connector.post_raw_translations("de", "en", [body.short_summary, body.summary])
        short_summary = result[0]
        summary = result[1]

        short_summary_urn = meta_data["short_summary_result_en"]
        save_to_summary_file(short_summary_urn, "en", short_summary)

        summary_urn = meta_data["summary_result_en"]
        save_to_summary_file(summary_urn, "en", summary)

    meta_data["state"]["overall_step"] = "EDITING"
    meta_data["state"]["editing_progress"] = 1 if body.language == "de" else 2

    mongo_connector.put_object(urn_meta_data, None, "application/json", meta_data)
    return JsonResponse.create({"success": True})


def save_to_summary_file(summary_urn: str, language: str, content: str):
    assetdb_connector = connector_provider.get_assetdb_connector()
    assetdb_connector.connect()

    summary_result = assetdb_connector.get_object(summary_urn)
    summary_data = json.loads(summary_result.data)

    summary_data["result"][0]["summary"] = content
    summary_as_stream = io.BytesIO(json.dumps(summary_data).encode())
    assetdb_connector.put_object(
        summary_urn,
        summary_as_stream,
        "application/json",
        {"X-Amz-Meta-Filename": assetdb_connector.parse_urn(summary_urn)["item"], "X-Amz-Meta-Language": language},
    )


class Fragment(BaseModel):
    start: float = Field(None, description="Start of the chapter")
    stop: float = Field(None, description="Stop of the chapter")


class ChapterFragmentationRequest(BaseModel):
    uuid: str = Field(None, description="Identifier of the media item")
    data: List[Fragment] = Field(None, description="Fragments of each chapter")


@upload_flow_api_bp.put("/chapter-fragmentation", tags=[chapter_fragmentation_tag])
@jwt_required()
def put_chapter_fragmentation(body: ChapterFragmentationRequest):
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    if not sec_meta_data.check_identity_is_valid():
        return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin", "developer", "lecturer"]) or sec_meta_data.is_sso_user is True:
        return ErrorForbidden.create()
    print(f"chapter-fragmentation: New segmentation for uuid: {body.uuid}")

    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()

    urn_meta_data = f"metadb:meta:post:id:{body.uuid}"
    print(f"Get meta data from urn: {urn_meta_data}")
    meta_data = mongo_connector.get_metadata(urn_meta_data)
    if meta_data is None:
        return ErrorResponse.create_custom(f"Error while fetching meta data from urn {urn_meta_data}")

    transcript_en = metadata_provider.get_raw_transcript_for_media(body.uuid, "en")

    segments = [{"start": 0, "stop": 0, "text": ""}]
    current_fragment = 0
    for i in range(len(transcript_en)):
        sentence = transcript_en[i]
        if sentence["interval"][1] > body.data[current_fragment].stop:
            segments.append({"start": 0, "stop": 0, "text": ""})
            current_fragment += 1

        segments[current_fragment]["text"] += sentence["transcript_formatted"] + " "

    parsed_seg_len = len(segments)
    uploaded_seg_len = len(body.data)
    print(f"Segment length (parsed:uploaded): {parsed_seg_len}:{uploaded_seg_len}")

    if parsed_seg_len > uploaded_seg_len:
        do_count = parsed_seg_len - uploaded_seg_len
        for i in range(do_count):
            segments.pop(0)

    for i in range(len(segments)):
        segments[i]["start"] = body.data[i].start
        segments[i]["stop"] = body.data[i].stop

    topic_result_raw = {"type": "TopicResultRaw", "language": "en", "result": []}

    for i in range(len(segments)):
        segment = segments[i]
        topic_result_raw["result"].append(
            {"result_index": i, "interval": [segments[i]["start"], segments[i]["stop"]], "text": segment["text"]}
        )

    assetdb_connector = connector_provider.get_assetdb_connector()
    assetdb_connector.connect()
    gen_uuid = str(uuid4())
    asset_urn = f"assetdb:raw:{gen_uuid}.json"
    asset_as_stream = io.BytesIO(json.dumps(topic_result_raw).encode())

    filename = assetdb_connector.parse_urn(asset_urn)["item"]
    assetdb_connector.put_object(
        asset_urn, asset_as_stream, "application/json", {"X-Amz-Meta-Filename": filename, "X-Amz-Meta-Language": "en"}
    )

    meta_data["topic_result_raw_en"] = asset_urn
    meta_data["state"]["overall_step"] = "PROCESSING"
    meta_data["state"]["editing_progress"] = 2

    print(f"Update meta data with urn: {urn_meta_data}")
    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()
    (success, urn_result) = mongo_connector.put_object(urn_meta_data, None, "application/json", meta_data)
    if success is False:
        return ErrorResponse.create_custom(f"Error while stroing new meta data state on urn {urn_meta_data}")

    success = trigger_airflow_dag_chapter_sum(filename, gen_uuid, asset_urn, urn_meta_data)
    if success is False:
        return ErrorResponse.create_custom("Error while triggering airflow job")

    return JsonResponse.create({"success": True, "uuid": gen_uuid})

class TopicFragment(BaseModel):
    result_index: int = Field(None, description="Index of this result field")
    interval: List[float] = Field(None, description="Start/End timestamp of this fragment")
    title: str = Field(None, description="Title of this fragment")
    summary: str = Field(None, description="Summary of this fragment")


class TopicResult(BaseModel):
    type: str = Field(None, description="TopicResult")
    language: str = Field(None, description="Language of this result")
    result: List[TopicFragment] = Field(None, description="List of fragments")


class Answer(BaseModel):
    index: int = Field(None, description="Index of the answer")
    answer: str = Field(None, description="Answer text")


class MultipleChoiceQuestion(BaseModel):
    question: str = Field(None, description="Question text")
    correct_answer_index: int = Field(None, description="Index of the correct answer in answers list")
    correct_answer_explanation: str = Field(None, description="Explanation for the correct answer")
    creator: str = Field(None, description="Initial creator of the question, usually llm")
    editor: str = Field(None, description="Last editor of the question, usually lecturer")
    answers: List[Answer] = Field(None, description="List of answers")


class QuestionItem(BaseModel):
    type: str = Field(None, description="Question type, e.g. mcq_one_correct")
    index: int = Field(None, description="Index of the question")
    mcq: MultipleChoiceQuestion = Field(
        None, description="The real question, currently only multiple choice question with single correct answer"
    )


class QuestionnaireItem(BaseModel):
    easy: List[QuestionItem] = Field(None, description="List of easy questions")
    medium: List[QuestionItem] = Field(None, description="List of medium questions")
    difficult: List[QuestionItem] = Field(None, description="List of difficult questions")


class QuestionnaireResultItem(BaseModel):
    result_index: int = Field(None, description="Index of this result field")
    interval: List[float] = Field(None, description="Start/End timestamp of this fragment")
    questionnaire: QuestionnaireItem = Field(None, description="Title of this fragment")


class QuestionnaireResult(BaseModel):
    type: str = Field(None, description="QuestionnaireResult")
    language: str = Field(None, description="Language of this result")
    result: List[QuestionnaireResultItem] = Field(None, description="List of fragments")


class ChaptersRequest(BaseModel):
    uuid: str = Field(None, description="Identifier of the media item")
    topicResult: TopicResult = Field(None, description="New content of topic_result_en/topic_result_de")
    questionnaireResult: QuestionnaireResult = Field(
        None, description="New content of questionnaire_result_en/questionnaire_result_de"
    )


@upload_flow_api_bp.post("/chapters", tags=[chapters_tag])
@jwt_required()
def put_chapters(body: ChaptersRequest):
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    if not sec_meta_data.check_identity_is_valid():
        return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin", "developer", "lecturer"]) or sec_meta_data.is_sso_user is True:
        return ErrorForbidden.create()

    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()

    urn_meta_data = f"metadb:meta:post:id:{body.uuid}"
    meta_data = mongo_connector.get_metadata(urn_meta_data)

    print(f"meta_data: {urn_meta_data}")
    summary_urn = meta_data["topic_result_de" if body.topicResult.language == "de" else "topic_result_en"]
    print(f"Summary urn: {summary_urn}")
    questionnaire_urn = meta_data[
        "questionnaire_result_de" if body.questionnaireResult.language == "de" else "questionnaire_result_en"
    ]
    print(f"Questionnaire urn: {summary_urn}")

    summary_as_stream = io.BytesIO(body.topicResult.model_dump_json().encode())
    questionnaire_as_stream = io.BytesIO(body.questionnaireResult.model_dump_json().encode())

    assetdb_connector = connector_provider.get_assetdb_connector()
    assetdb_connector.connect()

    assetdb_connector.put_object(
        summary_urn,
        summary_as_stream,
        "application/json",
        {
            "X-Amz-Meta-Filename": assetdb_connector.parse_urn(summary_urn)["item"],
            "X-Amz-Meta-Language": body.topicResult.language,
        },
    )
    print(f"Put summary urn: {summary_urn}")

    assetdb_connector.put_object(
        questionnaire_urn,
        questionnaire_as_stream,
        "application/json",
        {
            "X-Amz-Meta-Filename": assetdb_connector.parse_urn(questionnaire_urn)["item"],
            "X-Amz-Meta-Language": body.questionnaireResult.language,
        },
    )
    print(f"Put questionnaire urn: {questionnaire_urn}")

    if body.topicResult.language == "de":
        topic_gen_uuid = str(uuid4())
        topic_asset_urn = f"assetdb:raw:{topic_gen_uuid}.json"
        topic_asset_as_stream = io.BytesIO(json.dumps(body.topicResult.model_dump()).encode())
        topic_filename = assetdb_connector.parse_urn(topic_asset_urn)["item"]
        assetdb_connector.put_object(
            topic_asset_urn,
            topic_asset_as_stream,
            "application/json",
            {"X-Amz-Meta-Filename": topic_filename, "X-Amz-Meta-Language": "de"},
        )
        questionnaire_gen_uuid = str(uuid4())
        questionnaire_asset_urn = f"assetdb:raw:{questionnaire_gen_uuid}.json"
        questionnaire_asset_as_stream = io.BytesIO(json.dumps(body.questionnaireResult.model_dump()).encode())
        questionnaire_filename = assetdb_connector.parse_urn(questionnaire_asset_urn)["item"]
        assetdb_connector.put_object(
            questionnaire_asset_urn,
            questionnaire_asset_as_stream,
            "application/json",
            {"X-Amz-Meta-Filename": questionnaire_filename, "X-Amz-Meta-Language": "de"},
        )
        success = trigger_airflow_dag_translate_topics_quests(
            str(uuid4()),
            urn_meta_data,
            topic_asset_urn,
            topic_filename,
            questionnaire_asset_urn,
            questionnaire_filename,
        )
        if success is False:
            return ErrorResponse.create_custom("Error while triggering airflow job")

    if body.topicResult.language == "de":
        meta_data["state"]["overall_step"] = "PROCESSING"
        meta_data["state"]["editing_progress"] = 3
    else:
        meta_data["state"]["overall_step"] = "FINISHED"
        meta_data["state"]["editing_progress"] = 0
        meta_data["questionnaire_curated"] = True

    mongo_connector.connect()
    mongo_connector.put_object(urn_meta_data, None, "application/json", meta_data)
    print(f"Put final meta data update on urn: {urn_meta_data}")
    return JsonResponse.create({"success": True})


class OverwriteEditProgressRequest(BaseModel):
    uuid: str = Field(None, description="Identifier of the media item")


@upload_flow_api_bp.post("/overwriteEditProgress", tags=[overwrite_edit_progress_tag])
@jwt_required()
def overwrite_edit_progress(body: OverwriteEditProgressRequest):
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    if not sec_meta_data.check_identity_is_valid():
        return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin", "lecturer"]) or sec_meta_data.is_sso_user is True:
        return ErrorForbidden.create()

    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()

    urn_meta_data = f"metadb:meta:post:id:{body.uuid}"
    meta_data = mongo_connector.get_metadata(urn_meta_data)
    meta_data["state"]["overall_step"] = "FINISHED"
    meta_data["state"]["editing_progress"] = 0
    meta_data["questionnaire_curated"] = False
    mongo_connector.connect()
    mongo_connector.put_object(urn_meta_data, None, "application/json", meta_data)
    print(f"Overwrite edit progress meta data on urn: {urn_meta_data}")
    return JsonResponse.create({"success": True})


class RedoRequest(BaseModel):
    uuid: str = Field(None, description="Identifier of the media item")


@upload_flow_api_bp.post("/redo", tags=[redo_tag])
@jwt_required()
def post_restart_editing(body: RedoRequest):
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    if not sec_meta_data.check_identity_is_valid():
        return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin", "developer", "lecturer"]) or sec_meta_data.is_sso_user is True:
        return ErrorForbidden.create()

    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()

    urn_meta_data = f"metadb:meta:post:id:{body.uuid}"
    meta_data = mongo_connector.get_metadata(urn_meta_data)

    meta_data["state"]["overall_step"] = "EDITING"
    meta_data["state"]["editing_progress"] = 0
    meta_data["state"]["published"] = False
    meta_data["state"]["listed"] = False

    mongo_connector.put_object(urn_meta_data, None, "application/json", meta_data)
    return JsonResponse.create({"success": True})


class DeleteRequest(BaseModel):
    uuid: str = Field(None, description="Identifier of the media item")


@upload_flow_api_bp.post("/delete", tags=[delete_tag])
@jwt_required()
def delete_item(body: DeleteRequest):
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    if not sec_meta_data.check_identity_is_valid():
        return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin"]):
        return ErrorForbidden.create()

    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()

    urn_meta_data = f"metadb:meta:post:id:{body.uuid}"
    meta_data = mongo_connector.get_metadata(urn_meta_data)

    mongo_connector.remove_metadata(urn_meta_data)

    values = list(meta_data.values())
    assets = [urn for urn in values if isinstance(urn, str) and urn.startswith("assetdb")]
    medias = [urn for urn in values if isinstance(urn, str) and urn.startswith("mediadb")]

    assetdb_connector = connector_provider.get_assetdb_connector()
    assetdb_connector.connect()

    for asset in assets:
        print(f"deleting {asset}")
        assetdb_connector.delete_object_by_urn(asset)

    mediadb_connector = connector_provider.get_mediadb_connector()
    mediadb_connector.connect()

    for media in medias:
        print(f"deleting {media}")
        [_, bucket, urn] = media.split(":")
        [folder_name, _] = urn.split("/")
        assetdb_connector.delete_folder_in_bucket(bucket, folder_name)

    opensearch_connector = connector_provider.get_opensearch_connector()
    opensearch_connector.connect()

    opensearch_connector.delete_lecture_document(meta_data["uuid"])

    return JsonResponse.create({"success": True})


class VisibilityRequest(BaseModel):
    uuid: str = Field(None, description="Identifier of the media item")
    published: bool = Field(None, description="New published state of the media item")
    listed: bool = Field(None, description="New listed state of the media item")


def publish_on_searchengine(assetdb_connector, opensearch_connector, metadb_uuid, urn):
    """Load search engine search_data.json from assetdb and publish on search engine"""
    print("Search data urn: " + urn)
    search_data_response = assetdb_connector.get_object(urn)
    if "500 Internal Server Error" in search_data_response.data.decode("utf-8"):
        return ErrorResponse.create_custom("Error while fetching search data from assetdb!")
    print("Adding search data for uuid " + metadb_uuid)
    search_data = json.loads(search_data_response.data)
    opensearch_connector.insert_lecture_document(id=metadb_uuid, json_data=search_data)
    return True


def publish_vectors_on_searchengine(assetdb_connector, opensearch_connector, metadb_uuid, urn, index):
    """Load search engine search_data_vectors.json from assetdb and publish on search engine"""
    print("Search data vectors urn: " + urn)
    search_data_response = assetdb_connector.get_object(urn)
    if "500 Internal Server Error" in search_data_response.data.decode("utf-8"):
        return ErrorResponse.create_custom("Error while fetching search data vectors from assetdb!")
    print(f"Adding search data vectors in index {index} for uuid {metadb_uuid}")
    search_data_vectors = json.loads(search_data_response.data)
    for n, vector_data in enumerate(search_data_vectors):
        chunk_id = f"{metadb_uuid}__{n:05d}"
        opensearch_connector.insert_lecture_vector_entry(
            lecture_id=metadb_uuid, chunk_id=chunk_id, json_data=vector_data, index=index
        )
    return True


def publish_slides_vectors_on_searchengine(assetdb_connector, opensearch_connector, metadb_uuid, urn, index):
    """Load search engine search_data_vectors.json from assetdb and publish on search engine"""
    urn_bucket_folder = urn.rsplit("/")[0]
    print("Search data slides vectors base urn: " + urn_bucket_folder)
    images_slides_data_files = assetdb_connector.list_objects(urn_bucket_folder)
    sorted_slides_data_files = []
    for obj in images_slides_data_files:
        filepath = str(obj.object_name)
        name_with_fext = filepath.split("/", maxsplit=1)[-1]
        if (
            name_with_fext.endswith(".json")
            and not name_with_fext.endswith(".meta.json")
            and not name_with_fext.endswith("slides.meta.json")
        ):
            sorted_slides_data_files.append(name_with_fext)
    sorted_slides_data_files = sorted(sorted_slides_data_files, key=lambda x: int(x.split(".")[0]))
    print(f"Adding search data vectors in index {index} for uuid {metadb_uuid}")
    for n, name_with_fext in enumerate(sorted_slides_data_files):
        download_urn = urn_bucket_folder + "/" + name_with_fext
        print(f"Adding slides vector from {download_urn}")
        img_vector_data = assetdb_connector.get_object(download_urn)
        if "500 Internal Server Error" in img_vector_data.data.decode("utf-8"):
            return ErrorResponse.create_custom("Error while fetching search data slides vectors from assetdb!")
        img_vector_json = json.loads(img_vector_data.data)
        chunk_id = f"{metadb_uuid}__{n:05d}"
        opensearch_connector.insert_lecture_vector_entry(
            lecture_id=metadb_uuid, chunk_id=chunk_id, json_data=img_vector_json, index=index
        )
    return True


def publish_summary_vectors_on_searchengine(assetdb_connector, opensearch_connector, metadb_uuid, urn, index):
    """Load search engine search_data_vectors.json from assetdb and publish on search engine"""
    print("Search summary data vectors urn: " + urn)
    search_data_response = assetdb_connector.get_object(urn)
    if "500 Internal Server Error" in search_data_response.data.decode("utf-8"):
        return ErrorResponse.create_custom("Error while fetching search summary data vectors from assetdb!")
    print(f"Adding search summary data vector in index {index} for uuid {metadb_uuid}")
    summary_vector_data = json.loads(search_data_response.data)
    opensearch_connector.insert_lecture_vector_entry(
        lecture_id=metadb_uuid, chunk_id=None, json_data=summary_vector_data, index=index
    )
    return True


@upload_flow_api_bp.put("/visibility", tags=[visibility_tag])
@jwt_required()
def put_new_visibility(body: VisibilityRequest):
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    if not sec_meta_data.check_identity_is_valid():
        return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin", "developer", "lecturer"]) or sec_meta_data.is_sso_user is True:
        return ErrorForbidden.create()

    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()
    opensearch_connector = connector_provider.get_opensearch_connector()
    opensearch_connector.connect()
    assetdb_connector = connector_provider.get_assetdb_connector()
    assetdb_connector.connect()

    urn_meta_data = f"metadb:meta:post:id:{body.uuid}"
    meta_data = mongo_connector.get_metadata(urn_meta_data)

    meta_data["state"]["published"] = body.published
    meta_data["state"]["listed"] = body.listed

    (success, item) = mongo_connector.put_object(urn_meta_data, None, "application/json", meta_data)
    if not success:
        print("Error changing media item published state!")
        return JsonResponse.create({"success": False})
    if body.published is True:
        if "search_data_vectors" in meta_data:
            search_data_vectors_result = publish_vectors_on_searchengine(
                assetdb_connector,
                opensearch_connector,
                meta_data["uuid"],
                meta_data["search_data_vectors"],
                index=opensearch_connector.vector_index,
            )
            if search_data_vectors_result is False:
                return ErrorResponse.create_custom("Error publishing search engine vector data!")
        if "slides_images_meta" in meta_data:
            search_slides_data_vectors_result = publish_slides_vectors_on_searchengine(
                assetdb_connector,
                opensearch_connector,
                meta_data["uuid"],
                meta_data["slides_images_meta"],
                index=opensearch_connector.slides_vector_index,
            )
            if search_slides_data_vectors_result is False:
                return ErrorResponse.create_custom("Error publishing search engine slides vector data!")
        if "search_summary_data_vector" in meta_data:
            search_summary_data_vector_result = publish_summary_vectors_on_searchengine(
                assetdb_connector,
                opensearch_connector,
                meta_data["uuid"],
                meta_data["search_summary_data_vector"],
                index=opensearch_connector.summaries_vector_index,
            )
            if search_summary_data_vector_result is False:
                return ErrorResponse.create_custom("Error publishing search engine summary vector data!")
    else:
        del_uuid = meta_data["uuid"]
        del_vect_res = opensearch_connector.delete_all_vector_entries_of_lecture(del_uuid)
        if del_vect_res is False:
            print(
                f"Warning: Could not delete search engine vector data maybe media item not indexed! Media item uuid: {del_uuid}"
            )

    if body.listed is True:
        if "search_data" in meta_data:
            search_data_result = publish_on_searchengine(
                assetdb_connector, opensearch_connector, meta_data["uuid"], meta_data["search_data"]
            )
            if search_data_result is False:
                return ErrorResponse.create_custom("Error publishing search engine data!")
    else:
        del_uuid = meta_data["uuid"]
        del_lecture_res = opensearch_connector.delete_lecture_document(del_uuid)
        if del_lecture_res is False:
            print(
                f"Warning: Could not delete search engine data maybe media item not indexed! Media item uuid: {del_uuid}"
            )

    return JsonResponse.create({"success": True})


def trigger_airflow_dag_chapter_sum(filename, uuid, media_urn, meta_urn):
    """Helper to trigger ml-backend airflow job"""
    hans_type = "topic_result_raw"

    annotation_task_config = {
        "metaUrn": meta_urn,
        "input": [
            {
                "urn": media_urn,
                "filename": filename,
                "mime-type": "application/json",
                "hans-type": hans_type,
                "locale": "en",
            }
        ],
        "output": [get_hans_dag_output_connection_ids()],
    }
    airflow_connector = connector_provider.get_airflow_connector()
    airflow_connector.connect()
    return airflow_connector.post_dag_run("chapter_sum_v1.0.0", uuid, annotation_task_config)


def trigger_airflow_dag_translate_topics_quests(
    uuid, meta_urn, topic_urn, topic_filename, questionnaire_urn, questionnaire_filename
):
    """Helper to trigger ml-backend airflow job"""
    annotation_task_config = {
        "metaUrn": meta_urn,
        "input": [
            {
                "urn": topic_urn,
                "filename": topic_filename,
                "mime-type": "application/json",
                "hans-type": "topic_result_de",
                "locale": "de",
            },
            {
                "urn": questionnaire_urn,
                "filename": questionnaire_filename,
                "mime-type": "application/json",
                "hans-type": "questionnaire_result_de",
                "locale": "de",
            },
        ],
        "output": [get_hans_dag_output_connection_ids()],
    }
    airflow_connector = connector_provider.get_airflow_connector()
    airflow_connector.connect()
    return airflow_connector.post_dag_run("translate_topics_quests_v1.0.0", uuid, annotation_task_config)