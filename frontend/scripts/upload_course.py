"""
Upload and process a complete course on the HAnS prototype.
"""

import os
from datetime import datetime
import sys
from pathlib import Path
import subprocess
import requests
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from utils import read_json_file


def check_video_file(filename):
    """
    Run ffprobe command to get information about the video file
    """
    cmd = ["ffprobe", "-v", "error", "-show_format", "-show_streams", filename]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check for errors in the output
    if result.returncode != 0:
        print("Error: ffprobe command failed.")
        print("Error output:", result.stderr)
        return False
    elif "Invalid data found when processing input" in result.stderr:
        print("Error: Invalid data found in the video file.")
        return False
    else:
        print("Video file is valid.")
        return True


def upload_course_item(session, upload_url, auth, fields, videofile, slidesfile):
    """
    Upload a file
    From https://stackoverflow.com/questions/13909900/progress-of-python-requests-post
    """
    videopath = Path(videofile)
    total_size = videopath.stat().st_size
    videofilename = videopath.name

    slidespath = Path(slidesfile)
    total_size += slidespath.stat().st_size
    slidesfilename = slidespath.name

    with tqdm(
        desc=f"Upload course item with video {videofilename} and slides {slidesfilename}",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        with open(videofile, "rb") as tempvideof:
            with open(slidesfile, "rb") as tempslidesf:
                fields["media"] = (videofilename, tempvideof)
                fields["slides"] = (slidesfilename, tempslidesf)
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
UPLOAD_URL = f"http://{HOSTNAME}/api/upload"

options = sys.argv
x = len(options)

if x < 3:
    print("Error: Not enough parameters!")
    print("Usage:")
    print("  python3 upload_course.py <credentilas-json-file> <course-folder> [<hostname>]")
    print("Example:")
    print("  python3 upload_course.py ./credentials.json ./FODESOA/ localhost")
else:
    credentials_file = options[1]
    course_folder = options[2]
    if x > 3:
        HOSTNAME = options[3]
        LOGIN_URL = f"http://{HOSTNAME}/api/login"
        UPLOAD_URL = f"http://{HOSTNAME}/api/upload"

    meta_data_file = None
    slides_folder = None
    slides_folder_filecount = 0
    first_slide_file = None
    videos_folder = None
    upload_count = 0

    for filename in os.listdir(course_folder):
        f = os.path.join(course_folder, filename)
        if os.path.isfile(f):
            print(f"File: {f}")
            if os.path.basename(f) == "meta.json":
                meta_data_file = f
        else:
            print(f"Folder: {f}")
            if os.path.basename(f) == "slides":
                slides_folder = f
                slide_folder_content = [name for name in os.listdir(f)]
                slides_folder_filecount = len(slide_folder_content)
                first_slide_file = slide_folder_content[0]
            elif os.path.basename(f) == "videos":
                videos_folder = f

    credentials = read_json_file(credentials_file)
    meta_data = read_json_file(meta_data_file)

    session = requests.Session()

    auth = login(session)

    print("Start upload of complete course!")
    for filename in os.listdir(videos_folder):
        videofile = os.path.join(videos_folder, filename)
        if os.path.isfile(videofile):
            videofilename = os.path.basename(videofile)
            if videofilename.endswith(".mp4"):
                title = videofilename.replace(".mp4", "")
                if slides_folder_filecount > 1:
                    slidefile = os.path.join(slides_folder, f"{title}.pdf")
                else:
                    slidefile = os.path.join(slides_folder, first_slide_file)
                if os.path.isfile(slidefile):
                    print(f"Title: {title}")
                    meta_data["title"] = title
                    UPLOAD_LOCK_FILE = os.path.join(videos_folder, f"{title}.done")
                    if not os.path.exists(UPLOAD_LOCK_FILE):
                        if not check_video_file(videofile):
                            print(f"Error during upload on {videofilename}!")
                            exit(-2)
                        dtStart = datetime.utcnow().isoformat()
                        UPLOAD_OK = upload_course_item(session, UPLOAD_URL, auth, meta_data, videofile, slidefile)
                        dtFinished = datetime.utcnow().isoformat()
                        if UPLOAD_OK:
                            UPLOAD_LOCK_FILE = os.path.join(videos_folder, f"{title}.done")
                            with open(UPLOAD_LOCK_FILE, "w", encoding="UTF-8") as f:
                                f.writelines("UploadStart: " + dtStart + "\n")
                                f.writelines("UploadEnded: " + dtFinished + "\n")
                            print(f"Title: {title} uploaded!")
                            upload_count += 1
                        else:
                            print(f"Error during upload on {videofilename}!")
                            exit(-1)
                    else:
                        print(f"Title: {title} already uploaded!")
    if upload_count > 1:
        print(f"Finished! Uploaded {upload_count} files.")
    else:
        print(f"Finished! Uploaded {upload_count} file.")
