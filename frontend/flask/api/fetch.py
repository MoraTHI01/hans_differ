#!/usr/bin/env python
"""Fetch data from backend """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import json

from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from urllib.parse import unquote

from api.modules.metadata_provider import metadata_provider
from api.modules.connectors.connector_provider import connector_provider
from api.modules.connectors.minio_connector import MinioConnectorFetchUrlMode
from api.modules.responses import ErrorForbidden, ErrorNotFound, UnauthorizedResponse, RefreshAuthenticationRequired
from api.modules.responses import ErrorResponse, JsonResponse
from api.modules.security import SecurityConfiguration, SecurityMetaData


fetch_api_bp = APIBlueprint(
    "fetch",
    __name__,
    abp_security=SecurityConfiguration().get_security(),
    abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
)

media_tag = Tag(name="get media metadata", description="Provides metadata for a specific media item")


class MediaQuery(BaseModel):
    """API template for retrieving media metadata"""

    uuid: str = Field(None, description="Uuid of the media item")


marker_tag = Tag(name="marker for media", description="Provides marker for a specific media item")


class MarkerQuery(BaseModel):
    """API template for retrieving markers"""

    uuid: str = Field(None, description="Uuid of the media item")


transcript_tag = Tag(name="transcript for media", description="Provides transcript for a specific media item")


class TranscriptQuery(BaseModel):
    """API template for retrieving transcript"""

    uuid: str = Field(None, description="Uuid of the media item")


asr_results_tag = Tag(name="asr results for media", description="Provides asr results for a specific media item")


class AsrResultsQuery(BaseModel):
    """API template for retrieving asr results"""

    uuid: str = Field(None, description="Uuid of the media item")


transcript_results_tag = Tag(
    name="transcript results for media", description="Provides transcript results for a specific media item"
)


class TranscriptResultsQuery(BaseModel):
    """API template for retrieving asr results"""

    uuid: str = Field(None, description="Uuid of the media item")


short_summary_tag = Tag(name="short summary for media", description="Provides short summary for a specific media item")


class ShortSummaryQuery(BaseModel):
    """API template for retrieving short summary"""

    uuid: str = Field(None, description="Uuid of the media item")


summary_tag = Tag(name="summary for media", description="Provides summary for a specific media item")


class SummaryQuery(BaseModel):
    """API template for retrieving summary"""

    uuid: str = Field(None, description="Uuid of the media item")


search_trie_tag = Tag(name="search trie for media", description="Provides search trie for a specific media item")
search_trie_slides_tag = Tag(
    name="search trie for slides", description="Provides search trie for the slides of a specific media item"
)


class SearchTrieQuery(BaseModel):
    """API template for retrieving search trie"""

    uuid: str = Field(None, description="Uuid of the media item")


topics_tag = Tag(name="topics for media", description="Provides topics for a specific media item")


class TopicsQuery(BaseModel):
    """API template for retrieving topics"""

    uuid: str = Field(None, description="Uuid of the media item")


thumbnail_tag = Tag(name="Thumbnail for media", description="Provides thumbnail url for a specific urn")


class ThumbnailQuery(BaseModel):
    """API template for retrieving topics"""

    urn: str = Field(None, description="Urn of the thumbnail item")


questionnaire_tag = Tag(name="questionnaire for media", description="Provides questionnaire for a specific media item")


class QuestionnaireQuery(BaseModel):
    """API template for retrieving questionnaire"""

    uuid: str = Field(None, description="Uuid of the media item")


slides_images_meta_tag = Tag(
    name="slides images meta data for media", description="Provides slides images meta data for a specific media item"
)


class SlidesImagesMetaQuery(BaseModel):
    """API template for retrieving slides images meta data"""

    uuid: str = Field(None, description="Uuid of the media item")


keywords_tag = Tag(name="keywords data for media", description="Provides keywords data for a specific media item")


class KeywordsQuery(BaseModel):
    """API template for retrieving keywords data"""

    uuid: str = Field(None, description="Uuid of the media item")


url_tag = Tag(
    name="generate url for ml-backend for a specfic urn",
    description="Provides a URL for a specfic urn to the ml-backend",
)


class UrlQuery(BaseModel):
    """API template for retrieving url"""

    urn: str = Field(None, description="URN of the media item")
    mode: str = Field(None, description="Mode of the url, 'upload' or 'download'")


metadata_tag = Tag(
    name="download meta data for ml-backend for a specfic urn",
    description="Provides a meta data for a specfic urn to the ml-backend",
)


class MetaDataQuery(BaseModel):
    """API template for retrieving meta data"""

    urn: str = Field(None, description="URN of the metadb item")


upload_url_tag = Tag(
    name="upload url for ml-backend for a specfic urn",
    description="Provides a upload URL for a specfic urn to the ml-backend",
)


class UploadUrlQuery(BaseModel):
    """API template for retrieving upload url"""

    urn: str = Field(None, description="URN of the media item")


# REQUESTS FROM FRONTEND


@fetch_api_bp.get("/getMedia", tags=[media_tag])
@jwt_required()
def get_media(query: MediaQuery):
    """Fetch metadata of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    print("GetMedia")
    media_item = metadata_provider.get_metadata_by_uuid(query.uuid, "uuid")
    if not media_item:
        return ErrorNotFound.create_custom("Media item not found")
    # Should return empty list if user is not in the role to access the video
    media_item_filtered = sec_meta_data.filter_media_results([media_item])
    if media_item_filtered is None or len(media_item_filtered) < 1:
        return ErrorForbidden.create()
    return JsonResponse.create(media_item_filtered)


@fetch_api_bp.get("/getMarker", tags=[marker_tag])
@jwt_required()
def get_marker(query: MarkerQuery):
    """Fetch markers of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    markers = metadata_provider.get_markers_for_media(query.uuid)
    return JsonResponse.create_json_string_response(markers)


@fetch_api_bp.get("/getTranscript", tags=[transcript_tag])
@jwt_required()
def get_transcript(query: TranscriptQuery):
    """Fetch transcript of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    transcript = metadata_provider.get_transcript_for_media(query.uuid)
    return JsonResponse.create_json_string_response(transcript)


@fetch_api_bp.get("/getAsrResults", tags=[asr_results_tag])
@jwt_required()
def get_asr_results(query: AsrResultsQuery):
    """Fetch asr results of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    asr_results = metadata_provider.get_asr_results_for_media(query.uuid)
    print("AsrResults")
    # print(json.dumps(asr_results))
    return JsonResponse.create_json_string_response(json.dumps(asr_results))


@fetch_api_bp.get("/getTranscriptResults", tags=[transcript_results_tag])
@jwt_required()
def get_transcript_results(query: TranscriptResultsQuery):
    """Fetch transcript results of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    asr_results = metadata_provider.get_transcript_results_for_media(query.uuid)
    print("TranscriptResults")
    # print(json.dumps(asr_results))
    return JsonResponse.create_json_string_response(json.dumps(asr_results))


@fetch_api_bp.get("/getShortSummary", tags=[short_summary_tag])
@jwt_required()
def get_short_summary(query: ShortSummaryQuery):
    """Fetch short summary of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    short_summary = metadata_provider.get_short_summary_for_media(query.uuid)
    print("ShortSummaryResult")
    return JsonResponse.create(short_summary)


@fetch_api_bp.get("/getSearchTrie", tags=[search_trie_tag])
@jwt_required()
def get_search_trie(query: SearchTrieQuery):
    """Fetch short summary of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    search_trie_result = metadata_provider.get_search_trie_for_media(query.uuid)
    print("SearchTrieResult")
    # print(json.dumps(search_trie_result))
    return JsonResponse.create_json_string_response(json.dumps(search_trie_result))


@fetch_api_bp.get("/getSearchTrieSlides", tags=[search_trie_slides_tag])
@jwt_required()
def get_search_trie_slides(query: SearchTrieQuery):
    """Fetch short summary of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    search_trie_result = metadata_provider.get_search_trie_slides_for_media(query.uuid)
    print("SearchTrieSlidesResult")
    # print(json.dumps(search_trie_result))
    return JsonResponse.create_json_string_response(json.dumps(search_trie_result))


@fetch_api_bp.get("/getSummary", tags=[summary_tag])
@jwt_required()
def get_summary(query: SummaryQuery):
    """Fetch summary of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    summary = metadata_provider.get_summary_for_media(query.uuid)
    return JsonResponse.create(summary)


@fetch_api_bp.get("/getTopics", tags=[topics_tag])
@jwt_required()
def get_topics(query: TopicsQuery):
    """Fetch topics of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    topics = metadata_provider.get_topics_for_media(query.uuid)
    return JsonResponse.create(topics)


@fetch_api_bp.get("/getThumbnail", tags=[thumbnail_tag])
@jwt_required()
def get_thumbnail_url(query: ThumbnailQuery):
    """Get thumbnail url for thumbnail urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    result = metadata_provider.get_thumbnail_url_from_urn(query.urn)
    return JsonResponse.create_json_string_response(json.dumps(result))


@fetch_api_bp.get("/getQuestionnaire", tags=[questionnaire_tag])
@jwt_required()
def get_questionnaire_results(query: QuestionnaireQuery):
    """Fetch questionnaire results of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    questionnaire_results = metadata_provider.get_questionnaire_for_media(query.uuid)
    return JsonResponse.create(questionnaire_results)


@fetch_api_bp.get("/getSlidesImagesMeta", tags=[slides_images_meta_tag])
@jwt_required()
def get_slides_images_meta_results(query: SlidesImagesMetaQuery):
    """Fetch slides images meta results of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    slides_images_meta_results = metadata_provider.get_slides_images_meta_for_media(query.uuid)
    return JsonResponse.create(slides_images_meta_results)


@fetch_api_bp.get("/getKeywords", tags=[keywords_tag])
@jwt_required()
def get_keywords(query: KeywordsQuery):
    """Fetch keywords results of urn and provide to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    keywords_results = metadata_provider.get_keywords_for_media(query.uuid)
    return JsonResponse.create(keywords_results)


# REQUESTS FROM ML-BACKEND


@fetch_api_bp.get("/getUrl", tags=[url_tag])
@jwt_required()
def get_download_url(query: UrlQuery):
    """Create url from urn and provide to ml-backend"""
    # Protect api to only allow getUrl for ml-backend user
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()

    connector = None
    if "assetdb" in query.urn:
        connector = connector_provider.get_assetdb_connector()
    elif "mediadb" in query.urn:
        connector = connector_provider.get_mediadb_connector()
    else:
        return ErrorResponse.create_custom("Invalid urn for getUrl")

    connector.connect()
    # http://assetdb:9001/raw/8731cc0a-0f79-4af8-bbb6-1fce897a82f4.mp4?X-Amz-Algorithm
    query_mode = query.mode.lower()
    # quoted urn sent by airflow, unquote urn
    urn = unquote(query.urn)
    url = None
    if "upload" in query_mode:
        url = connector.gen_presigned_url(urn, MinioConnectorFetchUrlMode.UPLOAD)
    elif "download" in query.mode.lower():
        url = connector.gen_presigned_url(urn, MinioConnectorFetchUrlMode.DOWNLOAD)
    else:
        return ErrorResponse.create_custom("Invalid url mode for getUrl")

    if url is None:
        return ErrorResponse.create_custom("Url is None in getUrl")

    final_url = metadata_provider.modify_url_for_db_access(url)

    data_dict = {"url": final_url}
    data_str = json.dumps(data_dict)
    data_json = json.loads(data_str)
    return JsonResponse.create(data_json)


@fetch_api_bp.get("/getMetaData", tags=[metadata_tag])
@jwt_required()
def get_metadata_by_urn(query: MetaDataQuery):
    """Fetch meta data from metadb by urn and provide it to ml-backend"""
    # Protect api to only allow getMetaData for ml-backend user
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()

    connector = connector_provider.get_metadb_connector()
    connector.connect()
    data_dict = connector.get_metadata(query.urn)
    # Filter internal data, only use real meta data in response
    result_dict = {
        "uuid": data_dict["uuid"],
        "title": data_dict["title"],
        "type": data_dict["type"],
        "description": data_dict["description"],
        "language": data_dict["language"],
        "licenses": data_dict["licenses"],
        "permissions": data_dict["permissions"],
        "tags": data_dict["tags"],
        "thumbnails": data_dict["thumbnails"],
    }
    data_str = json.dumps(result_dict)
    data_json = json.loads(data_str)
    return JsonResponse.create(data_json)
