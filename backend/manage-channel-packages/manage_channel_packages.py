#!/usr/bin/env python
"""
Helper to manage channel packages on HAnS backend

Available Features:
  --clean-db              Cleanup all channel packages from database
  --list-db               List all channel packages in database
  --clean-db-with-log     List all channel packages and then delete them all
  --list-host             List channel packages in host packages folder
  --download --file FILE  Download a specific channel package from database
  --install --file FILE   Install a specific channel package from host folder
  --no-extraction         Skip extraction when installing (manual extraction required)

Examples:
  python manage_channel_packages.py --list-db
  python manage_channel_packages.py --clean-db-with-log
  python manage_channel_packages.py --install --file my_package.tar.gz
  python manage_channel_packages.py --download --file my_package.tar.gz
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import sys
import os
import argparse
import json
import requests
from datetime import datetime

from minio.error import S3Error, InvalidResponseError
from urllib3.exceptions import RequestError

from connectors.connector_provider import connector_provider
from connectors.storage_connector import StorageConnector


def show_comprehensive_help():
    """
    Display comprehensive help information for all available features
    """
    help_text = """
HAnS Channel Package Manager
============================

This script helps manage channel packages on the HAnS backend system.

AVAILABLE COMMANDS:
==================

Database Management:
  --clean-db                    Remove all channel packages from the database
  --list-db                     Display all channel packages currently in the database
  --list-db-with-datetime       Display all channel packages with their creation times
  --list-db-with-datetime-sorted Display all channel packages with creation times (sorted newest first)
  --clean-db-with-log          List all packages and then delete them (shows what will be deleted)

Host Management:
  --list-host             Show all channel package files in the host packages folder

Package Operations:
  --download --file FILE  Download a specific channel package from database to host
  --install --file FILE   Install a channel package from host folder to the system
  --no-extraction         Skip automatic extraction (requires manual extraction)

USAGE EXAMPLES:
==============

List all packages in database:
  python manage_channel_packages.py --list-db

List all packages with creation times:
  python manage_channel_packages.py --list-db-with-datetime

List all packages with creation times (sorted newest first):
  python manage_channel_packages.py --list-db-with-datetime-sorted

List and delete all packages:
  python manage_channel_packages.py --clean-db-with-log

Install a package:
  python manage_channel_packages.py --install --file my_channel_package.tar.gz

Download a package:
  python manage_channel_packages.py --download --file my_channel_package.tar.gz

Install without automatic extraction:
  python manage_channel_packages.py --install --file my_package.tar.gz --no-extraction

NOTES:
======
- Channel packages are stored as .tar.gz files
- The --no-extraction flag is useful when you have permission issues
- When using --no-extraction, you must manually extract the package first
- All operations require proper database connectivity
"""
    print(help_text)


def cleanup_channel_packages(assetdb_connector):
    """
    Cleanup all channel packages on assetdb

    :param assetdb_connector assetdb_connector: assetdb_connector
    """
    result = assetdb_connector.delete_all_objects_in_bucket("packages")
    if result is True:
        print("Cleanup channel packages successful")
    else:
        print("Error cleanup channel packages!")
        sys.exit(-1)


def delete_all_list_channel_packages(assetdb_connector):
    """
    List all channel packages on assetdb and then delete them all

    :param assetdb_connector assetdb_connector: assetdb_connector
    """
    channel_packages_gen = assetdb_connector.list_objects_on_bucket("packages", "")
    if channel_packages_gen is not None:
        channel_packages_list = list(channel_packages_gen)
        print(f"Found {len(channel_packages_list)} channel packages:")
        for channel_package in channel_packages_list:
            print(f"  - {channel_package.object_name}")

        if len(channel_packages_list) > 0:
            print(f"\nDeleting all {len(channel_packages_list)} channel packages...")
            result = assetdb_connector.delete_all_objects_in_bucket("packages")
            if result is True:
                print("Successfully deleted all channel packages")
            else:
                print("Error deleting channel packages!")
                sys.exit(-1)
        else:
            print("No channel packages to delete")
    else:
        print("No channel packages found")


def list_channel_packages(assetdb_connector):
    """
    List all channel packages on assetdb

    :param assetdb_connector assetdb_connector: assetdb_connector
    """
    channel_packages_gen = assetdb_connector.list_objects_on_bucket("packages", "")
    if channel_packages_gen is not None:
        channel_packages_list = list(channel_packages_gen)
        print(f"total {len(channel_packages_list)}")
        for channel_package in channel_packages_list:
            print(channel_package.object_name)
    else:
        print("total 0")


def list_channel_packages_with_datetime(assetdb_connector):
    """
    List all channel packages on assetdb with their creation times

    :param assetdb_connector assetdb_connector: assetdb_connector
    """
    channel_packages_gen = assetdb_connector.list_objects_on_bucket("packages", "")
    if channel_packages_gen is not None:
        channel_packages_list = list(channel_packages_gen)
        print(f"total {len(channel_packages_list)}")
        print(f"{'Package Name':<50} {'Created Date':<20} {'Created Time':<20}")
        print("-" * 90)
        for channel_package in channel_packages_list:
            # Get the last_modified time from the object
            created_time = channel_package.last_modified
            if created_time:
                # Format the datetime for display
                created_date = created_time.strftime("%Y-%m-%d")
                created_time_str = created_time.strftime("%H:%M:%S")
                print(f"{channel_package.object_name:<50} {created_date:<20} {created_time_str:<20}")
            else:
                # If no creation time available, show unknown
                print(f"{channel_package.object_name:<50} {'Unknown':<20} {'Unknown':<20}")
    else:
        print("total 0")


def list_channel_packages_with_datetime_sorted(assetdb_connector):
    """
    List all channel packages on assetdb with their creation times, sorted by date/time in descending order

    :param assetdb_connector assetdb_connector: assetdb_connector
    """
    channel_packages_gen = assetdb_connector.list_objects_on_bucket("packages", "")
    if channel_packages_gen is not None:
        channel_packages_list = list(channel_packages_gen)

        # Create a list of tuples with (package, created_time) for sorting
        packages_with_time = []
        for channel_package in channel_packages_list:
            created_time = channel_package.last_modified
            if created_time:
                packages_with_time.append((channel_package, created_time))
            else:
                # Put packages without time at the end
                packages_with_time.append((channel_package, datetime.min))

        # Sort by created_time in descending order (newest first)
        packages_with_time.sort(key=lambda x: x[1], reverse=True)

        print(f"total {len(channel_packages_list)}")
        print(f"{'Package Name':<50} {'Created Date':<20} {'Created Time':<20}")
        print("-" * 90)

        for channel_package, created_time in packages_with_time:
            if created_time != datetime.min:
                # Format the datetime for display
                created_date = created_time.strftime("%Y-%m-%d")
                created_time_str = created_time.strftime("%H:%M:%S")
                print(f"{channel_package.object_name:<50} {created_date:<20} {created_time_str:<20}")
            else:
                # If no creation time available, show unknown
                print(f"{channel_package.object_name:<50} {'Unknown':<20} {'Unknown':<20}")
    else:
        print("total 0")


def download_channel_package(assetdb_connector, channel_package_file):
    """
    Download a channel package to host packages folder

    :param assetdb_connector assetdb_connector: assetdb_connector
    :param str channel_package_file: Channel package file to download,
    e.g. 6a31edcc-1b34-4343-bed7-047a1cf36383.tar.gz
    """
    try:
        response = assetdb_connector.get_object_on_bucket("packages", channel_package_file)
        with open("/channel-packages/" + channel_package_file, "wb") as f:
            f.write(response.data)
    except (S3Error, InvalidResponseError, RequestError) as err:
        print("Error")
        print(err)
        sys.exit(-1)
    finally:
        response.close()
        response.release_conn()


def transfer_file_to_remote(
    assetdb_connector, mediadb_connector, upload_file, upload_filename, upload_urn, content_type
):
    """
    Helper to transfer byte data from download url to upload url for an artefact.

    :param assetdb_connector assetdb_connector: assetdb_connector
    :param mediadb_connector mediadb_connector: mediadb_connector
    :param str upload_file: Upload file path
    :param str upload_filename: Filename of the upload file
    :param str upload_urn: URN to upload data, e.g. to assetdb on HAnS backend
    :param dict content_type: Content type of the file
    """

    connector = None
    if "assetdb" in upload_urn:
        connector = assetdb_connector
    elif "mediadb" in upload_urn:
        connector = mediadb_connector

    metadata = {"X-Amz-Meta-Filename": upload_filename, "Content-Type": content_type}
    (success, result_object_name) = connector.fput_object(upload_urn, upload_file, content_type, metadata)

    if success is False:
        print("Error uploading file: " + upload_filename)
    else:
        print(f"Created {result_object_name}")
    return success


def cleanup_old_package(channel_package_json, cleanup_json, mediadb_connector, assetdb_connector, mongo_connector):
    """
    Cleanup previous old package data on databases
    """
    print("Cleanup old package")
    opensearch_connector = connector_provider.get_opensearch_connector()
    opensearch_connector.connect()

    # Delete searchengine data
    for id in cleanup_json["searchengine"]["ids"]:
        if not opensearch_connector.delete_lecture_document(id):
            print(f"Error deleting opensearch document with id: {id}")
        data_dict = mongo_connector.get_metadata(f"metadb:meta:post:id:{id}")
        if "search_data" in data_dict:
            urn = data_dict["search_data"]
            if not assetdb_connector.delete_object_by_urn(urn):
                print(f"Error deleting assetdb asset {urn}!")
        if "search_data_vectors" in data_dict:
            urn = data_dict["search_data_vectors"]
            if not assetdb_connector.delete_object_by_urn(urn):
                print(f"Error deleting assetdb asset {urn}!")
            if "slides_images_meta" in data_dict:
                urn = data_dict["slides_images_meta"]
                if not assetdb_connector.delete_object_by_urn(urn):
                    print(f"Error deleting assetdb asset {urn}!")
                urn_root = data_dict["slides_images_meta"].rsplit("/")[0]
                if not assetdb_connector.delete_folder_in_bucket("assets", urn_root):
                    print(f"Error deleting assetdb folder in bucket {urn_root}!")
            if not opensearch_connector.delete_all_vector_entries_of_lecture(id):
                print(f"Error deleting opensearch vectors with id: {id}")

    # Delete metadb data
    course_acronym = channel_package_json["course_acronym"]
    if not mongo_connector.remove_metadata_by_filter("meta", "post", {"course_acronym": course_acronym}):
        print(f"Error deleting metadb channel: {course_acronym}")
    for uuid in cleanup_json["metadb"]["uuids"]:
        if not mongo_connector.remove_metadata(f"metadb:meta:post:id:{uuid}"):
            print(f"Error deleting metadb data with uuid: {uuid}")

    # Delete mediadb data
    if "mediadb" in cleanup_json and "videos" in cleanup_json["mediadb"]:
        for folder_name in cleanup_json["mediadb"]["videos"]:
            if not mediadb_connector.delete_folder_in_bucket("videos", folder_name):
                print(f"Error deleting mediadb videos folder: {folder_name}")
    else:
        print("Warning: No mediadb videos to cleanup!")

    # Delete assetdb data
    if "assetdb" in cleanup_json and "assets" in cleanup_json["assetdb"]:
        if not assetdb_connector.delete_objects_in_bucket("assets", cleanup_json["assetdb"]["assets"]):
            print("Error deleting assetdb assets!")
    else:
        print("Warning: No assetdb assets to cleanup!")

    print("Cleanup old package finished!")
    input("Press any key to continue installation...")


def install_channel_package(assetdb_connector, channel_package_file, skip_extraction=False):
    """
    Install a channel package on the backend

    :param assetdb_connector assetdb_connector: assetdb_connector
    :param str channel_package_file: Channel package file to install,
    e.g. 6a31edcc-1b34-4343-bed7-047a1cf36383.tar.gz
    :param bool skip_extraction: Skip extraction of channel package archive
    """
    print(f"Installing {channel_package_file}")

    channel_package_folder = channel_package_file.split(".")[0]
    channel_package_folder_path = os.path.join("/channel-packages", channel_package_folder)

    if skip_extraction is False:
        if os.path.exists(channel_package_folder_path):
            os.system(f"cd /channel-packages && rm -Rf {channel_package_folder}")
        print(f"Extracting {channel_package_file} on host")
        os.system(
            f"cd /channel-packages && mkdir {channel_package_folder} && tar -xvf {channel_package_file} -C {channel_package_folder}"
        )
    else:
        print("Skipping extraction, please ensure you have extracted the channel package on host!")

    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()
    mediadb_connector = connector_provider.get_mediadb_connector()
    mediadb_connector.connect()

    channel_package_json_path = f"/channel-packages/{channel_package_folder}/channel.json"
    channel_package_data = {}
    channel_uuid = ""
    with open(channel_package_json_path, encoding="utf-8") as f:
        channel_package_data = json.load(f)
        channel_uuid = channel_package_data["uuid"]

    cleanup_file_path = os.path.join(channel_package_folder_path, "cleanup.json")
    if os.path.exists(cleanup_file_path) and os.path.isfile(cleanup_file_path):
        print("Update package")
        with open(cleanup_file_path, encoding="utf-8") as f:
            cleanup_old_package(
                channel_package_data, json.load(f), mediadb_connector, assetdb_connector, mongo_connector
            )

    print("Installing sub lectures of channel:")
    for subdir in os.listdir(channel_package_folder_path):
        subpath = os.path.join(channel_package_folder_path, subdir)
        if os.path.isdir(subpath):
            print("Current dir: %s", subdir)
            # analyze
            curr_meta_data_lecture = {}
            curr_meta_data_urns = {}
            curr_meta_data_lecture_uuid = ""
            curr_thumbnails_media_urn = ""
            curr_slides_images_meta_urn = ""
            curr_thumbnails_lecturer_urn = ""
            for file in os.listdir(subpath):
                if file.endswith(".meta.json"):
                    current_file_path = os.path.join(subpath, file)
                    print("Current meta.json file: %s", current_file_path)
                    with open(current_file_path, encoding="utf-8") as f:
                        artefact_meta_data = json.load(f)
                        is_folder = artefact_meta_data["is_folder"]
                        hans_type = artefact_meta_data["hans_type"].upper()
                        print("HAnS type: %s", hans_type)
                        if is_folder is False:
                            if hans_type == "META_DATA":
                                # meta data resides in meta db and needs additional entries
                                meta_data_file = os.path.join(subpath, artefact_meta_data["artefact_file"])
                                with open(meta_data_file, encoding="utf-8") as f:
                                    curr_meta_data_lecture = json.load(f)
                                curr_meta_data_lecture_uuid = artefact_meta_data["artefact_file"].split(".")[0]
                            else:
                                urn = StorageConnector.create_urn(
                                    artefact_meta_data["destination_database"],
                                    artefact_meta_data["destination_bucket"],
                                    artefact_meta_data["artefact_file"],
                                )
                                if hans_type == "THUMBNAILS_MEDIA":
                                    curr_thumbnails_media_urn = urn
                                elif hans_type == "SLIDES_IMAGES_META":
                                    curr_slides_images_meta_urn = urn
                                elif hans_type == "THUMBNAILS_LECTURER":
                                    curr_thumbnails_lecturer_urn = urn
                                else:
                                    curr_meta_data_urns[hans_type.lower()] = urn

                                content_type = artefact_meta_data["mime_type"]
                                upload_file = os.path.join(subpath, artefact_meta_data["artefact_file"])
                                result = transfer_file_to_remote(
                                    assetdb_connector,
                                    mediadb_connector,
                                    upload_file,
                                    artefact_meta_data["artefact_file"],
                                    urn,
                                    content_type,
                                )
                                if result is False:
                                    sys.exit(-1)
                        else:
                            if hans_type == "MEDIA":
                                print("Media files")
                                media_root_path = os.path.join(subpath, artefact_meta_data["artefact_file"])
                                for media_file in os.listdir(media_root_path):
                                    print(media_file)
                                    # Default: application/octet-stream
                                    media_file_sub_path = os.path.join(artefact_meta_data["artefact_file"], media_file)
                                    print("FileSubPath: %s", media_file_sub_path)
                                    urn = StorageConnector.create_urn(
                                        artefact_meta_data["destination_database"],
                                        artefact_meta_data["destination_bucket"],
                                        media_file_sub_path,
                                    )
                                    content_type = artefact_meta_data["mime_type"]
                                    if media_file.endswith(".mpd"):
                                        content_type = "application/dash+xml"
                                        curr_meta_data_urns[hans_type.lower()] = urn
                                    elif media_file.endswith(".m4s"):
                                        content_type = "video/mp4"

                                    upload_file = os.path.join(subpath, media_file_sub_path)
                                    result = transfer_file_to_remote(
                                        assetdb_connector,
                                        mediadb_connector,
                                        upload_file,
                                        media_file_sub_path,
                                        urn,
                                        content_type,
                                    )
                                    if result is False:
                                        sys.exit(-1)
                            elif hans_type == "THUMBNAILS_MEDIA":
                                print("Thumbnail files")
                                thumbnail_root_path = os.path.join(subpath, artefact_meta_data["artefact_file"])
                                for thumbnail_file in os.listdir(thumbnail_root_path):
                                    print(thumbnail_file)
                                    # Default: application/octet-stream
                                    thumbnail_file_sub_path = os.path.join(
                                        artefact_meta_data["artefact_file"], thumbnail_file
                                    )
                                    print("FileSubPath: %s", thumbnail_file_sub_path)
                                    urn = StorageConnector.create_urn(
                                        artefact_meta_data["destination_database"],
                                        artefact_meta_data["destination_bucket"],
                                        thumbnail_file_sub_path,
                                    )
                                    if ".json" in thumbnail_file_sub_path:
                                        content_type = "application/json"
                                    elif ".png" in thumbnail_file_sub_path:
                                        content_type = "image/png"
                                    else:
                                        content_type = artefact_meta_data["mime_type"]
                                    if thumbnail_file.endswith(".thumb.png"):
                                        curr_thumbnails_media_urn = urn

                                    upload_file = os.path.join(subpath, thumbnail_file_sub_path)
                                    result = transfer_file_to_remote(
                                        assetdb_connector,
                                        mediadb_connector,
                                        upload_file,
                                        thumbnail_file_sub_path,
                                        urn,
                                        content_type,
                                    )
                                    if result is False:
                                        sys.exit(-1)
                            elif hans_type == "SLIDES_IMAGES_META":
                                print("Slides image files")
                                slides_images_root_path = os.path.join(
                                    subpath, artefact_meta_data["artefact_file"].rsplit("/")[0]
                                )
                                print(f"Slides image files root path: {slides_images_root_path}")
                                for slide_image_file in os.listdir(slides_images_root_path):
                                    print(slide_image_file)
                                    # Default: application/octet-stream
                                    slide_image_file_sub_path = os.path.join(
                                        artefact_meta_data["artefact_file"], slide_image_file
                                    )
                                    print("FileSubPath: %s", slide_image_file_sub_path)
                                    urn = StorageConnector.create_urn(
                                        artefact_meta_data["destination_database"],
                                        artefact_meta_data["destination_bucket"],
                                        slide_image_file_sub_path,
                                    )
                                    if ".json" in slide_image_file_sub_path:
                                        content_type = "application/json"
                                    elif ".png" in slide_image_file_sub_path:
                                        content_type = "image/png"
                                    else:
                                        content_type = artefact_meta_data["mime_type"]
                                    if slide_image_file.endswith("slides.meta.json"):
                                        curr_slides_images_meta_urn = urn

                                    upload_file = os.path.join(subpath, slide_image_file_sub_path)
                                    result = transfer_file_to_remote(
                                        assetdb_connector,
                                        mediadb_connector,
                                        upload_file,
                                        slide_image_file_sub_path,
                                        urn,
                                        content_type,
                                    )
                                    if result is False:
                                        sys.exit(-1)
            # publish
            # Insert hans_type urn tuples from curr_meta_data_urns dict into curr_meta_data_lecture dict
            curr_meta_data_lecture.update(curr_meta_data_urns)
            if "thumbnails" not in curr_meta_data_lecture:
                curr_meta_data_lecture["thumbnails"] = {}
            curr_meta_data_lecture["thumbnails"]["media"] = curr_thumbnails_media_urn
            curr_meta_data_lecture["slides_images_meta"] = curr_slides_images_meta_urn
            if "lecturer" not in curr_meta_data_lecture["thumbnails"]:
                if len(curr_thumbnails_lecturer_urn) > 1:
                    curr_meta_data_lecture["thumbnails"]["lecturer"] = curr_thumbnails_lecturer_urn
                else:
                    print("Using default avatar for thumbnails lecturer")
                    curr_meta_data_lecture["thumbnails"]["lecturer"] = "http://localhost/avatars/avatar-m-01.png"

            # Add additional versioning info and stats
            curr_meta_data_lecture["package_info"] = {}
            now = datetime.now()
            curr_meta_data_lecture["package_info"]["installed"] = now.strftime("%m_%d_%Y_%H_%M_%S")

            # Check if lecture already exists in database and preserve its state
            existing_lecture = mongo_connector.get_metadata(f"metadb:meta:post:id:{curr_meta_data_lecture_uuid}")

            if existing_lecture and "state" in existing_lecture:
                # Preserve existing state from database
                curr_meta_data_lecture["state"] = existing_lecture["state"]
                print(f"Preserved existing state for lecture {curr_meta_data_lecture_uuid}")
            else:
                # Set default state for new lectures
                curr_meta_data_lecture["state"] = {
                    "published": True,
                    "listed": True,
                    "overall_step": "EDITING",
                    "editing_progress": 0
                }
                print(f"Set default state for new lecture {curr_meta_data_lecture_uuid}")

            print("Final meta data:")
            meta_data_str = json.dumps(curr_meta_data_lecture)
            print(meta_data_str)

            urn_meta_data = f"metadb:meta:post:id:{curr_meta_data_lecture_uuid}"
            transfer_meta_data = json.loads(meta_data_str)

            (success, urn_result) = mongo_connector.put_object(
                urn_meta_data, None, "application/json", transfer_meta_data
            )
            if success is False:
                print("Error during meta data publishing!")
                sys.exit(-1)
            else:
                print(f"Published {urn_result}")

    print("Installing channel")
    channel_data_str = json.dumps(channel_package_data)
    print(channel_data_str)

    urn_input = f"metadb:meta:post:id:{channel_uuid}"
    (success, urn_result) = mongo_connector.put_object(urn_input, None, "application/json", channel_package_data)

    if success is False:
        print("Error during channel data publishing!")
        sys.exit(-1)
    else:
        print(f"Published channel succesful: {urn_result}")


parser = argparse.ArgumentParser(
    description="HAnS Channel Package Manager - Manage channel packages on HAnS backend",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  %(prog)s --list-db                           # List all packages in database
  %(prog)s --list-db-with-datetime             # List all packages with creation times
  %(prog)s --list-db-with-datetime-sorted      # List all packages with creation times (sorted newest first)
  %(prog)s --clean-db-with-log                 # List and delete all packages
  %(prog)s --install --file package.tar.gz     # Install a package
  %(prog)s --download --file package.tar.gz    # Download a package
  %(prog)s --help                              # Show this help message
    """
)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--clean-db", action="store_true",
                  help="Remove all channel packages from the database")
group.add_argument("--list-db", action="store_true",
                  help="Display all channel packages currently in the database")
group.add_argument("--list-db-with-datetime", action="store_true",
                  help="Display all channel packages with their creation times")
group.add_argument("--list-db-with-datetime-sorted", action="store_true",
                  help="Display all channel packages with creation times (sorted newest first)")
group.add_argument("--clean-db-with-log", action="store_true",
                  help="List all channel packages and then delete them all (shows what will be deleted)")
group.add_argument("--list-host", action="store_true",
                  help="Show all channel package files in the host packages folder")
group.add_argument("--download", action="store_true",
                  help="Download a specific channel package from database to host (requires --file)")
group.add_argument("--install", action="store_true",
                  help="Install a channel package from host folder to the system (requires --file)")
group.add_argument("--help-features", action="store_true",
                  help="Show comprehensive help with all features and examples")
parser.add_argument("--file", type=str,
                   help="Channel package filename (e.g., 6a31edcc-1b34-4343-bed7-047a1cf36383.tar.gz)")
parser.add_argument("--no-extraction", action="store_true",
                   help="Skip automatic extraction when installing (requires manual extraction)")
args = parser.parse_args()

# Show comprehensive help if no arguments or help requested
if len(sys.argv) == 1 or args.help_features:
    show_comprehensive_help()
    sys.exit(0)

try:
    assetdb_con = connector_provider.get_assetdb_connector()
    assetdb_con.connect()
    if args.clean_db:
        cleanup_channel_packages(assetdb_con)
    if args.list_db:
        list_channel_packages(assetdb_con)
    elif args.list_db_with_datetime:
        list_channel_packages_with_datetime(assetdb_con)
    elif args.list_db_with_datetime_sorted:
        list_channel_packages_with_datetime_sorted(assetdb_con)
    elif args.clean_db_with_log:
        delete_all_list_channel_packages(assetdb_con)
    elif args.list_host:
        os.system("cd /channel-packages && ls -1 *.tar.gz")
    elif args.download:
        download_channel_package(assetdb_con, args.file)
    elif args.install:
        install_channel_package(assetdb_con, args.file, args.no_extraction)
    elif args.help_features:
        show_comprehensive_help()
    else:
        sys.exit(-1)
    sys.exit(0)
except Exception as e:
    print("Unexpected error occured:")
    print(e)
    sys.exit(-1)
