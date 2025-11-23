#!/usr/bin/env python
"""Central point to access the meta data in the databases """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.1" # Version bumped
__status__ = "Draft"


from connectors.connector_provider import connector_provider
from connectors.config import get_frontend_protocol, get_backend_protocol
from connectors.config import get_backend_host_url, get_frontend_host_url

import json
from typing import Any, Dict, List, Optional

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

    def modify_url_for_db_access(self, input_url):
        if input_url is None or not isinstance(input_url, str):
            return ErrorResponse.create_custom("Url is None or invalid in getUrl")

        expected_frontend_base = get_frontend_protocol() + "://" + get_frontend_host_url()

        if input_url.startswith(expected_frontend_base + "/avatars/"):
            return input_url
        elif input_url.startswith("http://localhost/avatars/"):
            path_after_localhost = input_url.split("http://localhost/", 1)[1] 
            return expected_frontend_base + "/" + path_after_localhost
        
        path_parts = input_url.split("/", 3)
        sub_url = path_parts[3] if len(path_parts) > 3 else ""

        if "://assetdb:" in input_url:
            final_url = get_backend_protocol() + "://" + get_backend_host_url() + "/assetdb/" + sub_url
        elif "://mediadb:" in input_url:
            final_url = get_backend_protocol() + "://" + get_backend_host_url() + "/mediadb/" + sub_url
        elif "://searchengine:" in input_url:
            final_url = get_backend_protocol() + "://" + get_backend_host_url() + "/searchengine/" + sub_url
        elif "://localhost/" in input_url:
            final_url = expected_frontend_base + "/" + sub_url
        else:
            return ErrorResponse.create_custom("Invalid url generated in getUrl")
        return final_url

    def get_metadata_for_uuid_list(self, uuid_list):
        result_data_list = []
        for uuid in uuid_list:
            result_dict = self.get_metadata_by_uuid(uuid)
            data_str = json.dumps(result_dict)
            data_json = json.loads(data_str)
            result_data_list.append(data_json)
        return result_data_list

    def get_media_metadata(self, uuid: str, key="_id") -> Dict[str, Any]:
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        result = mongo_connector.get_metadata(f"metadb:meta:post:id:{uuid}", key)
        return result

    # --- MODIFIED FUNCTION: Now checks for key existence and valid URN format ---
    def _activate_access_to_url(
        self, top_level_entry: str, meta_data: Dict[str, Any], read_only=False, destination_entry=None
    ):
        """
        Safely activate access for clients to URLs in meta data.
        """
        # 1. Check if the key exists in the metadata at all.
        if top_level_entry not in meta_data:
            return meta_data # Key is missing, do nothing.

        temp_urn = meta_data[top_level_entry]

        # 2. Check if the value is a valid-looking URN (string with a colon).
        # This will skip placeholders like "<...>" which caused previous errors.
        if not isinstance(temp_urn, str) or ":" not in temp_urn:
            return meta_data # Data is not a valid URN, do nothing.

        if read_only is True:
            self.assetdb_connector.activate_read_only_policy(temp_urn)
        
        temp_url = self.assetdb_connector.gen_presigned_url(temp_urn)
        temp_url_mod = self.modify_url_for_db_access(temp_url)
        
        if destination_entry is None:
            meta_data[top_level_entry] = temp_url_mod
        else:
            meta_data[destination_entry] = temp_url_mod
        return meta_data

    # --- UNCHANGED FUNCTION: The logic here is preserved, but it now uses the safe helper above ---
    def activate_meta_data_access(self, meta_data):
        """
        Activate access for meta data item.
        This function is now robust against missing keys in the 'meta_data' dict.
        """
        if "thumbnails" in meta_data and meta_data["thumbnails"]:
            if "lecturer" in meta_data["thumbnails"]:
                 meta_data["thumbnails"]["lecturer"] = self.modify_url_for_db_access(meta_data["thumbnails"]["lecturer"])
            if "media" in meta_data["thumbnails"] and isinstance(meta_data["thumbnails"]["media"], str) and ":" in meta_data["thumbnails"]["media"]:
                media_thumbnail_urn = meta_data["thumbnails"]["media"]
                media_thumbnail_timeline_urn = media_thumbnail_urn.rsplit("/")[0]
                media_thumbnail_url = self.assetdb_connector.gen_presigned_url(media_thumbnail_urn)
                meta_data["thumbnails"]["media"] = self.modify_url_for_db_access(media_thumbnail_url)
                meta_data["thumbnails"]["timeline"] = media_thumbnail_timeline_urn

        if "slides_images_meta" in meta_data and isinstance(meta_data["slides_images_meta"], str) and ":" in meta_data["slides_images_meta"]:
            slides_images_folder_urn = meta_data["slides_images_meta"].rsplit("/")[0]
            slides_images_meta_urn = slides_images_folder_urn + "/slides.meta.json"
            self.assetdb_connector.activate_read_only_policy(slides_images_folder_urn)
            slides_images_meta_url = self.assetdb_connector.gen_presigned_url(slides_images_meta_urn)
            meta_data["slides_images_meta"] = self.modify_url_for_db_access(slides_images_meta_url)
            meta_data["slides_images_folder"] = slides_images_folder_urn

        if "media" in meta_data and isinstance(meta_data["media"], str) and ":" in meta_data["media"]:
            media_urn = meta_data["media"]
            media_hls_urn = media_urn.replace(".dash.mpd", ".m3u8")
            self.mediadb_connector.activate_read_only_policy(media_urn)
            self.mediadb_connector.activate_read_only_policy_for_videos()
            media_url = self.mediadb_connector.gen_presigned_url(media_urn)
            meta_data["media"] = self.modify_url_for_db_access(media_url)
            if self.mediadb_connector.get_metadata(media_hls_urn) is not None:
                media_hls_url = self.mediadb_connector.gen_presigned_url(media_hls_urn)
                meta_data["media_hls"] = self.modify_url_for_db_access(media_hls_url)
        
        meta_data.setdefault("media_hls", "none")

        meta_data = self._activate_access_to_url("slides", meta_data)
        meta_data = self._activate_access_to_url("audio", meta_data)

        language = meta_data.get("language")
        if language == "de":
            meta_data = self._activate_access_to_url("transcript_de", meta_data, False, "transcript")
            meta_data = self._activate_access_to_url("asr_result_de", meta_data, False, "asr_result")
            meta_data = self._activate_access_to_url("subtitle_de", meta_data, False, "subtitle")
        elif language == "en":
            meta_data = self._activate_access_to_url("transcript_en", meta_data, False, "transcript")
            meta_data = self._activate_access_to_url("asr_result_en", meta_data, False, "asr_result")
            meta_data = self._activate_access_to_url("subtitle_en", meta_data, False, "subtitle")
        
        # Process all optional asset fields safely
        optional_asset_fields = [
            "subtitle_de", "subtitle_en", "asr_result_de", "asr_result_en", "transcript_de",
            "transcript_en", "summary_result_de", "summary_result_en", "short_summary_result_de",
            "short_summary_result_en", "topic_result_de", "topic_result_en", "questionnaire_result_de",
            "questionnaire_result_en", "search_trie_de", "search_trie_en", "slides_trie", "keywords_result"
        ]
        for field in optional_asset_fields:
            meta_data = self._activate_access_to_url(field, meta_data)
            meta_data.setdefault(field, "none") # Ensure key exists even if not processed

        # Set other defaults for missing keys
        meta_data.setdefault("questionnaire_curated", True)
        meta_data.setdefault("airflow_info", {})
        meta_data.setdefault("topic_result_de_history", [])
        meta_data.setdefault("topic_result_en_history", [])
        meta_data.setdefault("questionnaire_result_de_history", [])
        meta_data.setdefault("questionnaire_result_en_history", [])
        meta_data.setdefault("airflow_info_history", [])
        meta_data.setdefault("marker", "marker_result.json")
        meta_data.setdefault("lms_gated_access", False)
        meta_data.setdefault("lms_gated_access_details", {})
        meta_data.setdefault("surveys", [])

        # Build the final dictionary from the processed (and now complete) meta_data
        return {
            "uuid": meta_data.get("uuid"),
            "asr_result": meta_data.get("asr_result"),
            "audio": meta_data.get("audio"),
            "description": meta_data.get("description"),
            "language": meta_data.get("language"),
            "licenses": meta_data.get("licenses"),
            "marker": meta_data.get("marker"),
            "media": meta_data.get("media"),
            "media_hls": meta_data.get("media_hls"),
            "permissions": meta_data.get("permissions"),
            "slides": meta_data.get("slides"),
            "slides_images_meta": meta_data.get("slides_images_meta"),
            "slides_images_folder": meta_data.get("slides_images_folder"),
            "subtitle": meta_data.get("subtitle"),
            "subtitle_de": meta_data.get("subtitle_de"),
            "subtitle_en": meta_data.get("subtitle_en"),
            "thumbnails": meta_data.get("thumbnails"),
            "title": meta_data.get("title"),
            "transcript": meta_data.get("transcript"),
            "state": meta_data.get("state"),
            "surveys": meta_data.get("surveys"),
            "asr_result_de": meta_data.get("asr_result_de"),
            "asr_result_en": meta_data.get("asr_result_en"),
            "transcript_de": meta_data.get("transcript_de"),
            "transcript_en": meta_data.get("transcript_en"),
            "short_summary_result_de": meta_data.get("short_summary_result_de"),
            "short_summary_result_en": meta_data.get("short_summary_result_en"),
            "summary_result_de": meta_data.get("summary_result_de"),
            "summary_result_en": meta_data.get("summary_result_en"),
            "topic_result_de": meta_data.get("topic_result_de"),
            "topic_result_en": meta_data.get("topic_result_en"),
            "search_trie_de": meta_data.get("search_trie_de"),
            "search_trie_en": meta_data.get("search_trie_en"),
            "slides_trie": meta_data.get("slides_trie"),
            "topic_result_de_history": meta_data.get("topic_result_de_history"),
            "topic_result_en_history": meta_data.get("topic_result_en_history"),
            "airflow_info": meta_data.get("airflow_info"),
            "airflow_info_history": meta_data.get("airflow_info_history"),
            "questionnaire_curated": meta_data.get("questionnaire_curated"),
            "questionnaire_result_de": meta_data.get("questionnaire_result_de"),
            "questionnaire_result_en": meta_data.get("questionnaire_result_en"),
            "questionnaire_result_de_history": meta_data.get("questionnaire_result_de_history"),
            "questionnaire_result_en_history": meta_data.get("questionnaire_result_en_history"),
            "keywords_result": meta_data.get("keywords_result"),
            "lms_gated_access": meta_data.get("lms_gated_access"),
            "lms_gated_access_details": meta_data.get("lms_gated_access_details"),
        }

    def get_metadata_by_uuid(self, uuid, key="_id"):
        meta_data = self.get_media_metadata(uuid, key)
        if meta_data is None or not meta_data:
            return {}
        return self.activate_meta_data_access(meta_data=meta_data)

    def _get_object_for_media(self, media_uuid: str, metadata_key: str) -> str:
        meta_data = self.get_media_metadata(media_uuid)
        if not meta_data or metadata_key not in meta_data:
            return "" # Return empty string if key is missing
        return self.assetdb_connector.get_object(meta_data[metadata_key]).data

    def get_transcript_for_media(self, media_uuid: str) -> str:
        return self._get_object_for_media(media_uuid, "transcript")

    def get_asr_results_for_media(self, media_uuid: str) -> str:
        asr_result_de = self._get_object_for_media(media_uuid, "asr_result_de")
        asr_result_en = self._get_object_for_media(media_uuid, "asr_result_en")
        return {
            "data": [
                {"type": "AsrResult", "language": "de", "result": asr_result_de},
                {"type": "AsrResult", "language": "en", "result": asr_result_en},
            ]
        }

    def get_transcript_results_for_media(self, media_uuid: str) -> str:
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
        if not transcript: return []
        return json.loads(transcript)["result"]

    def get_short_summary_for_media(self, media_uuid: str) -> dict[str, list[Any]]:
        short_summary_result_de = self._get_object_for_media(media_uuid, "short_summary_result_de")
        short_summary_result_en = self._get_object_for_media(media_uuid, "short_summary_result_en")
        data = []
        if short_summary_result_de: data.append(json.loads(short_summary_result_de.decode()))
        if short_summary_result_en: data.append(json.loads(short_summary_result_en.decode()))
        return {"data": data}

    def get_search_trie_for_media(self, media_uuid: str) -> str:
        search_trie_result_de = self._get_object_for_media(media_uuid, "search_trie_de")
        search_trie_result_en = self._get_object_for_media(media_uuid, "search_trie_en")
        return {"data": [search_trie_result_de, search_trie_result_en]}

    def get_search_trie_slides_for_media(self, media_uuid: str) -> str:
        slides_trie_result = self._get_object_for_media(media_uuid, "slides_trie")
        return {"data": [slides_trie_result]}

    def get_summary_for_media(self, media_uuid: str) -> str:
        summary_result_de = self._get_object_for_media(media_uuid, "summary_result_de")
        summary_result_en = self._get_object_for_media(media_uuid, "summary_result_en")
        data = []
        if summary_result_de: data.append(json.loads(summary_result_de.decode()))
        if summary_result_en: data.append(json.loads(summary_result_en.decode()))
        return {"data": data}

    def get_topics_for_media(self, media_uuid: str) -> str:
        topic_result_de = self._get_object_for_media(media_uuid, "topic_result_de")
        topic_result_en = self._get_object_for_media(media_uuid, "topic_result_en")
        data = []
        if topic_result_de: data.append(json.loads(topic_result_de.decode()))
        if topic_result_en: data.append(json.loads(topic_result_en.decode()))
        return {"data": data}

    def get_markers_for_media(self, media_uuid: str) -> str:
        return self._get_object_for_media(media_uuid, "marker")

    def get_thumbnail_url_from_urn(self, urn: str) -> str:
        thumbnail_timeline_url = self.assetdb_connector.gen_presigned_url(urn)
        thumbnail_timeline_url_mod = self.modify_url_for_db_access(thumbnail_timeline_url)
        return {"data": thumbnail_timeline_url_mod}

    def get_questionnaire_for_media(self, media_uuid: str) -> str:
        questionnaire_result_de = self._get_object_for_media(media_uuid, "questionnaire_result_de")
        questionnaire_result_en = self._get_object_for_media(media_uuid, "questionnaire_result_en")
        data = []
        if questionnaire_result_de: data.append(json.loads(questionnaire_result_de.decode()))
        if questionnaire_result_en: data.append(json.loads(questionnaire_result_en.decode()))
        return {"data": data}

    def get_slides_images_meta_for_media(self, media_uuid: str) -> dict:
        slides_images_meta_result = self._get_object_for_media(media_uuid, "slides_images_meta")
        data = []
        if slides_images_meta_result: data.append(json.loads(slides_images_meta_result.decode()))
        return {"data": data}

    def get_keywords_for_media(self, media_uuid: str) -> dict:
        keywords_result = self._get_object_for_media(media_uuid, "keywords_result")
        data = []
        if keywords_result: data.append(json.loads(keywords_result.decode()))
        return {"data": data}

    def get_documents_for_channel(self, channel_uuid: str) -> dict:
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        channel_meta_data = mongo_connector.get_metadata(f"metadb:meta:post:id:{channel_uuid}")
        if "documents" not in channel_meta_data:
            return {"data": []}
        result = []
        for doc_uuid in channel_meta_data["documents"]:
            doc_meta_data = mongo_connector.get_metadata(f"metadb:meta:post:id:{doc_uuid}")
            res_meta = {
                "uuid": doc_meta_data["uuid"], "filename": doc_meta_data["filename"],
                "mime_type": doc_meta_data["mime_type"], "urn": doc_meta_data["urn"],
                "channel_uuid": doc_meta_data["channel_uuid"], "status": doc_meta_data["status"],
                "visible": doc_meta_data["visible"],
            }
            res_meta = self._activate_access_to_url("urn", res_meta, True, "url")
            result.append(res_meta)
        return {"data": result}

    def search_lectures_standard(self, query, search_credentials, fields=[]):
        if fields is None: fields = []
        return self.opensearch_connector.standard_document_search(query, search_credentials, fields)

    def search_lectures_multi_match(self, query, fields=[]):
        if fields is None: fields = []
        return self.opensearch_connector.search_lectures_multi_match(query, fields)

    def search_recent_lectures(self, search_credentials, amount):
        return self.opensearch_connector.search_recent_lectures(search_credentials, amount)

    def search_channels(self, amount):
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        resultChannels = mongo_connector.get_list_of_metadata_by_type("metadb:meta:post:id:dummy0815", "channel", amount)
        result_data_list = []
        for channel in resultChannels:
            channel.setdefault("surveys", [])
            channel.setdefault("lms_gated_access", False)
            channel.setdefault("lms_gated_access_details", {})
            result_dict = {
                "uuid": channel["uuid"], "course": channel["course"], "course_acronym": channel["course_acronym"],
                "faculty": channel["faculty"], "faculty_acronym": channel["faculty_acronym"],
                "faculty_color": channel["faculty_color"], "language": channel["language"],
                "lecturer": channel["lecturer"], "license": channel["license"],
                "license_url": channel["license_url"], "semester": channel["semester"],
                "tags": channel["tags"], "thumbnails": channel["thumbnails"],
                "university": channel["university"], "university_acronym": channel["university_acronym"],
                "surveys": channel["surveys"], "lms_gated_access": channel["lms_gated_access"],
                "lms_gated_access_details": channel["lms_gated_access_details"],
            }
            lecturer_thumbnail_url = result_dict["thumbnails"]["lecturer"]
            result_dict["thumbnails"]["lecturer"] = self.modify_url_for_db_access(lecturer_thumbnail_url)
            result_data_list.append(json.loads(json.dumps(result_dict)))
        return result_data_list

    def search_media(self, amount):
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        resultMediaFull = mongo_connector.get_list_of_metadata_by_type("metadb:meta:post:id:dummy0815", "media", amount)
        resultMedia = [self.activate_meta_data_access(mediaitem) for mediaitem in resultMediaFull]
        return resultMedia

    # This is the new, flexible search function
    def search_uploaded_media(self, sec_meta_data, channel_uuid: Optional[str] = None, channel_course_acronym: Optional[str] = None):
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        resultMediaFull = []

        if channel_uuid and channel_course_acronym:
            print("SearchUploadedMedia: Filtering by channel")
            resultMediaFull = mongo_connector.get_media_metadata_by_sec_meta_data(channel_uuid, channel_course_acronym, sec_meta_data)
        else:
            print("SearchUploadedMedia: Getting all media for user")
            resultMediaFull = mongo_connector.get_all_media_metadata_by_sec_meta_data(sec_meta_data)
        
        resultMedia = [self.activate_meta_data_access(mediaitem) for mediaitem in resultMediaFull]
        return resultMedia
    
    def search_user_channels(self, sec_meta_data):
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        resultChannelsFull = None
        if sec_meta_data.check_user_has_roles(["admin", "developer"]):
            resultChannelsFull = mongo_connector.get_list_of_metadata_by_type("metadb:meta:post:id:dummy0815", "channel", 1024)
        else:
            resultChannelsFull = mongo_connector.get_channels_metadata_by_sec_meta_data(sec_meta_data)
        
        resultChannels = []
        for channel in resultChannelsFull:
            lecturer_thumbnail_url = channel["thumbnails"]["lecturer"]
            channel["thumbnails"]["lecturer"] = self.modify_url_for_db_access(lecturer_thumbnail_url)
            channel.setdefault("lms_gated_access", False)
            channel.setdefault("lms_gated_access_details", {})
            resultChannels.append(channel)
        return resultChannels

metadata_provider = MetaDataProvider()