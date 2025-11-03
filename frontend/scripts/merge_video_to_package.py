"""
Create an update HAnS channel package on the HAnS prototype.
"""

import argparse
import os
import shutil
import tarfile
from datetime import datetime
from uuid import uuid4
from utils import read_json_file


def analyze_old_package(old_package_path):
    """
    Analyze old package
    """
    # title to video folder mapping
    title_to_video_folder = {}
    # title to video meta data file mapping
    title_to_video_meta_file = {}

    for path in os.listdir(old_package_path):
        curr_path = os.path.join(old_package_path, path)
        # omit channel.json
        if os.path.isdir(curr_path):
            curr_video_folder = None
            curr_video_meta_file_path = None
            curr_video_title = None
            for filename in os.listdir(curr_path):
                f = os.path.join(curr_path, filename)
                if os.path.isfile(f):
                    if f.endswith("meta.json"):
                        curr_json = read_json_file(f)
                        if curr_json["hans_type"] == "MEDIA":
                            curr_video_meta_file_path = f
                            media_folder = curr_json["artefact_file"]
                            media_folder_path = os.path.join(curr_path, media_folder)
                            if os.path.isdir(media_folder_path) and curr_json["is_folder"] is True:
                                curr_video_folder = media_folder_path
                                if curr_video_title is not None:
                                    if not curr_video_title in title_to_video_folder:
                                        title_to_video_folder[curr_video_title] = curr_video_folder
                                    if not curr_video_title in title_to_video_meta_file:
                                        title_to_video_meta_file[curr_video_title] = curr_video_meta_file_path
                        elif curr_json["hans_type"] == "META_DATA":
                            meta_data_filename = curr_json["artefact_file"]
                            meta_data_path = os.path.join(curr_path, meta_data_filename)
                            meta_json = read_json_file(meta_data_path)
                            curr_video_title = meta_json["title"]
                            if curr_video_folder is not None:
                                if not curr_video_title in title_to_video_folder:
                                    title_to_video_folder[curr_video_title] = curr_video_folder
                                if not curr_video_title in title_to_video_meta_file:
                                    title_to_video_meta_file[curr_video_title] = curr_video_meta_file_path

    return {"title_to_video_folder": title_to_video_folder, "title_to_video_meta_file": title_to_video_meta_file}


def create_merge_package(old_package, update_package_path, output_package_path, output_package_created):
    """
    Create update package using new package and old package as input
    """
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
                    output_file = os.path.join(output_path, filename)
                    shutil.copy2(f, output_file)
                    if f.endswith("meta.json"):
                        curr_json = read_json_file(f)
                        if curr_json["hans_type"] == "META_DATA":
                            meta_data_filename = curr_json["artefact_file"]
                            meta_data_path = os.path.join(curr_path, meta_data_filename)
                            meta_json = read_json_file(meta_data_path)
                            curr_title = meta_json["title"]
                            print(f"Title: {curr_title}")
                            old_video_folder = old_package["title_to_video_folder"][curr_title]
                            print(f"Old video folder: {old_video_folder}")
                            old_video_meta_file = old_package["title_to_video_meta_file"][curr_title]
                            print(f"Old video meta data file: {old_video_meta_file}")
                            output_video_folder = os.path.join(output_path, old_video_folder.rsplit("/", 1)[-1])
                            shutil.copytree(old_video_folder, output_video_folder)
                            output_video_meta_file = os.path.join(output_path, old_video_meta_file.rsplit("/", 1)[-1])
                            shutil.copy2(old_video_meta_file, output_video_meta_file)
                elif os.path.isdir(f):
                    output_folder = os.path.join(output_path, filename)
                    print(f"Copy folder {f} to {output_folder}")
                    shutil.copytree(f, output_folder)
        elif os.path.isfile(curr_path) and not curr_path.endswith(".DS_Store"):
            output_file = os.path.join(output_package_path, curr_path.rsplit("/", 1)[-1])
            shutil.copy2(curr_path, output_file)


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
    Merge old package video into new package
    """
    args = parse_args()

    old_package = analyze_old_package(args.old_package)

    if not os.path.exists(args.output_folder):
        os.mkdir(args.output_folder)

    output_package_id = str(uuid4())
    output_package_created = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    output_package_path = os.path.join(args.output_folder, output_package_id)
    os.mkdir(output_package_path)

    create_merge_package(old_package, args.new_package, output_package_path, output_package_created)
    package(args.output_folder, output_package_id, output_package_path)


if __name__ == "__main__":
    main()
