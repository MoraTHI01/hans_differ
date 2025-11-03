# Scripts

Overview of available scripts.

## Scripts for Courses

Scripts related to courses, also known as `upload-bundles`.

## Course Folder

In order to upload a complete course aka `upload-bundle`
for processing on ml-backend of a HAnS Prototype
you need the following input folder structure:

```bash
- coursefolder
  |
  - label.meta.json
  - meta.json
  - slides/
  - podcasts/
  - videos/
```

It contains a `meta.json` file which contains the needed meta data for the course,
a folder `slides` containing one or more PDF files,
a folder `videos` containing all video (mp4) files of the course and
optional a folder `podcasts` containing the audio podcasts which
were used to create the video files.
The `label.meta.json` is only used in hans-annotation and contains
a subset of the meta data of `meta.json`.

The slides and video file names should be synchronized if a slide file exists
for every video file, e.g. "lecture_01.mp4" corresponds to "lecture_01.pdf".

The video files should be encoded as mp4 (x264) for 720p resolution
with an aspect ratio of 16:9 and 48khz mono audio using the following command:

```bash
ffmpeg -y -i "$videoFile" -map_metadata -1 \
-c:v libx264 -profile:v high -level:v 3.1 \
-c:a aac -b:a 256k -ac 1 -ar 48000 \
-vf "scale=1280x720:force_original_aspect_ratio=decrease,pad=1280:720:-1:-1:color=black" -aspect "16:9" \
-movflags faststart -tune zerolatency -max_muxing_queue_size 9999 "$outputFile"
```

If a single slide file is available the slide file will be used for all videos.

The `meta.json` file needs to contain the correct meta data for the upload:

```json
{
 "language": "de",
 "course": "Example Course Name",
 "course_acronym": "ECN",
 "semester": "Winter 2022/2023",
 "lecturer": "Prof. Dr. Max Musterman",
 "faculty": "Example Faculty",
 "faculty_acronym": "EXFA",
 "faculty_color": "#FC9136",
 "university": "Example University",
 "university_acronym": "EXUN",
 "permission_public": "True",
 "permission_university_only": "False",
 "permission_faculty_only": "False",
 "permission_study_topic_only": "False",
 "permission_students_only": "False",
 "license_cc_0": "True",
 "license_cc_by_4": "False",
 "license_cc_by_sa_4": "False",
 "tags": "ECN",
 "thumbnails_lecturer": "http://localhost/avatars/avatar-m-00001.png"
}
```

Instructions for creating the `meta.json` file:

- You should only change the image name `avatar-m-00001.png`
when modifying the `thumbnails_lecturer` value!
  - Take care if you have already courses of the lecturer to use the same avatar picture
    for all lectures of the lecturer!
    - Check the existing live system

- Choose the `faculty_color` according to the faculty web design of your institute

- The `course_acronym` should be approx. 3 to 8 letters long and be a unique identifier which
is created from the course name
  - Check that the course acronym is defined in [authorization configuration](./../flask/api/auth/gen_auth_config.py)

- The `tags` should currently only contain the `course_acronym`
  - Check that the course acronym is defined in [authorization configuration](./../flask/api/auth/gen_auth_config.py)

- The `semester` value should follow one of the following templates:
  - German courses:
    - "Winter 2022/2023"
    - "Sommer 2023"
  - English courses:
    - "Winter 2022/2023"
    - "Summer 2023"

  - Important: Only modify the year of the `semester` value and use the correct
    current/upcoming summer/winter semester period!

- Be careful by setting the values for `course_acronym`, `faculty`, `faculty_acronym`, `university`
  and `university_acronym`:
  - Check [authorization configuration](./../flask/api/auth/gen_auth_config.py) for the correct values!
    - method `add_default_static_thn`:
      - `org = "Technische Hochschule Nürnberg"`
      - Would result in the following json values:

        ```json
            "university": "Technische Hochschule Nürnberg",
            "universityAcronym": "THN"
        ```

    - method `add_default_static_thn`:
      - `org = "Technische Hochschule Ingolstadt"`
      - Would result in the following json values:

        ```json
            "university": "Technische Hochschule Ingolstadt",
            "universityAcronym": "THI"
        ```

The `label.meta.json` file contains only a subset of the meta data of the `meta.json` file
and is used in hans-annotation repo for labelstud.io:

```json
{
    "language": "de",
    "course": "Example Course Name",
    "courseAcronym": "ECN",
    "semester": "Sommer 2023",
    "lecturer": "Prof. Dr. Max Musterman",
    "faculty": "Example Faculty",
    "facultyAcronym": "EXFA",
    "university": "Example University",
    "universityAcronym": "EXUN",
}
```

### Credentials

- Create a `credentials.json` by copying the template `credentials.json.template`
and modifying the `credentials.json` with the correct login credentials
from `frontend/flask/api/auth/static_auth.json` (usually an admin account).

### Requirements

- [Python 3](https://www.python.org/)
  - Python is required for configuration, please ensure python3 (>=3.5)
  is installed on your system
  - See the [official python download page](https://www.python.org/downloads/)

- [pip](https://pip.pypa.io/en/stable/installation/)

  ```bash
  python3 -m ensurepip --upgrade
  ```

### Upload Course

To upload a course we use the `upload_course.py` script.

- Install the requirements of the script using `pip`:

```bash
pip3 install -r requirements.txt
```

- Check your current Airflow instance on ml-backend for running DAG jobs
and clear the archive using the clear archive DAG job if necessary.
  - Mainly required if creating a clean new HAnS channel package

- Start uploading with the `upload_course.py` script.

The script requires the `credentials.json`, the path to the course folder as parameters.
The hostname parameter is optional, default hostname is `localhost`.

```bash
python3 upload_course.py ./credentials.json ./ECN/ localhost
```

### Create Course Channel Package

A channel package consists of a complete course which was
previously uploaded in the previous section.

- Check if the processing of the uploaded course in the previous section
was finished on the Airflow instance!

- Install the requirements of the script using `pip`:

```bash
pip3 install -r requirements.txt
```

- Start creation of the channel package with the `create_channel_package.py` script.

The script requires the `credentials.json`, the path to the course folder as parameters.
The hostname parameter is optional, default hostname is `localhost`.

```bash
python3 create_channel_package.py ./credentials.json ./ECN/ localhost
```

### Create Update Course Channel Package

If you have created a new version of a channel package you might want to create
an update package for the old channel package.

- Use the newly created channel package and the old channel package to create
  an update package for a running HAnS instance.

- The update package will have a new archive uuid but internaly an update could be performed by installing
  this package with the [manage-channel-packages](./../../backend/manage-channel-packages/) container,
  for instructions see [SETUP](./../../SETUP.md#install-channel-package)

- Install the requirements of the script using `pip`:

```bash
pip3 install -r requirements.txt
```

- Start creation of the update channel package with the `create_update_package.py` script.

  - All channel packages should be extracted on your system, in `channel-packages` folder e.g.:

  ```bash
  ls -l backend/channel-packages
  ```

  ```bash
  059f1c07-95d6-49f7-bbbd-2c82ed10b694
  059f1c07-95d6-49f7-bbbd-2c82ed10b694.tar.gz
  e296db7b-1a3e-42c0-ac4b-da3e41a5da47
  e296db7b-1a3e-42c0-ac4b-da3e41a5da47.tar.gz
  ```

  - The `create_update_package.py` script requires the following parameters:
    - `--old-package`: path to old channel package folder (extracted from broken package tar.gz)
    - `--new-package`: path to new channel package folder (extracted from recreated / new channel package tar.gz)
    - `--output-folder`: path to output folder, creates update package tar.gz and update package folder

  ```bash
  python3 create_update_package.py \
    --old-package ./../../backend/channel-packages/059f1c07-95d6-49f7-bbbd-2c82ed10b694 \
    --new-package ./../../backend/channel-packages/e296db7b-1a3e-42c0-ac4b-da3e41a5da47 \
    --output-folder ./../../backend/channel-packages
  ```

  - After a successful update package creation you should see a package folder with a new uuid,
    e.g. `e0adbc1f-30d0-4893-abf2-77f04c0b4e19`:

  ```bash
  059f1c07-95d6-49f7-bbbd-2c82ed10b694
  059f1c07-95d6-49f7-bbbd-2c82ed10b694.tar.gz
  e0adbc1f-30d0-4893-abf2-77f04c0b4e19
  e0adbc1f-30d0-4893-abf2-77f04c0b4e19.tar.gz
  e296db7b-1a3e-42c0-ac4b-da3e41a5da47
  e296db7b-1a3e-42c0-ac4b-da3e41a5da47.tar.gz
  ```
