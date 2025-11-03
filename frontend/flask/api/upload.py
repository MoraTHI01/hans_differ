#!/usr/bin/env python
"""Upload raw media and slide files to backend """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import io
import json
from uuid import uuid4
from typing import List

from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag, FileStorage
from pydantic import BaseModel, Field

from api.modules.config import get_frontend_host, get_hans_dag_output_connection_ids
from api.modules.connectors.connector_provider import connector_provider
from api.modules.responses import ErrorForbidden, UnauthorizedResponse, RefreshAuthenticationRequired
from api.modules.responses import ErrorResponse, JsonResponse
from api.modules.security import SecurityConfiguration, SecurityMetaData


upload_api_bp = APIBlueprint(
    "upload",
    __name__,
    abp_security=SecurityConfiguration().get_security(),
    abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
)


# BEGIN EXPERIMENTAL DEFINITION
class MediaItemThumbnails(BaseModel):
    """API template for media item thumbnails"""

    media: str = Field(None, description="Presigned url to the thumbnail for the media item")
    lecturer: str = Field(None, description="Thumbnail id for the lecturer of the media item")


class MediaItemDescription(BaseModel):
    """API template for media item description"""

    course: str = Field(None, description="Name of the course of the media item")
    course_acronym: str = Field(None, description="Acronym for the course of the media item")
    semester: str = Field(None, description="Semester of the course")
    lecturer: str = Field(None, description="Lecturer of the course")
    faculty: str = Field(None, description="Faculty of the course")
    faculty_acronym: str = Field(None, description="Faculty acronym of the course")
    faculty_color: str = Field(None, description="Faculty color")
    university: str = Field(None, description="University of the course")
    university_acronym: str = Field(None, description="University acronym of the course")


class MediaItem(BaseModel):
    """API template for media item"""

    uuid: str = Field(None, description="Identifier of the media item")
    media: str = Field(None, description="Presigned url to stream media")
    title: str = Field(None, description="Title of the media item")
    slides: str = Field(None, description="Presigned url to download the slides file")
    transcript: str = Field(None, description="Presigned url to download the transcript file")
    language: str = Field(None, description="Spoken language identifier, e.g. 'en' or 'de'")
    description: MediaItemDescription = Field(None, description="Description of the media content")
    thumbnails: MediaItemThumbnails = Field(None, description="Thumbnails for the media content")
    tags: List[str] = Field(
        None, description="List of tags associated with the media item, used to appear in specific channels"
    )


class MediaItemResponse(BaseModel):
    """API template for media item response"""

    result: List[MediaItem] = Field(None, description="List of media items")


# END EXPERIMENTAL DEFINITION


upload_tag = Tag(name="upload media", description="Upload media content")


class UploadFileForm(BaseModel):
    """API template for submit upload form"""

    media: FileStorage = Field(None, description="Media file, supported formats: 'mp4', 'mp3'")
    slides: FileStorage = Field(None, description="Slides file, supported formats: 'pdf'")
    language: str = Field(None, description="Spoken language identifier, supported identifiers: 'en', 'de'")
    # description
    title: str = Field(None, description="Title of the media file")
    course: str = Field(None, description="Name of the course of the media file")
    course_acronym: str = Field(None, description="Acronym for the course of the media file")
    semester: str = Field(None, description="Semester of the course")
    lecturer: str = Field(None, description="Lecturer of the course")
    faculty: str = Field(None, description="Faculty of the course")
    faculty_acronym: str = Field(None, description="Faculty acronym of the course")
    faculty_color: str = Field(None, description="Faculty color")
    university: str = Field(None, description="University of the course")
    university_acronym: str = Field(None, description="University acronym of the course")
    # permissions
    permission_public: bool = Field(None, description="Permission for public access")
    permission_university_only: bool = Field(None, description="Permission only university members have access")
    permission_faculty_only: bool = Field(None, description="Permission only faculty members have access")
    permission_study_topic_only: bool = Field(
        None, description="Permission only students with specific study topic have access"
    )
    permission_students_only: bool = Field(None, description="Permission only students have access")
    # licenses
    license_cc_0: bool = Field(None, description="CC0 1.0 Universal (CC0 1.0) Public Domain Dedication license")
    license_cc_by_4: bool = Field(None, description="Attribution 4.0 International (CC BY 4.0) license")
    license_cc_by_sa_4: bool = Field(
        None, description="Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) license"
    )
    tags: str = Field(
        None,
        description="List of comma seperated tags, if a channel tag is specified media item appears in a specific channel",
    )
    thumbnails_lecturer: str = Field(None, description="Thumbnail id of the lecturer, avatar picture")


def wrap_form_boolean(value):
    """Helper to handle empty boolean form values"""
    if value is None:
        return False
    else:
        return value


def upload_meta_data(form: UploadFileForm, uuid, media_urn, slides_urn):
    """Helper to store meta data in mongodb"""
    my_entry = {
        "uuid": uuid,
        # Used to filter by type entry
        "type": "media",
        # raw entries should not be propagated back to the client!
        "raw_media": media_urn,
        "raw_slides": slides_urn,
        "title": form.title,
        "language": form.language,
        "state": {"overall_step": "PROCESSING", "editing_progress": 0, "published": False, "listed": False},
        "description": {
            "course": form.course,
            "course_acronym": form.course_acronym,
            "semester": form.semester,
            "lecturer": form.lecturer,
            "faculty": form.faculty,
            "faculty_acronym": form.faculty_acronym,
            "faculty_color": form.faculty_color,
            "university": form.university,
            "university_acronym": form.university_acronym,
        },
        "tags": form.tags.split(","),
        "thumbnails": {
            "media": "<MEDIA THUMBNAIL URL WILL BE CREATED BY AIRFLOW DAG>.png",
            "lecturer": form.thumbnails_lecturer,
        },
        "permissions": [
            {"type": "public", "value": wrap_form_boolean(form.permission_public)},
            {"type": "universityOnly", "value": wrap_form_boolean(form.permission_university_only)},
            {"type": "facultyOnly", "value": wrap_form_boolean(form.permission_faculty_only)},
            {"type": "studyTopicOnly", "value": wrap_form_boolean(form.permission_study_topic_only)},
            {"type": "studentsOnly", "value": wrap_form_boolean(form.permission_students_only)},
        ],
        "licenses": [
            {
                "type": "CC0-1.0",
                "name": "CC0 1.0 Universal Public Domain Dedication",
                "acronym": "CC0 1.0",
                "url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "value": wrap_form_boolean(form.license_cc_0),
            },
            {
                "type": "CC-BY-4.0",
                "name": "Attribution 4.0 International",
                "acronym": "CC BY 4.0",
                "url": "https://creativecommons.org/licenses/by/4.0/",
                "value": wrap_form_boolean(form.license_cc_by_4),
            },
            {
                "type": "CC-BY-SA-4.0",
                "name": "Attribution-ShareAlike 4.0 International",
                "acronym": "CC BY-SA 4.0",
                "url": "https://creativecommons.org/licenses/by-sa/4.0/",
                "value": wrap_form_boolean(form.license_cc_by_sa_4),
            },
        ],
    }
    my_entry_str = json.dumps(my_entry, indent=4)
    # print(my_entry_str, sys.stderr)
    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()
    urn_input = f"metadb:meta:post:id:{uuid}"
    (success, urn_result) = mongo_connector.put_object(urn_input, None, "application/json", json.loads(my_entry_str))
    # mongo_connector.disconnect()
    if success is True:
        return urn_result
    else:
        return None


def trigger_airflow_dag(form: UploadFileForm, uuid, media_urn, slides_urn, meta_urn):
    """Helper to trigger ml-backend airflow job"""
    hans_type = "video"
    if form.media.mimetype.startswith("audio"):
        hans_type = "podcast"

    # TODO use hostnames from configuration
    annotation_task_config = {
        "metaUrn": meta_urn,
        "input": [
            {
                "urn": media_urn,
                "filename": form.media.filename,
                "mime-type": form.media.mimetype,
                "hans-type": hans_type,
                "locale": form.language,
            },
            {
                "urn": slides_urn,
                "filename": form.slides.filename,
                "mime-type": form.slides.mimetype,
                "hans-type": "slides",
                "locale": form.language,
            },
        ],
        # Providing Airflow CONN_ID's for backend and frontend,
        # see https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html
        "output": [get_hans_dag_output_connection_ids()],
    }
    airflow_connector = connector_provider.get_airflow_connector()
    airflow_connector.connect()
    # TODO: Let the admin select the HAnS airflow DAG
    return airflow_connector.post_dag_run("hans_v1.0.3", uuid, annotation_task_config)


# REQUESTS FROM FRONTEND


@upload_api_bp.post("/upload", tags=[upload_tag])
@jwt_required()
def upload_file(form: UploadFileForm):
    """Upload raw media files from vue to backend"""
    # Protect api to only allow uploading for admin user
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin"]):
        return ErrorForbidden.create()

    print("Upload")
    assetdb_connector = connector_provider.get_assetdb_connector()
    assetdb_connector.connect()

    uuid = str(uuid4())

    # Store media file
    # TODO: bug is here on some media files, showing latin-1 encoding byte issue
    value_as_a_stream = io.BytesIO(form.media.read())
    metadata = {"X-Amz-Meta-Filename": form.media.filename, "X-Amz-Meta-Language": form.language}

    media_urn = "assetdb:" + "raw:" + uuid
    if form.media.filename.endswith("mp4"):
        media_urn = media_urn + ".mp4"
    elif form.media.filename.endswith("mp3"):
        media_urn = media_urn + ".mp3"
    else:
        media_urn = media_urn + ".mp4"

    result = assetdb_connector.put_object(media_urn, value_as_a_stream, form.media.mimetype, metadata)
    if result is False:
        return ErrorResponse.create_custom("Error while uploading media file")

    # Store slides file
    # TODO: maybe here is also an issue on some slide files, showing latin-1 encoding byte issue?
    slides_value_as_a_stream = io.BytesIO(form.slides.read())
    slides_metadata = {"X-Amz-Meta-Filename": form.slides.filename, "X-Amz-Meta-Language": form.language}
    slides_urn = "assetdb:" + "raw:" + uuid + ".pdf"
    slides_result = assetdb_connector.put_object(
        slides_urn, slides_value_as_a_stream, form.slides.mimetype, slides_metadata
    )
    if slides_result is False:
        return ErrorResponse.create_custom("Error while uploading slides file")

    # Store meta data in mongodb
    meta_urn = upload_meta_data(form, uuid, media_urn, slides_urn)
    if meta_urn is None:
        return ErrorResponse.create_custom("Error while uploading meta data")

    # Trigger ml-backend airflow job
    success = trigger_airflow_dag(form, uuid, media_urn, slides_urn, meta_urn)
    if success is False:
        return ErrorResponse.create_custom("Error while triggering airflow job")

    return JsonResponse.create({"success": True})
