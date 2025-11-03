#!/usr/bin/env python
"""
Helper to download multiple objects from assetdb-temp
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import argparse
import json
import sys
import os
from modules.connectors.connector_provider import connector_provider

parser = argparse.ArgumentParser(description="Helper to download multiple objects from assetdb-temp")
parser.add_argument("config", type=str, help="Configuration to establish minio connection")
parser.add_argument("folder_path", type=str, help="Path to the folder to store the downloaded objects")
parser.add_argument("bucketid", type=str, help="Id name of the bucket, e.g. archive-bucket, assets-temp")
parser.add_argument("files", type=str, help="Comma seperated list of objects to be downloaded, or * for all objects")
args = parser.parse_args()

try:
    config = json.loads(args.config)
    bucket = config[args.bucketid]
    connector_provider.configure({"assetdb_temp": config})
    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    download_files = []
    download_all_files = False
    if "," in args.files:
        download_files = args.files.split(",")
    elif "*" in args.files:
        download_all_files = True
    else:
        download_files = [args.files]

    if download_all_files:
        print("- Download all files")
        minio_objects = assetdb_temp_connector.list_objects_on_bucket(bucket, "")
        for minio_object in minio_objects:
            FILE_PATH = str(minio_object.object_name)
            print("- FILE: " + FILE_PATH)
            response = assetdb_temp_connector.get_object_on_bucket(bucket, FILE_PATH)
            sub_path = FILE_PATH.rsplit("/", maxsplit=1)[0]
            store_path = args.folder_path + "/" + sub_path
            IS_EXISTING = os.path.exists(store_path)
            if not IS_EXISTING:
                os.makedirs(store_path, exist_ok=True)
            with open(args.folder_path + "/" + FILE_PATH, "wb") as f:
                f.write(response.data)
    else:
        print("- Download specific files")
        for file in download_files:
            print("- FILE: " + file)
            response = assetdb_temp_connector.get_object_on_bucket(bucket, file)
            sub_path = file.rsplit("/", maxsplit=1)[0]
            store_path = args.folder_path + "/" + sub_path
            IS_EXISTING = os.path.exists(store_path)
            if not IS_EXISTING:
                os.makedirs(store_path, exist_ok=True)
            with open(args.folder_path + "/" + file, "wb") as f:
                f.write(response.data)
    sys.exit(0)
except Exception as e:
    print("Unexpected error occured:")
    print(e)
    sys.exit(-1)
