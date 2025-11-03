"""
Create a HAnS channel package on the HAnS prototype.
"""

import os
import json
import sys
import requests
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from utils import read_json_file


def create_channel_package(session, upload_url, auth, fields):
    """
    Create channel package
    """
    total_size = len(json.dumps(fields))
    course = fields["course"]

    with tqdm(
        desc=f"Create channel package for course {course}",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        e = MultipartEncoder(fields=fields)
        m = MultipartEncoderMonitor(e, lambda monitor: bar.update(monitor.bytes_read - bar.n))
        access_token = auth["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": m.content_type,
            "Access-Control-Allow-Origin": "*",
        }
        response = session.post(upload_url, data=m, headers=headers)
        print("HTTP request response code: " + f"{response.status_code:d}")
        if response.status_code == 200:
            return True
        else:
            return False


def login(session):
    """
    Login to HAnS
    return: json dictionary with "access_token" and "refresh_token"
    """
    print(f"Login on {LOGIN_URL}")
    response = session.get(LOGIN_URL, auth=HTTPBasicAuth(credentials["username"], credentials["password"]))
    print("Login HTTP request response code: " + f"{response.status_code:d}")
    if response.status_code != 200:
        print(f"Error during login on {LOGIN_URL}")
        exit(-1)
    return response.json()


HOSTNAME = "localhost"
LOGIN_URL = f"http://{HOSTNAME}/api/login"
CREATE_CHANNEL_URL = f"http://{HOSTNAME}/api/createChannel"

options = sys.argv
x = len(options)

if x < 3:
    print("Error: Not enough parameters!")
    print("Usage:")
    print("  python3 create_channel_package.py <credentilas-json-file> <course-folder> [<hostname>]")
    print("Example:")
    print("  python3 create_channel_package.py ./credentials.json ./FODESOA/ localhost")
else:
    credentials_file = options[1]
    course_folder = options[2]
    if x > 3:
        HOSTNAME = options[3]
        LOGIN_URL = f"http://{HOSTNAME}/api/login"
        CREATE_CHANNEL_URL = f"http://{HOSTNAME}/api/createChannel"

    meta_data_file = None

    for filename in os.listdir(course_folder):
        f = os.path.join(course_folder, filename)
        if os.path.isfile(f):
            print(f"File: {f}")
            if os.path.basename(f) == "meta.json":
                meta_data_file = f

    credentials = read_json_file(credentials_file)
    meta_data = read_json_file(meta_data_file)

    session = requests.Session()

    auth = login(session)

    final_meta_data = {}

    final_meta_data["language"] = meta_data["language"]
    final_meta_data["course"] = meta_data["course"]
    final_meta_data["course_acronym"] = meta_data["course_acronym"]
    final_meta_data["semester"] = meta_data["semester"]
    final_meta_data["lecturer"] = meta_data["lecturer"]
    final_meta_data["faculty"] = meta_data["faculty"]
    final_meta_data["faculty_acronym"] = meta_data["faculty_acronym"]
    final_meta_data["faculty_color"] = meta_data["faculty_color"]
    final_meta_data["university"] = meta_data["university"]
    final_meta_data["university_acronym"] = meta_data["university_acronym"]
    final_meta_data["license"] = "OER"
    final_meta_data["license_url"] = "https://open-educational-resources.de"
    final_meta_data["tags"] = meta_data["tags"]
    final_meta_data["thumbnails_lecturer"] = meta_data["thumbnails_lecturer"]
    final_meta_data["archive_channel_content"] = "True"

    if create_channel_package(session, CREATE_CHANNEL_URL, auth, final_meta_data):
        print("Finished!")
    else:
        print("Error creating channel package!")
