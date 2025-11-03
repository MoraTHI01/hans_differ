#!/usr/bin/env python
"""Manage channels """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"

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


channel_api_bp = APIBlueprint(
    "channels",
    __name__,
    abp_security=SecurityConfiguration().get_security(),
    abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
)


# BEGIN EXPERIMENTAL DEFINITION
class ChannelItemThumbnails(BaseModel):
    """API template for channel item thumbnails"""

    lecturer: str = Field(None, description="Thumbnail id for the lecturer of the channel item")


class ChannelItem(BaseModel):
    """API template for channel item"""

    uuid: str = Field(None, description="Identifier of the channel item")
    course: str = Field(None, description="Name of the course of the channel item")
    course_acronym: str = Field(None, description="Acronym for the course of the channel item")
    faculty: str = Field(None, description="Faculty of the course")
    faculty_acronym: str = Field(None, description="Faculty acronym of the course")
    faculty_color: str = Field(None, description="Faculty color")
    language: str = Field(None, description="Spoken language identifier, e.g. 'en' or 'de'")
    lecturer: str = Field(None, description="Lecturer of the course")
    license: str = Field(None, description="License of the channel item")
    license_url: str = Field(None, description="License url to download the license file")
    semester: str = Field(None, description="Semester of the course")
    tags: List[str] = Field(None, description="List of tags associated with the channel item")
    thumbnails: ChannelItemThumbnails = Field(None, description="Thumbnails for the channel item")
    university: str = Field(None, description="University of the course")
    university_acronym: str = Field(None, description="University acronym of the course")


class ChannelItemResponse(BaseModel):
    """API template for channel item response"""

    result: List[ChannelItem] = Field(None, description="List of channel items")


# END EXPERIMENTAL DEFINITION


create_channel_tag = Tag(name="create channel", description="Create channel")


class CreateChannelForm(BaseModel):
    """API template for create channel form"""

    language: str = Field(None, description="Spoken language identifier, supported identifiers: 'en', 'de'")
    # description
    course: str = Field(None, description="Name of the course of the media file")
    course_acronym: str = Field(None, description="Acronym for the course of the media file")
    semester: str = Field(None, description="Semester of the course")
    lecturer: str = Field(None, description="Lecturer of the course")
    faculty: str = Field(None, description="Faculty of the course")
    faculty_acronym: str = Field(None, description="Faculty acronym of the course")
    faculty_color: str = Field(None, description="Faculty color")
    university: str = Field(None, description="University of the course")
    university_acronym: str = Field(None, description="University acronym of the course")
    license: str = Field(None, description="License of the channel")
    license_url: str = Field(None, description="License url to download the license file")
    tags: str = Field(None, description="List of comma seperated tags")
    thumbnails_lecturer: str = Field(None, description="Thumbnail id of the lecturer, avatar picture")
    # Optional
    archive_channel_content: bool = Field(
        None, description="Archive channel content, creates channel package on ml-backend"
    )


def wrap_form_boolean(value):
    """Helper to handle empty boolean form values"""
    if value is None:
        return False
    else:
        return value


def get_channel_entry(form: CreateChannelForm, uuid):
    """
    Helper to create a channel entry dict

    :param CreateChannelForm form: Meta data
    :param str uuid: UUID of the channel

    :return: dict Channel meta data
    """
    return {
        "uuid": uuid,
        # Used to filter by type entry
        "type": "channel",
        "course": form.course,
        "course_acronym": form.course_acronym,
        "faculty": form.faculty,
        "faculty_acronym": form.faculty_acronym,
        "faculty_color": form.faculty_color,
        "language": form.language,
        "lecturer": form.lecturer,
        "license": form.license,
        "license_url": form.license_url,
        "semester": form.semester,
        "tags": form.tags.split(","),
        "thumbnails": {"lecturer": form.thumbnails_lecturer},
        "university": form.university,
        "university_acronym": form.university_acronym,
    }


def trigger_airflow_dag(form: CreateChannelForm, uuid):
    """
    Helper to trigger ml-backend airflow job

    :param CreateChannelForm form: Meta data
    :param str uuid: UUID of the channel

    :return: bool True if successful, False otherwise
    """

    create_channel_task_config = {
        "token": {"type": "BearerToken", "apiAccessToken": "an OAuth2 bearer token", "expiresIn": 259200},
        "channel": get_channel_entry(form, uuid),
        # Providing Airflow CONN_ID's for backend and frontend,
        # see https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html
        "output": [get_hans_dag_output_connection_ids()],
    }
    airflow_connector = connector_provider.get_airflow_connector()
    airflow_connector.connect()
    # TODO: Let the admin select the HAnS airflow DAG
    return airflow_connector.post_dag_run("create_hans_channel_package_v1.0.0", uuid, create_channel_task_config)


def create_channel_meta_data(form: CreateChannelForm, uuid):
    """
    Helper to create meta data in mongodb

    :param CreateChannelForm form: Meta data
    :param str uuid: UUID of the channel

    :return: bool True if successful, False otherwise
    """
    my_entry = get_channel_entry(form, uuid)
    my_entry_str = json.dumps(my_entry, indent=4)
    return add_channel_meta_data(uuid, my_entry_str)


def add_channel_meta_data(uuid, meta_data_str):
    """
    Helper to add meta data in mongodb

    :param str uuid: UUID of the channel
    :param str meta_data_str: Meta data of the channel

    :return: bool True if successful, False otherwise
    """
    print("Adding channel meta data")
    # print(meta_data_str, sys.stderr)
    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()
    urn_input = f"metadb:meta:post:id:{uuid}"
    (success, urn_result) = mongo_connector.put_object(urn_input, None, "application/json", json.loads(meta_data_str))
    # mongo_connector.disconnect()
    if success is True:
        return urn_result
    else:
        return None


@channel_api_bp.post("/createChannel", tags=[create_channel_tag])
@jwt_required()
def create_channel(form: CreateChannelForm):
    """Create a new channel on backend"""
    # Protect api to only allow creation of channels for admin user
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin"]):
        return ErrorForbidden.create()

    print("CreateChannel")
    # print("CreateChannel: Received data:")
    # print(form)
    uuid = str(uuid4())

    # Store meta data in mongodb
    meta_urn = create_channel_meta_data(form, uuid)
    if meta_urn is None:
        return ErrorResponse.create_custom("Error while creating channel")

    # If optional archive_channel_content set
    if wrap_form_boolean(form.archive_channel_content):
        # Trigger ml-backend airflow job
        success = trigger_airflow_dag(form, uuid)
        if success is False:
            return ErrorResponse.create_custom("Error while triggering airflow job")

    return JsonResponse.create({"success": True})
