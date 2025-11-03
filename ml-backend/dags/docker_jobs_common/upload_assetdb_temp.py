#!/usr/bin/env python
"""
Helper to upload multiple files to assetdb-temp
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import argparse
import json
import sys
from io import BytesIO
from modules.connectors.connector_provider import connector_provider

parser = argparse.ArgumentParser(description="Helper to upload multiple files to assetdb-temp")
parser.add_argument("config", type=str, help="Configuration to establish minio connection")
parser.add_argument("urn", type=str, help="URN path on the assetdb-temp minio instance, e.g. ")
parser.add_argument("files", type=str, help="Comma seperated list of files to be uploaded")
args = parser.parse_args()

try:
    config = json.loads(args.config)
    connector_provider.configure({"assetdb_temp": config})
    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    URN = str(args.urn)
    print("- URN: " + URN)

    upload_files = []
    if "," in args.files:
        upload_files = args.files.split(",")
    else:
        upload_files.append(args.files)

    for file in upload_files:
        print("- FILE: " + file)
        fext = file.rsplit(".")
        mime_type = "application/octet-stream"
        if "json" in fext:
            mime_type = "application/json"
        elif "mpd" in fext:
            mime_type = "application/dash+xml"
        elif "m4s" in fext:
            mime_type = "video/mp4"
        elif "mp4" in fext:
            mime_type = "video/mp4"
        elif "pdf" in fext:
            mime_type = "application/pdf"
        elif "wav" in fext:
            mime_type = "audio/wav"
        elif "mp3" in fext:
            mime_type = "audio/mpeg"
        elif "jpg" or "jpeg" in fext:
            mime_type = "image/jpg"
        elif "png" in fext:
            mime_type = "image/png"

        with open(file, "rb") as fh:
            stream_bytes = BytesIO(fh.read())
            final_urn = URN + "/" + file
            print("- UPLOAD_URN: " + final_urn)
            assetdb_temp_connector.put_object(
                final_urn, stream_bytes, mime_type, {"X-Amz-Meta-Filename": file, "Content-Type": mime_type}
            )
    sys.exit(0)
except Exception as e:
    print("Unexpected error occured:")
    print(e)
    sys.exit(-1)
