"""
Create an update HAnS channel package on the HAnS prototype.
"""

import argparse
import os
import shutil
import tarfile
from datetime import datetime
from uuid import uuid4
from utils import read_json_file, write_to_file, dump_json


def update_channel(old_package_path, update_package_path, output_package_path, output_package_created):
    """
    Update channel.json
    """
    channel_old_path = os.path.join(old_package_path, "channel.json")
    channel_update_path = os.path.join(update_package_path, "channel.json")

    old_channel_json = read_json_file(channel_old_path)
    update_channel_json = read_json_file(channel_update_path)

    update_channel_json["uuid"] = old_channel_json["uuid"]
    update_channel_json["update_package_created"] = output_package_created
    channel_output_path = os.path.join(output_package_path, "channel.json")
    write_to_file(channel_output_path, dump_json(update_channel_json))


def analyze_old_package(old_package_path):
    """
    Analyze old package
    """
    # title to uuid mapping for patching metadb entries
    title_to_uuid = {}
    # uuid of media files in mediadb bucket videos
    delete_mediadb_videos_folder_uuids = []
    # filenames of assets to delete in assetdb bucket assets
    delete_assetdb_assets_files = []
    # metadb uuids used in metadb for keys '_id' and 'uuid'
    # Also used as searchengine document id's
    uuids = []

    for path in os.listdir(old_package_path):
        curr_path = os.path.join(old_package_path, path)
        # omit channel.json
        if os.path.isdir(curr_path):
            for filename in os.listdir(curr_path):
                f = os.path.join(curr_path, filename)
                if os.path.isfile(f):
                    if f.endswith("meta.json"):
                        curr_json = read_json_file(f)
                        if curr_json["hans_type"] == "META_DATA":
                            meta_data_filename = curr_json["artefact_file"]
                            meta_data_path = os.path.join(curr_path, meta_data_filename)
                            meta_json = read_json_file(meta_data_path)
                            title_to_uuid[meta_json["title"]] = meta_json["uuid"]
                            uuids.append(meta_json["uuid"])
                        elif not curr_json["hans_type"] in (
                            "SEARCH_DATA",
                            "SEARCH_DATA_VECTORS",
                            "SEARCH_SUMMARY_DATA_VECTORS",
                        ):
                            delete_assetdb_assets_files.append(curr_json["artefact_file"])
                elif os.path.isdir(f):
                    delete_mediadb_videos_folder_uuids.append(filename)
    return {
        "title_to_uuid": title_to_uuid,
        "delete_mediadb_videos_folder_uuids": delete_mediadb_videos_folder_uuids,
        "delete_assetdb_assets_files": delete_assetdb_assets_files,
        "uuids": uuids,
    }


def create_cleanup_json(old_package, output_package_path, output_package_created):
    """
    Create cleanup.json for update package
    """
    cleanup_json = {
        "update_package_created": output_package_created,
        "metadb": {"uuids": old_package["uuids"]},
        "mediadb": {"videos": old_package["delete_mediadb_videos_folder_uuids"]},
        "assetdb": {"assets": old_package["delete_assetdb_assets_files"]},
        "searchengine": {"ids": old_package["uuids"]},
    }
    cleanup_output_path = os.path.join(output_package_path, "cleanup.json")
    write_to_file(cleanup_output_path, dump_json(cleanup_json))


def create_meta_json(title_to_old_uuid, update_package_path, output_package_path, output_package_created):
    """
    Create updated meta.json for metadb
    """
    meta_data_files = []
    for path in os.listdir(update_package_path):
        curr_path = os.path.join(update_package_path, path)
        # omit channel.json
        if os.path.isdir(curr_path):
            output_path = os.path.join(output_package_path, path)
            os.mkdir(output_path)
            for filename in os.listdir(curr_path):
                f = os.path.join(curr_path, filename)
                if os.path.isfile(f):
                    if f.endswith("meta.json"):
                        curr_json = read_json_file(f)
                        if curr_json["hans_type"] == "META_DATA":
                            meta_data_filename = curr_json["artefact_file"]
                            meta_data_path = os.path.join(curr_path, meta_data_filename)
                            meta_json = read_json_file(meta_data_path)
                            if meta_json["title"] in title_to_old_uuid.keys():
                                meta_json["uuid"] = title_to_old_uuid[meta_json["title"]]
                            meta_json["update_package_created"] = output_package_created
                            updated_meta_json_path = os.path.join(output_path, meta_data_filename)
                            write_to_file(updated_meta_json_path, dump_json(meta_json))
                            meta_data_files.append(meta_data_filename)
    return meta_data_files


def create_update_package(title_to_old_uuid, update_package_path, output_package_path, output_package_created):
    """
    Create update package using new package and old package as input
    """
    meta_data_files = create_meta_json(
        title_to_old_uuid, update_package_path, output_package_path, output_package_created
    )
    for path in os.listdir(update_package_path):
        curr_path = os.path.join(update_package_path, path)
        # omit channel.json
        if os.path.isdir(curr_path):
            output_path = os.path.join(output_package_path, path)
            if not os.path.exists(output_path):
                os.mkdir(output_path)
            for filename in os.listdir(curr_path):
                f = os.path.join(curr_path, filename)
                if os.path.isfile(f):
                    if filename not in meta_data_files:
                        output_file = os.path.join(output_path, filename)
                        shutil.copy2(f, output_file)
                elif os.path.isdir(f):
                    output_folder = os.path.join(output_path, filename)
                    print(f"Copy folder {f} to {output_folder}")
                    shutil.copytree(f, output_folder)


def package(output_folder, output_package_id, output_package_path):
    """
    Create output package archive tar.gz
    """
    output_package_archive_path = os.path.join(output_folder, output_package_id + ".tar.gz")
    print("Creating new package archive")
    with tarfile.open(output_package_archive_path, "w:gz") as tar:
        tar.add(output_package_path, arcname=".")
    print(f"Created package archive: {output_package_archive_path}")


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--old-package", type=str, help="Old/previous package folder")
    parser.add_argument("-n", "--new-package", type=str, help="Newly created package folder")
    parser.add_argument("-f", "--output-folder", type=str, help="Output folder for output package")
    return parser.parse_args()


def main():
    """
    Merge old package and update package to new HAnS output package
    """
    args = parse_args()

    old_package = analyze_old_package(args.old_package)

    if not os.path.exists(args.output_folder):
        os.mkdir(args.output_folder)

    output_package_id = str(uuid4())
    output_package_created = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    output_package_path = os.path.join(args.output_folder, output_package_id)
    os.mkdir(output_package_path)

    update_channel(args.old_package, args.new_package, output_package_path, output_package_created)
    create_cleanup_json(old_package, output_package_path, output_package_created)
    create_update_package(old_package["title_to_uuid"], args.new_package, output_package_path, output_package_created)
    package(args.output_folder, output_package_id, output_package_path)


if __name__ == "__main__":
    main()
