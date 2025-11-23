#!/usr/bin/env python
"""Central point to access the meta data in the databases """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from connectors.connector_provider import connector_provider
from connectors.config import get_frontend_protocol, get_backend_protocol
from connectors.config import get_backend_host_url, get_frontend_host_url

import json
from typing import Any, Dict, List

from api.modules.responses import JsonResponse, ErrorResponse


class MetaDataProvider:
    """
    MetaDataProvider is responsible for
    providing meta data from all databases on a central point
    """

    def __init__(self):
        self.assetdb_connector = connector_provider.get_assetdb_connector()
        self.assetdb_connector.connect()
        self.mediadb_connector = connector_provider.get_mediadb_connector()
        self.mediadb_connector.connect()
        self.opensearch_connector = connector_provider.get_opensearch_connector()
        self.opensearch_connector.connect()

    def modify_url_for_db_access(self, input_url): # Original method signature
        """
        Convert url to correct backend url for accessing the url from the public

        :param str input_url: Url

        :return: str Corrected url or an ErrorResponse object
        """
        # --- START OF MODIFICATIONS ---
        if input_url is None or not isinstance(input_url, str): # Added type check for robustness
            # Consider logging here if you have a logger (e.g., logger.error(f"Input URL is None or invalid: {input_url}"))
            return ErrorResponse.create_custom("Url is None or invalid in getUrl") # Slightly updated message

        # Get your dynamically configured frontend base URL (e.g., http://10.16.246.8:7087)
        expected_frontend_base = get_frontend_protocol() + "://" + get_frontend_host_url()

        # 1. Check for direct, fully qualified frontend avatar URLs (like http://10.16.246.8:7087/avatars/...)
        if input_url.startswith(expected_frontend_base + "/avatars/"):
            return input_url # It's already correct, return as is

        # 2. Check for the "http://localhost/avatars/..." placeholder pattern
        elif input_url.startswith("http://localhost/avatars/"):
            # Extracts "avatars/filename.png" from "http://localhost/avatars/filename.png"
            path_after_localhost = input_url.split("http://localhost/", 1)[1] 
            return expected_frontend_base + "/" + path_after_localhost
        # --- END OF MODIFICATIONS ---
        
        # Original logic for backend services and other general localhost paths follows:
        # Safely extract sub_url (path part after scheme://host:port/)
        path_parts = input_url.split("/", 3)
        # if input_url is "http://localhost/", path_parts is ['http:', '', 'localhost', '']
        # if input_url is "http://localhost/path", path_parts is ['http:', '', 'localhost', 'path']
        # if input_url is "http://assetdb:9000/bucket/file", path_parts is ['http:', '', 'assetdb:9000', 'bucket/file']
        sub_url = path_parts[3] if len(path_parts) > 3 else ""

        if "://assetdb:" in input_url:
            final_url = get_backend_protocol() + "://" + get_backend_host_url() + "/assetdb/" + sub_url
        elif "://mediadb:" in input_url:
            final_url = get_backend_protocol() + "://" + get_backend_host_url() + "/mediadb/" + sub_url
        elif "://searchengine:" in input_url:
            final_url = get_backend_protocol() + "://" + get_backend_host_url() + "/searchengine/" + sub_url
        elif "://localhost/" in input_url: # Handles general "http://localhost/other_paths" (avatars already handled)
            # The sub_url from input_url.split("/", 3)[3] is used here as in original logic for this case.
            final_url = expected_frontend_base + "/" + sub_url
        else:
            # If it's not any of the known patterns (avatars, backend services, general localhost)
            # Consider logging here for unhandled patterns (e.g., logger.warning(f"Unhandled URL: {input_url}"))
            return ErrorResponse.create_custom("Invalid url generated in getUrl")
        return final_url

    def get_metadata_for_uuid_list(self, uuid_list):
        """
        Get metadata objects from metadb for specified uuids and preprocess data for search vue.

        :param list(str) uuid_list: List of uuids for metadb

        :return: array(dict) List of meta data items, e.g. media items
        """
        result_data_list = []
        for uuid in uuid_list:
            result_dict = self.get_metadata_by_uuid(uuid)
            data_str = json.dumps(result_dict)
            data_json = json.loads(data_str)

            result_data_list.append(data_json)

        return result_data_list

    def get_media_metadata(self, uuid: str, key="_id") -> Dict[str, Any]:
        """
        Retrieves the metadata for a media UUID

        :param uuid: UUID for the meta data in mongo db

        :return: The metadata for the given media UUID
        """
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        result = mongo_connector.get_metadata(f"metadb:meta:post:id:{uuid}", key)
        # mongo_connector.disconnect()
        return result

    def _activate_access_to_url(
        self, top_level_entry: str, meta_data: Dict[str, Any], read_only=False, destination_entry=None
    ):
        """
        Activate access for clients to urls in meta data
        Currently only works for top level entries in meta data
        Could also store the url on a different destination key
        Uses assetdb connector
        """

        temp_urn = meta_data[top_level_entry]
        if read_only is True:
            # TODO: security handling for minio media db access
            # print(f"Activate readonly policy for {top_level_entry} : Start")
            self.assetdb_connector.activate_read_only_policy(temp_urn)
            # print(f"Activate readonly policy for {top_level_entry} : Finish")
        temp_url = self.assetdb_connector.gen_presigned_url(temp_urn)
        temp_url_mod = self.modify_url_for_db_access(temp_url)
        if destination_entry is None:
            meta_data[top_level_entry] = temp_url_mod
        else:
            meta_data[destination_entry] = temp_url_mod
        return meta_data

    def activate_meta_data_access(self, meta_data):
        """
        Activate access for meta data item

        :param dict meta_data: Meta data to activate access for

        :return: dict Media item meta data
        """
        if "thumbnails" in meta_data:
            lecturer_thumbnail_url = meta_data["thumbnails"]["lecturer"]
            meta_data["thumbnails"]["lecturer"] = self.modify_url_for_db_access(lecturer_thumbnail_url)
            media_thumbnail_urn = meta_data["thumbnails"]["media"]
            media_thumbnail_timeline_urn = meta_data["thumbnails"]["media"].rsplit("/")[0]
            media_thumbnail_url = self.assetdb_connector.gen_presigned_url(media_thumbnail_urn)
            media_thumbnail_url_mod = self.modify_url_for_db_access(media_thumbnail_url)
            meta_data["thumbnails"]["media"] = media_thumbnail_url_mod
            meta_data["thumbnails"]["timeline"] = media_thumbnail_timeline_urn

        if "slides_images_meta" in meta_data:
            slides_images_meta_urn = meta_data["slides_images_meta"]
            slides_images_folder_urn = meta_data["slides_images_meta"].rsplit("/")[0]
            slides_images_meta_urn = slides_images_folder_urn + "/slides.meta.json"
            # print("Activate readonly policy for slides_images_meta: Start")
            self.assetdb_connector.activate_read_only_policy(slides_images_folder_urn)
            # print("Activate readonly policy for slides_images_meta: Finish")
            slides_images_meta_url = self.assetdb_connector.gen_presigned_url(slides_images_meta_urn)
            slides_images_meta_url_mod = self.modify_url_for_db_access(slides_images_meta_url)
            meta_data["slides_images_meta"] = slides_images_meta_url_mod
            meta_data["slides_images_folder"] = slides_images_folder_urn

        if "media" in meta_data:
            media_urn = meta_data["media"]
            media_hls_urn = meta_data["media"].replace(".dash.mpd", ".m3u8")
            # TODO: security handling for minio media db access
            # print("Activate readonly policy for media: Start")
            self.mediadb_connector.activate_read_only_policy(media_urn)
            self.mediadb_connector.activate_read_only_policy_for_videos()
            # print("Activate readonly policy for media: Finish")
            media_url = self.mediadb_connector.gen_presigned_url(media_urn)
            media_url_mod = self.modify_url_for_db_access(media_url)
            meta_data["media"] = media_url_mod
            if self.mediadb_connector.get_metadata(media_hls_urn) is not None:
                media_hls_url = self.mediadb_connector.gen_presigned_url(media_hls_urn)
                media_hls_url_mod = self.modify_url_for_db_access(media_hls_url)
                meta_data["media_hls"] = media_hls_url_mod
        if not "media_hls" in meta_data:
            meta_data["media_hls"] = "none"

        if "slides" in meta_data:
            meta_data = self._activate_access_to_url("slides", meta_data)
        if "audio" in meta_data:
            meta_data = self._activate_access_to_url("audio", meta_data)

        if meta_data["language"] == "de" and "asr_result_de" in meta_data.keys():
            meta_data = self._activate_access_to_url("transcript_de", meta_data, False, "transcript")
            meta_data = self._activate_access_to_url("asr_result_de", meta_data, False, "asr_result")
            meta_data = self._activate_access_to_url("subtitle_de", meta_data, False, "subtitle")
        elif meta_data["language"] == "en" and "asr_result_en" in meta_data.keys():
            meta_data = self._activate_access_to_url("transcript_en", meta_data, False, "transcript")
            meta_data = self._activate_access_to_url("asr_result_en", meta_data, False, "asr_result")
            meta_data = self._activate_access_to_url("subtitle_en", meta_data, False, "subtitle")
        meta_data = self._activate_access_to_url("subtitle_de", meta_data)
        meta_data = self._activate_access_to_url("subtitle_en", meta_data)

        if "asr_result_de" in meta_data.keys():
            meta_data = self._activate_access_to_url("asr_result_de", meta_data)
        else:
            meta_data["asr_result_de"] = "none"
        if "asr_result_en" in meta_data.keys():
            meta_data = self._activate_access_to_url("asr_result_en", meta_data)
        else:
            meta_data["asr_result_en"] = "none"

        if "transcript_de" in meta_data.keys():
            meta_data = self._activate_access_to_url("transcript_de", meta_data)
        else:
            meta_data["transcript_de"] = "none"
        if "transcript_en" in meta_data.keys():
            meta_data = self._activate_access_to_url("transcript_en", meta_data)
        else:
            meta_data["transcript_en"] = "none"

        if "summary_result_de" in meta_data.keys():
            meta_data = self._activate_access_to_url("summary_result_de", meta_data)
        else:
            meta_data["summary_result_de"] = "none"
        if "summary_result_en" in meta_data.keys():
            meta_data = self._activate_access_to_url("summary_result_en", meta_data)
        else:
            meta_data["summary_result_en"] = "none"

        if "short_summary_result_de" in meta_data.keys():
            meta_data = self._activate_access_to_url("short_summary_result_de", meta_data)
        else:
            meta_data["short_summary_result_de"] = "none"
        if "short_summary_result_en" in meta_data.keys():
            meta_data = self._activate_access_to_url("short_summary_result_en", meta_data)
        else:
            meta_data["short_summary_result_en"] = "none"

        if "topic_result_de" in meta_data.keys():
            meta_data = self._activate_access_to_url("topic_result_de", meta_data)
        else:
            meta_data["topic_result_de"] = "none"
        if "topic_result_en" in meta_data.keys():
            meta_data = self._activate_access_to_url("topic_result_en", meta_data)
        else:
            meta_data["topic_result_en"] = "none"

        if "questionnaire_curated" not in meta_data.keys():
            meta_data["questionnaire_curated"] = True

        if "questionnaire_result_de" in meta_data.keys():
            meta_data = self._activate_access_to_url("questionnaire_result_de", meta_data)
        else:
            meta_data["questionnaire_result_de"] = "none"
        if "questionnaire_result_en" in meta_data.keys():
            meta_data = self._activate_access_to_url("questionnaire_result_en", meta_data)
        else:
            meta_data["questionnaire_result_en"] = "none"

        if "search_trie_de" in meta_data.keys():
            meta_data = self._activate_access_to_url("search_trie_de", meta_data)
        else:
            meta_data["search_trie_de"] = "none"
        if "search_trie_en" in meta_data.keys():
            meta_data = self._activate_access_to_url("search_trie_en", meta_data)
        else:
            meta_data["search_trie_en"] = "none"

        if "slides_trie" in meta_data.keys():
            meta_data = self._activate_access_to_url("slides_trie", meta_data)
        else:
            meta_data["slides_trie"] = "none"

        if "keywords_result" in meta_data.keys():
            meta_data = self._activate_access_to_url("keywords_result", meta_data)
        else:
            meta_data["keywords_result"] = "none"

        if not "airflow_info" in meta_data.keys():
            meta_data["airflow_info"] = {}

        # make history available to frontend
        if not "topic_result_de_history" in meta_data.keys():
            meta_data["topic_result_de_history"] = []
        if not "topic_result_en_history" in meta_data.keys():
            meta_data["topic_result_en_history"] = []
        if not "questionnaire_result_de_history" in meta_data.keys():
            meta_data["questionnaire_result_de_history"] = []
        if not "questionnaire_result_en_history" in meta_data.keys():
            meta_data["questionnaire_result_en_history"] = []
        if not "airflow_info_history" in meta_data.keys():
            meta_data["airflow_info_history"] = []

        # TODO: Fix handling of markers if available in airflow
        meta_data["marker"] = "marker_result.json"

        if "lms_gated_access" not in meta_data.keys():
            meta_data["lms_gated_access"] = False
        if "lms_gated_access_details" not in meta_data.keys():
            meta_data["lms_gated_access_details"] = {}

        surveys = []
        if "surveys" in meta_data:
            surveys = meta_data["surveys"]

        return {
            "uuid": meta_data["uuid"],
            "asr_result": meta_data["asr_result"],
            "audio": meta_data["audio"],
            "description": meta_data["description"],
            "language": meta_data["language"],
            "licenses": meta_data["licenses"],
            "marker": meta_data["marker"],
            "media": meta_data["media"],
            "media_hls": meta_data["media_hls"],
            "permissions": meta_data["permissions"],
            "slides": meta_data["slides"],
            "slides_images_meta": meta_data["slides_images_meta"],
            "slides_images_folder": meta_data["slides_images_folder"],
            "subtitle": meta_data["subtitle"],
            "subtitle_de": meta_data["subtitle_de"],
            "subtitle_en": meta_data["subtitle_en"],
            "thumbnails": meta_data["thumbnails"],
            "title": meta_data["title"],
            "transcript": meta_data["transcript"],
            "state": meta_data["state"],
            "surveys": surveys,
            "asr_result_de": meta_data["asr_result_de"],
            "asr_result_en": meta_data["asr_result_en"],
            "transcript_de": meta_data["transcript_de"],
            "transcript_en": meta_data["transcript_en"],
            "short_summary_result_de": meta_data["short_summary_result_de"],
            "short_summary_result_en": meta_data["short_summary_result_en"],
            "summary_result_de": meta_data["summary_result_de"],
            "summary_result_en": meta_data["summary_result_en"],
            "topic_result_de": meta_data["topic_result_de"],
            "topic_result_en": meta_data["topic_result_en"],
            "search_trie_de": meta_data["search_trie_de"],
            "search_trie_en": meta_data["search_trie_en"],
            "slides_trie": meta_data["slides_trie"],
            "topic_result_de_history": meta_data["topic_result_de_history"],
            "topic_result_en_history": meta_data["topic_result_en_history"],
            "airflow_info": meta_data["airflow_info"],
            "airflow_info_history": meta_data["airflow_info_history"],
            "questionnaire_curated": meta_data["questionnaire_curated"],
            "questionnaire_result_de": meta_data["questionnaire_result_de"],
            "questionnaire_result_en": meta_data["questionnaire_result_en"],
            "questionnaire_result_de_history": meta_data["questionnaire_result_de_history"],
            "questionnaire_result_en_history": meta_data["questionnaire_result_en_history"],
            "keywords_result": meta_data["keywords_result"],
            "lms_gated_access": meta_data["lms_gated_access"],
            "lms_gated_access_details": meta_data["lms_gated_access_details"],
        }

    def get_metadata_by_uuid(self, uuid, key="_id"):
        """
        Get meta data as dict by uuid

        :param str uuid: UUID for the meta data in mongo db

        :return: dict Media item meta data
        """
        meta_data = self.get_media_metadata(uuid, key)

        if meta_data is None or not meta_data.keys():
            return {}
        return self.activate_meta_data_access(meta_data=meta_data)

    def _get_object_for_media(self, media_uuid: str, metadata_key: str) -> str:
        """
        Gets an object with a key from metadata for a media UUID

        :param media_uuid: UUID for the media meta data in mongo db
        :param metadata_key: Key for retrieving an item from the media metadata

        :return: An object loaded from the media metadata with the given key
        """
        meta_data = self.get_media_metadata(media_uuid)
        # TODO: Fix handling of markers if available in airflow
        meta_data["marker"] = "marker_result.json"
        return self.assetdb_connector.get_object(meta_data[metadata_key]).data

    def get_transcript_for_media(self, media_uuid: str) -> str:
        """
        Get the transcript for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized transcript json object for the given media UUID
        """
        return self._get_object_for_media(media_uuid, "transcript")

    def get_asr_results_for_media(self, media_uuid: str) -> str:
        """
        Get the asr results for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized asr result json objects for the given media UUID
        """
        asr_result_de = self._get_object_for_media(media_uuid, "asr_result_de")
        asr_result_en = self._get_object_for_media(media_uuid, "asr_result_en")
        return {
            "data": [
                {"type": "AsrResult", "language": "de", "result": asr_result_de},
                {"type": "AsrResult", "language": "en", "result": asr_result_en},
            ]
        }

    def get_transcript_results_for_media(self, media_uuid: str) -> str:
        """
        Get the transcript results for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized asr result json objects for the given media UUID
        """
        transcript_de = self._get_object_for_media(media_uuid, "transcript_de")
        transcript_en = self._get_object_for_media(media_uuid, "transcript_en")
        return {
            "data": [
                {"type": "TranscriptResult", "language": "de", "result": transcript_de},
                {"type": "TranscriptResult", "language": "en", "result": transcript_en},
            ]
        }

    def get_raw_transcript_for_media(self, media_uuid: str, language: str) -> str:
        transcript = self._get_object_for_media(media_uuid, "transcript_de" if language == "de" else "transcript_en")
        return json.loads(transcript)["result"]

    def get_short_summary_for_media(self, media_uuid: str) -> dict[str, list[Any]]:
        """
        Get the short summaries for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized short summaries result json object for the given media UUID
        """

        short_summary_result_de = self._get_object_for_media(media_uuid, "short_summary_result_de")
        short_summary_result_en = self._get_object_for_media(media_uuid, "short_summary_result_en")

        # print(type(short_summary_result_en), short_summary_result_en)

        return {"data": [json.loads(short_summary_result_de.decode()), json.loads(short_summary_result_en.decode())]}

    def get_search_trie_for_media(self, media_uuid: str) -> str:
        """
        Get the search trie for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized search trie result json object for the given media UUID
        """

        search_trie_result_de = self._get_object_for_media(media_uuid, "search_trie_de")
        search_trie_result_en = self._get_object_for_media(media_uuid, "search_trie_en")

        return {"data": [search_trie_result_de, search_trie_result_en]}

    def get_search_trie_slides_for_media(self, media_uuid: str) -> str:
        """
        Get the slides earch trie for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized search trie result json object for the given media UUID
        """

        slides_trie_result_de = self._get_object_for_media(media_uuid, "slides_trie")

        return {"data": [slides_trie_result_de]}

    def get_summary_for_media(self, media_uuid: str) -> str:
        """
        Get the summaries for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized summareis result json object for the given media UUID
        """

        summary_result_de = self._get_object_for_media(media_uuid, "summary_result_de")
        summary_result_en = self._get_object_for_media(media_uuid, "summary_result_en")

        return {"data": [json.loads(summary_result_de.decode()), json.loads(summary_result_en.decode())]}

    def get_topics_for_media(self, media_uuid: str) -> str:
        """
        Get the topic results for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized topics result json object for the given media UUID
        """

        topic_result_de = self._get_object_for_media(media_uuid, "topic_result_de")
        topic_result_en = self._get_object_for_media(media_uuid, "topic_result_en")

        return {"data": [json.loads(topic_result_de.decode()), json.loads(topic_result_en.decode())]}

    def get_markers_for_media(self, media_uuid: str) -> str:
        """
        Get the markers for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized markers json object for the given media UUID
        """
        return self._get_object_for_media(media_uuid, "marker")

    def get_thumbnail_url_from_urn(self, urn: str) -> str:
        """
        Get the summaries for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized summareis result json object for the given media UUID
        """
        thumbnail_timeline_url = self.assetdb_connector.gen_presigned_url(urn)
        thumbnail_timeline_url_mod = self.modify_url_for_db_access(thumbnail_timeline_url)

        return {"data": thumbnail_timeline_url_mod}

    def get_questionnaire_for_media(self, media_uuid: str) -> str:
        """
        Get the questionnaires for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized questionnaires result json object for the given media UUID
        """

        questionnaire_result_de = self._get_object_for_media(media_uuid, "questionnaire_result_de")
        questionnaire_result_en = self._get_object_for_media(media_uuid, "questionnaire_result_en")

        return {"data": [json.loads(questionnaire_result_de.decode()), json.loads(questionnaire_result_en.decode())]}

    def get_slides_images_meta_for_media(self, media_uuid: str) -> dict:
        """
        Get the slides images meta data for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized slides images meta data json object for the given media UUID
        """

        slides_images_meta_result = self._get_object_for_media(media_uuid, "slides_images_meta")

        return {"data": [json.loads(slides_images_meta_result.decode())]}

    def get_keywords_for_media(self, media_uuid: str) -> dict:
        """
        Get the keywords data for the media UUID

        :param media_uuid: UUID for the media meta data in mongo db

        :return: The serialized keywords data json object for the given media UUID
        """

        keywords_result = self._get_object_for_media(media_uuid, "keywords_result")

        return {"data": [json.loads(keywords_result.decode())]}

    def get_documents_for_channel(self, channel_uuid: str) -> dict:
        """
        Get the documents data for the channel UUID

        :param channel_uuid: UUID for the channel meta data in mongo db

        :return: The serialized documents data json object for the given channel UUID
        """
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        channel_meta_data = mongo_connector.get_metadata(f"metadb:meta:post:id:{channel_uuid}")
        if not "documents" in channel_meta_data:
            return {"data": []}
        result = []
        for doc_uuid in channel_meta_data["documents"]:
            doc_meta_data = mongo_connector.get_metadata(f"metadb:meta:post:id:{doc_uuid}")
            res_meta = {
                "uuid": doc_meta_data["uuid"],
                "filename": doc_meta_data["filename"],
                "mime_type": doc_meta_data["mime_type"],
                "urn": doc_meta_data["urn"],
                "channel_uuid": doc_meta_data["channel_uuid"],
                "status": doc_meta_data["status"],
                "visible": doc_meta_data["visible"],
            }
            res_meta = self._activate_access_to_url("urn", res_meta, True, "url")
            result.append(res_meta)

        return {"data": result}

    def search_lectures_standard(self, query, search_credentials, fields=[]):
        """
        Search lectures

        :param str query: Search query for the searchengine
        :param str fields: Fields for the searchengine, empty array searches in all fields

        :return: List of search-result media item uuids
        """
        if fields is None:
            return self.opensearch_connector.standard_document_search(query, search_credentials, [])
        return self.opensearch_connector.standard_document_search(query, search_credentials, fields)

    def search_lectures_multi_match(self, query, fields=[]):
        """
        Search lectures

        :param str query: Search query for the searchengine
        :param str fields: Fields for the searchengine, empty array searches in all fields

        :return: List of search-result media item uuids
        """
        if fields is None:
            return self.opensearch_connector.search_lectures_multi_match(query, [])
        return self.opensearch_connector.search_lectures_multi_match(query, fields)

    def search_recent_lectures(self, search_credentials, amount):
        """
        Search recent lectures

        :param int amount: Amount of lectures to obtain, e.g. 16

        :return: List of search-result media item uuids
        """
        print("Search credentials: ", search_credentials)
        print("Amount: ", amount)
        return self.opensearch_connector.search_recent_lectures(search_credentials, amount)

    def search_channels(self, amount):
        """
        Search channels

        :param int amount: Amount of channels to obtain, e.g. 8

        :return: array(dict) List of channel items
        """
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        resultChannels = mongo_connector.get_list_of_metadata_by_type(
            "metadb:meta:post:id:dummy0815", "channel", amount
        )
        result_data_list = []
        for channel in resultChannels:
            surveys = []
            if "surveys" in channel:
                surveys = channel["surveys"]
            if "lms_gated_access" not in channel.keys():
                channel["lms_gated_access"] = False
            if "lms_gated_access_details" not in channel.keys():
                channel["lms_gated_access_details"] = {}
            result_dict = {
                "uuid": channel["uuid"],
                "course": channel["course"],
                "course_acronym": channel["course_acronym"],
                "faculty": channel["faculty"],
                "faculty_acronym": channel["faculty_acronym"],
                "faculty_color": channel["faculty_color"],
                "language": channel["language"],
                "lecturer": channel["lecturer"],
                "license": channel["license"],
                "license_url": channel["license_url"],
                "semester": channel["semester"],
                "tags": channel["tags"],
                "thumbnails": channel["thumbnails"],
                "university": channel["university"],
                "university_acronym": channel["university_acronym"],
                "surveys": surveys,
                "lms_gated_access": channel["lms_gated_access"],
                "lms_gated_access_details": channel["lms_gated_access_details"],
            }
            lecturer_thumbnail_url = result_dict["thumbnails"]["lecturer"]
            result_dict["thumbnails"]["lecturer"] = self.modify_url_for_db_access(lecturer_thumbnail_url)
            data_str = json.dumps(result_dict)
            data_json = json.loads(data_str)

            result_data_list.append(data_json)
        # mongo_connector.disconnect()
        return result_data_list

    def search_media(self, amount):
        """
        Search media

        :param int amount: Amount of channels to obtain, e.g. 8

        :return: array(dict) List of channel items
        """
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        print("SearchMedia")
        resultMediaFull = mongo_connector.get_list_of_metadata_by_type("metadb:meta:post:id:dummy0815", "media", amount)
        print("SearchMedia: Create result")
        resultMedia = []
        for mediaitem in resultMediaFull:
            # print(mediaitem)
            resultMedia.append(self.activate_meta_data_access(mediaitem))
        # mongo_connector.disconnect()
        print("SearchMedia: Done")
        return resultMedia

    def search_uploaded_media(self, channel_uuid, channel_course_acronym, sec_meta_data):
        """
        Search uploaded media by login sec_meta_data, channel uuid and channel course acronym

        :return: array(dict) List of media items
        """
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        print("SearchUploadedMedia")
        resultMediaFull = mongo_connector.get_media_metadata_by_sec_meta_data(
            channel_uuid, channel_course_acronym, sec_meta_data
        )
        print("SearchUploadedMedia: Create result")
        resultMedia = []
        for mediaitem in resultMediaFull:
            # print(mediaitem)
            resultMedia.append(self.activate_meta_data_access(mediaitem))
        # mongo_connector.disconnect()
        print("SearchUploadedMedia: Done")
        return resultMedia

    def search_user_channels(self, sec_meta_data):
        """
        Search users channels by login sec_meta_data

        :return: array(dict) List of media items
        """
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        print("SearchUsersChannels")
        resultChannelsFull = None
        if sec_meta_data.check_user_has_roles(["admin", "developer"]):
            resultChannelsFull = mongo_connector.get_list_of_metadata_by_type(
                "metadb:meta:post:id:dummy0815", "channel", 1024
            )
        else:
            resultChannelsFull = mongo_connector.get_channels_metadata_by_sec_meta_data(sec_meta_data)
        print("SearchUsersChannels: Create result")
        resultChannels = []
        for channel in resultChannelsFull:
            # print(channel)
            # TODO: Duplicate here with search_channels, check what to remove/modify
            lecturer_thumbnail_url = channel["thumbnails"]["lecturer"]
            channel["thumbnails"]["lecturer"] = self.modify_url_for_db_access(lecturer_thumbnail_url)
            if "lms_gated_access" not in channel.keys():
                channel["lms_gated_access"] = False
            if "lms_gated_access_details" not in channel.keys():
                channel["lms_gated_access_details"] = {}
            resultChannels.append(channel)
        # mongo_connector.disconnect()
        print("SearchUsersChannels: Done")
        return resultChannels


# Initialize connectors once
metadata_provider = MetaDataProvider()
