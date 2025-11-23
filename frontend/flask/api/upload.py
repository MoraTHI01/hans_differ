#!/usr/bin/env python
"""Upload raw media and slide files to backend """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import os
import io
import json
import subprocess
import tempfile
from uuid import uuid4
from typing import List
from http import HTTPStatus

from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag, FileStorage
from pydantic import BaseModel, Field

from connectors.connector_provider import connector_provider
from connectors.config import get_frontend_host, get_hans_dag_output_connection_ids

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


def validate_video_aspect_ratio(video_file):
    """Validate video has valid streams using ffprobe"""
    try:
        # First check if ffprobe is available
        ffprobe_path = '/usr/bin/ffprobe'
        try:
            subprocess.run([ffprobe_path, '-version'], capture_output=True, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("ffprobe not found or not accessible")
            return False, "Video validation tool (ffprobe) is not available on this system"
        
        # Create a temporary file to store the video data
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            # Write the video data to temporary file
            video_file.seek(0)  # Reset file pointer
            temp_file.write(video_file.read())
            temp_file.flush()
            temp_file_path = temp_file.name
        
        # Run ffprobe command to get aspect ratio information
        cmd = [
            ffprobe_path, 
            '-v', 'error', 
            '-select_streams', 'v:0', 
            '-show_entries', 'stream=sample_aspect_ratio,display_aspect_ratio', 
            '-of', 'json', 
            temp_file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except Exception as e:
            print(f"Warning: Could not delete temporary file {temp_file_path}: {e}")
        
        if result.returncode != 0:
            print(f"ffprobe error: {result.stderr}")
            return False, "Failed to analyze video file"
        
        # Parse the JSON output
        try:
            probe_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print(f"Failed to parse ffprobe JSON output: {e}")
            return False, "Invalid video file - corrupted or unsupported format"
        
        # Check if output is empty {} or streams is empty []
        if not probe_data or not probe_data.get('streams') or len(probe_data['streams']) == 0:
            print("No video streams found in file - invalid or corrupted video")
            return False, "Invalid video file - no video streams detected. The video may be corrupted or in an unsupported format."
        
        # Video has valid streams
        stream = probe_data['streams'][0]
        display_aspect_ratio = stream.get('display_aspect_ratio', 'unknown')
        print(f"Video validation passed - aspect ratio: {display_aspect_ratio}")
        return True, f"Video is valid (aspect ratio: {display_aspect_ratio})"
            
    except subprocess.TimeoutExpired:
        return False, "Video analysis timed out"
    except Exception as e:
        print(f"Error validating video: {e}")
        return False, f"Error analyzing video: {str(e)}"


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

    # Validate video aspect ratio if it's a video file
    if form.media.mimetype.startswith("video/"):
        print("Validating video aspect ratio...")
        is_valid, validation_message = validate_video_aspect_ratio(form.media)
        if not is_valid:
            return ErrorResponse.create_custom(f"Video validation failed: {validation_message}")
        print(f"Video validation passed: {validation_message}")

    # Use the original file directly (no processing)
    form.media.seek(0)
    value_as_a_stream = io.BytesIO(form.media.read())

    metadata = {"X-Amz-Meta-Filename": form.media.filename, "X-Amz-Meta-Language": form.language}

    media_urn = "assetdb:" + "raw:" + uuid
    if form.media.filename.endswith("mp4"):
        media_urn = media_urn + ".mp4"
    elif form.media.filename.endswith("mp3"):
        media_urn = media_urn + ".mp3"
    else:
        media_urn = media_urn + ".mp4"

    print(f"Uploading media file to assetdb with URN: {media_urn}")
    result = assetdb_connector.put_object(media_urn, value_as_a_stream, form.media.mimetype, metadata)
    if result is False:
        return ErrorResponse.create_custom("Error while uploading media file")
    
    print(f"Media file uploaded successfully to: {media_urn}")

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

    return JsonResponse.create({
        "success": True,
        "uuid": uuid,
        "processing_message": "File uploaded successfully"
    })


class UploadDocumentFileForm(BaseModel):
    """API template for file upload"""

    uuid: str = Field(None, description="Identifier of the channel item")
    language: str = Field(None, description="Spoken language identifier of channel, e.g. 'en' or 'de'")
    document: FileStorage = Field(..., description="Uploaded file")
    filename: str = Field(None, description="Document filename on client side")
    mimetype: str = Field(None, description="Document mimetype")


@upload_api_bp.post("/upload-document")
@jwt_required()
def upload_document(form: UploadDocumentFileForm):
    """Upload document files for a channel from vue to backend"""
    # Protect api to only allow uploading for admin user
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin", "developer", "lecturer"]):
        return ErrorForbidden.create()

    print("Upload-Document")
    assetdb_connector = connector_provider.get_assetdb_connector()
    assetdb_connector.connect()
    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()
    airflow_connector = connector_provider.get_airflow_connector()
    airflow_connector.connect()
    file = form.document
    if not file:
        return ErrorResponse.create_custom("No file provided", HTTPStatus.BAD_REQUEST)
    print(f"Document-Channel-UUID: {form.uuid}")
    print(f"Document-Channel-Language: {form.language}")
    # Generate unique UUID for the file
    file_uuid = str(uuid4())
    file_extension = os.path.splitext(form.filename)[1]
    file_urn = "assetdb:" + "assets:" + file_uuid + file_extension
    metadata = {"X-Amz-Meta-Filename": form.filename, "X-Amz-Meta-Language": form.language}

    print(f"Document-Name: {form.filename}")
    print(f"Document-UUID: {file_uuid}")
    print(f"Document-Type: {form.mimetype}")
    print(f"Document-URN: {file_urn}")

    try:
        value_as_a_stream = io.BytesIO(file.read())
        print("Document read!")
        result = assetdb_connector.put_object(file_urn, value_as_a_stream, form.mimetype, metadata)
        if result is False:
            return ErrorResponse.create_custom("Error while uploading document file to assetdb")
        print("Document stored!")
        # Store meta data in mongodb
        file_meta_urn = f"metadb:meta:post:id:{file_uuid}"
        file_entry = {
            "uuid": file_uuid,
            "type": "document",
            "filename": form.filename,
            "mime_type": form.mimetype,
            "urn": file_urn,
            "channel_uuid": form.uuid,
            "status": "Processing",
            "embeddings_urn": "",
            "visible": False,
        }
        file_entry_str = json.dumps(file_entry, indent=4)
        (success, urn_result) = mongo_connector.put_object(
            file_meta_urn, None, "application/json", json.loads(file_entry_str)
        )
        print(urn_result)
        if success is False:
            return ErrorResponse.create_custom("Error while uploading document meta data")
        print("Document entry created!")
        channel_urn = f"metadb:meta:post:id:{form.uuid}"
        channel_data_dict = mongo_connector.get_metadata(channel_urn)
        if not "documents" in channel_data_dict:
            channel_data_dict["documents"] = []
        channel_data_dict["documents"].append(file_uuid)
        channel_data_dict_str = json.dumps(channel_data_dict, indent=4)
        (success, urn_channel_result) = mongo_connector.put_object(
            channel_urn, None, "application/json", json.loads(channel_data_dict_str)
        )
        if success is False:
            return ErrorResponse.create_custom("Error while updating channel meta data")
        print("Document channel entry updated!")
        # Trigger ml-backend airflow job
        # TODO use hostnames from configuration
        document_task_config = {
            "metaUrn": urn_channel_result,
            "input": [
                {
                    "urn": file_urn,
                    "filename": form.filename,
                    "mime-type": form.mimetype,
                    "hans-type": "document",
                    "locale": form.language,  # currently channel language, document specific language does not make real sense?
                }
            ],
            # Providing Airflow CONN_ID's for backend and frontend,
            # see https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html
            "output": [get_hans_dag_output_connection_ids()],
        }

        # TODO: Let the admin select the HAnS airflow DAG
        success = airflow_connector.post_dag_run("embed_channel_documents_v1.0.0", file_uuid, document_task_config)
        if success is False:
            return ErrorResponse.create_custom("Error while triggering airflow document embedding job")
        print("Document processing started!")
        return JsonResponse.create({"message": "Upload successful", "uuid": file_uuid})
    except Exception as e:
        return ErrorResponse.create_custom(f"Upload failed: {str(e)}")


class DocumentStatus(BaseModel):
    file_uuid: str = Field(..., description="Document uuid, same as airflow dag run uuid")


class UploadStatus(BaseModel):
    """API template for upload status check"""

    uuid: str = Field(..., description="Upload UUID to check status for")


@upload_api_bp.get("/process-status/<file_uuid>")
@jwt_required()
def process_status(path: DocumentStatus):
    """Check the processing status of a file"""
    # Protect api to only allow uploading for admin user
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin", "developer", "lecturer"]):
        return ErrorForbidden.create()
    print("Process-Status")
    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()
    airflow_connector = connector_provider.get_airflow_connector()
    airflow_connector.connect()
    print(f"Check process-status of Airflow-DAG-Run UUID: {path.file_uuid}")
    state = airflow_connector.get_dag_run_state("embed_channel_documents_v1.0.0", path.file_uuid)
    # print(state)
    file_urn = f"metadb:meta:post:id:{path.file_uuid}"
    file_data_dict = mongo_connector.get_metadata(file_urn)
    file_status = "Processing"
    if state in ["queued", "running"]:
        file_status = "Processing"
    elif state == "success":
        file_status = "Completed"
    elif state == "failed":
        file_status = "Failed"
    else:
        file_status = "Error"
    file_data_dict["status"] = file_status
    print(f"Process-Status: {file_status}")
    file_data_dict_str = json.dumps(file_data_dict, indent=4)
    (success, urn_channel_result) = mongo_connector.put_object(
        file_urn, None, "application/json", json.loads(file_data_dict_str)
    )
    if success is False:
        return ErrorResponse.create_custom("Error while updating document processing status")

    return JsonResponse.create({"status": file_status})


@upload_api_bp.get("/upload-status/<uuid>")
@jwt_required()
def upload_status(path: UploadStatus):
    """Check the upload and processing status of a media file"""
    # Protect api to only allow checking for admin user
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    if not sec_meta_data.check_user_has_roles(["admin", "developer", "lecturer"]):
        return ErrorForbidden.create()

    print(f"Check upload-status of UUID: {path.uuid}")

    try:
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        airflow_connector = connector_provider.get_airflow_connector()
        airflow_connector.connect()

        # Get metadata from MongoDB
        meta_urn = f"metadb:meta:post:id:{path.uuid}"
        meta_data = mongo_connector.get_metadata(meta_urn)

        if not meta_data:
            return ErrorResponse.create_custom("Upload not found", HTTPStatus.NOT_FOUND)

        # Get Airflow DAG run status
        dag_state = airflow_connector.get_dag_run_state("hans_v1.0.3", path.uuid)

        # Determine overall status
        overall_status = "unknown"
        processing_progress = 0

        if dag_state in ["queued", "running"]:
            overall_status = "processing"
            processing_progress = 50  # Approximate progress during processing
        elif dag_state == "success":
            overall_status = "completed"
            processing_progress = 100
        elif dag_state == "failed":
            overall_status = "failed"
            processing_progress = 0
        else:
            overall_status = "error"
            processing_progress = 0

        # Get state from metadata if available
        if "state" in meta_data:
            state_info = meta_data["state"]
            if "overall_step" in state_info:
                overall_status = state_info["overall_step"].lower()
            if "editing_progress" in state_info:
                processing_progress = state_info["editing_progress"]

        return JsonResponse.create({
            "uuid": path.uuid,
            "status": overall_status,
            "progress": processing_progress,
            "dag_state": dag_state,
            "message": f"Upload is {overall_status}"
        })

    except Exception as e:
        return ErrorResponse.create_custom(f"Error checking upload status: {str(e)}")
