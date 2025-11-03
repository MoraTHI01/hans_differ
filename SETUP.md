# Configuration and Environment Setup

## Global Configuration

- Per default, the configuration from repository root file [`.env.template`](./.env.template) will be used.
- If you want to change values, copy the [`.env.template`](./.env.template) to a global configuration file `.env.config`
  in the repository root folder
- Set the correct environment variables, e.g. database credentials, service ports and protocols.
- In case HAnS is already running when you change variable values, remember to restart all containers using
  [`start.cmd`](./start.cmd)

### Docker Rootless Setup

- HAnS can be setup with [Docker rootless mode](https://docs.docker.com/engine/security/rootless/),
  which allows running the Docker daemon and containers as a non-root user
- This involves the following steps:
  - Install and start docker rootless as described
    [in the official manual](https://docs.docker.com/engine/security/rootless/)
  - Make sure to adapt the DOCKER_SOCKET_PATH in `.env.config` to your docker host, e.g. `/run/user/1005/docker.sock`
  - Docker rootless does not have access to privileged ports (below 1024) by default. Adapt `.env.config` accordingly
    or follow [Exposing privileged ports](https://docs.docker.com/engine/security/rootless/#exposing-privileged-ports)
  - In case the searchengine services are not starting properly, try removing the `USER` field
    in the searchengine services in [`backend/docker-compose.yaml`](./backend/docker-compose.yaml)

### HAnS Frontend Analytics Configuration

To enable web analytics for HAnS frontend [setup Matomo](./backend/matomo/SETUP_MATOMO.md).

### Linux Server Configuration for ml-backend

ml-backend Airflow spawns docker containers on demand.
It needs appropriate permissions on the docker socket.

- Ensure the docker socket is readable (use the socket path specified as DOCKER_SOCKET_PATH):

```bash
sudo chmod 666 /var/run/docker.sock
```

#### GPU Acceleration

The HAnS direct acyclic graph (DAG) spawns docker containers which could use gpu's to speed up processing.

In order to be able to use GPU acceleration you need to change the docker files in the corresponding below the
[docker jobs folder](./ml-backend/dags/docker_jobs/).

- Set the correct Nvidia CUDA version according of your servers nvidia driver in the following docker files:

  - [asr-engine-local-openai](./ml-backend/dags/docker_jobs/asr-engine-local-openai/Dockerfile)

  - [media-converter-video-gpu](./ml-backend/dags/docker_jobs/media-converter-video-gpu/Dockerfile)

- Modify the [`hans_v1.py`](./ml-backend/dags/hans_v1.py) DAG by setting the corresponding `use_gpu` options to true.

#### CPU Threads Configuration

- Modify the [`hans_v1.py`](./ml-backend/dags/hans_v1.py) DAG by setting the corresponding `num_cpus` options.

#### Concurrency and Maximum Active Runs

Maximum active runs configures how many DAG runs should run in parallel.
Concurrency defines the maximum of parallel tasks within DAG runs.

- Modify the [`hans_v1.py`](./ml-backend/dags/hans_v1.py)
DAG by setting the corresponding `concurrency` and `max_active_runs` options, e.g. `concurrency=8, max_active_runs=4`

#### Setup and Configure Remote Services

[`hans_v1.py`](./ml-backend/dags/hans_v1.py) depends on inference services which usually run on a GPU cluster.
Depending on the used cluster there might be a workload manager involved, e.g. [slurm](https://slurm.schedmd.com/overview.html).

All service connections are configured in [`ml-backend/docker-compose.yaml`](./ml-backend/docker-compose.yaml) in
command section of `airflow-cli`. They could be changed during runtime of airflow via browser in menu `Admin`/`Connections`.

You need to setup the following services in order to run the processing DAG [`hans_v1.py`](./ml-backend/dags/hans_v1.py)
and the DAGs used for frontend editing [`chapter_sum_v1.py`](./ml-backend/dags/chapter_sum_v1.py) and
[`translate_topics_quests_v1.py`](./ml-backend/dags/translate_topics_quests_v1.py):

- Transcription Service from [hans-ml-services](https://github.com/th-nuernberg/hans-ml-services) on GPU
  - [`run_transcription_service.sh`](https://github.com/th-nuernberg/hans-ml-services/blob/main/run_transcription_service.sh)
  - The connection is configured by entry `asr_engine_remote_whisper_s2t`

- Large Language Model (LLM) Service from [text-generation-inference](https://github.com/th-nuernberg/text-generation-inference)
on GPU
  - [`run_lorax.sh`](https://github.com/th-nuernberg/text-generation-inference/blob/main/run_lorax.sh)
  - The connection is configured by entry `llm_remote`

- Vision Large Language Model (VLLM) Service from [vllm](https://github.com/th-nuernberg/vllm) on GPU
  - [`run.sh`](https://github.com/th-nuernberg/vllm/blob/main/run.sh)
  - The connection is configured by entry `vllm_remote`

- Translation Service from [text-generation-inference](https://github.com/th-nuernberg/text-generation-inference) on GPU
  - [`run_translation.sh`](https://github.com/th-nuernberg/text-generation-inference/blob/main/run_translation.sh)
  - The connection is configured by entry `nlp_translate_remote`

- Text Embeddings Service from [text-embeddings-inference](https://github.com/th-nuernberg/text-embeddings-inference)
on CPU
  - [`run-CPU.sh`](https://github.com/th-nuernberg/text-embeddings-inference/blob/main/run-CPU.sh)
  - The connection is configured by entry `text_embedding_remote`

- Topic Segmentation Service from [hans-ml-services](https://github.com/th-nuernberg/hans-ml-services) on CPU
  - [`run_topic_segmentation_service.sh`](https://github.com/th-nuernberg/hans-ml-services/blob/main/run_topic_segmentation_service.sh)
  - The connection is configured by entry `topic_segmentation_remote`

#### Final

- Follow the [server configuration for backend](#linux-server-configuration-for-backend) instructions.

### Linux Server Configuration for backend

The following section describes the search engine and storage databases environment setup.

#### Number of Open Files Limit

- Check number of open files limit:

```bash
cat /proc/sys/fs/file-max
65536
```

- Open `sysctl.conf` and increase number of open files limit:

```bash
sudo vi /etc/sysctl.conf
```

- Add the following line, save and quit:

```bash
fs.file-max=9223372036854775807
```

- Apply the limit immediately:

```bash
sudo sysctl -p
```

#### Max Map Count

In order to run the search engine you may need to increase the max map count:

- [OpenSearch documentation](https://opensearch.org/docs/latest/opensearch/install/important-settings/)
- [ElasticSearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html)

- Check current max map count value:

```bash
cat /proc/sys/vm/max_map_count
```

- The following bash command sets the max_map_count once (not persistent after restart):

```bash
sudo sysctl -w vm.max_map_count=262144
```

### Windows Subsystem for Linux Configuration

- You may use Windows Subsystem for Linux Version 2 (WSL2) and Docker Desktop for Windows for development.

- If you use WSL2 and Docker Desktop for Windows you need to change [`vm.max_map_count` setting](#max-map-count).

#### WSL2 Configuration

Configure appropriate resources for the virtual machine, by creating a `.wslconfig` in your users home folder, see
[WSL config documentation of Microsoft](https://learn.microsoft.com/en-us/windows/wsl/wsl-config#wslconfig).

Example `.wslconfig` file:

```bash
# Settings apply across all Linux distros running on WSL 2
[wsl2]

# Limits VM memory to use no more than 4 GB, this can be set as whole numbers using GB or MB
memory=8GB

# Sets the VM to use two virtual processors
processors=8

# Specify a custom Linux kernel to use with your installed distros. The default kernel used can be found at
# https://github.com/microsoft/WSL2-Linux-Kernel
#kernel=C:\\temp\\myCustomKernel

# Sets additional kernel parameters, in this case enabling older Linux base images such as Centos 6
#kernelCommandLine = vsyscall=emulate

# Sets amount of swap storage space to 8GB, default is 25% of available RAM
swap=8GB

# Sets swapfile path location, default is %USERPROFILE%\AppData\Local\Temp\swap.vhdx
swapfile=C:\\wsl\\wsl-swap.vhdx

# Disable page reporting so WSL retains all allocated memory claimed from Windows and releases none back when free
pageReporting=false

# Turn off default connection to bind WSL 2 localhost to Windows localhost
localhostforwarding=true

# Disables nested virtualization, on Windows 11 enable this option by setting it to true!
nestedVirtualization=false

# Turns on output console showing contents of dmesg when opening a WSL 2 distro for debugging
debugConsole=true
```

- On Windows 11 enable nested virtualization:

```bash
nestedVirtualization=true
```

## Managing Channel Packages

### Create Channel Package

It is possible to create channel packages which could be installed on HAnS `backend` docker instances.

A channel package consists of one or multiple media items which correspond usually to a full lecture course.

Follow the steps to create and install a new channel package.

#### Cleanup ml-backend Archive

Open airflow in your webbrowser, e.g. on [http://localhost:8080/home](http://localhost:8080/home).

Trigger the airflow DAG to cleanup the archive, e.g. `cleanup_archive_v1.0.0` and click on play button and select
`Trigger DAG`, as shown in the next picture.

Wait until the DAG execution is finished!

![CleanupArchive](./docs/images/cleanup-ml-backend-archive.png "Cleanup ml-backend Archive")

#### Upload Media Items

Upload all media items which should be part of the channel by using the HAnS frontend upload form, e.g. on
[http://localhost/upload](http://localhost/upload):

![UploadMediaItem](./docs/images/upload-media-item.png "Upload media item")

Check in airflow if all `hans_v1.0.1` DAG runs are finished:

In the following picture there is one run still active:

![AirflowDAGOverview](./docs/images/airflow-dag-overview.png "Airflow DAG overview")

##### Upload Complete Course from Command Line

If you want to automatically upload a complete course consisting of multiple media items follow the instructions on
[Upload Course](./frontend/scripts/README.md#upload-course).

#### Trigger Channel Package Creation

If all airflow DAG's are executed and no DAG is active anymore trigger the channel package creation using
the webfrontend create channel form, e.g. on [http://localhost/create](http://localhost/create).

Select the optional `Create Channel Package` option as shown in the following picture:

![CreateChannelPackage](./docs/images/create-channel-package.png "Create Channel Package")

Check if the `create_hans_channel_package_v1.0.0` DAG is finished in the airflow overview:

![AirflowDAGOverview](./docs/images/airflow-dag-overview.png "Airflow DAG overview")

You could now download the channel package on the HAnS backend host machine.

##### Trigger Channel Package Creation from Command Line

If you want to create a course channel package consisting of multiple media items on command line follow
the instructions on [Create Course Channel Package](./frontend/scripts/README.md#create-course-channel-package).

### Download Channel Package

A channel package file could be downloaded to install it on a different HAnS `backend` host machine.

#### Open Docker Container Shell for Download

In order to download a channel package you need to connect to the HAnS backend host machine and
open a bash on the `manage-channel-packages` docker container:

- Check for the container id of `manage-channel-packages` docker container:

```bash
docker ps -a
```

- Open bash by using the container id of `manage-channel-packages` docker container:

```bash
docker exec -it <container-id> /bin/bash
```

#### Check List of Channel Packages

- List the channel packages available on the packages database:

```bash
python3 manage_channel_packages.py --list-db
```

- Output:

```bash
total 2
52da2021-1359-40e0-a4b6-d904e5bc67bb.tar.gz
6a31edcc-1b34-4343-bed7-047a1cf36383.tar.gz
```

#### Download Channel Package to Host

- Download the desired channel packge to the HAnS backend host machine:

```bash
python3 manage_channel_packages.py --download --file 52da2021-1359-40e0-a4b6-d904e5bc67bb.tar.gz
```

The channel package file should now exist on the host machine in folder `backend/channel-packages`.

### Install Channel Package

You could use a downloaded channel package file and install it on a different HAnS `backend` instance.

#### Transfer Channel Package File

Copy the channel package file in the folder `backend/channel-packages` on the `backend` host machine.

#### Open Docker Container Shell for Installation

In order to download a channel package you need to connect to the HAnS backend host machine and
open a bash on the `manage-channel-packages` docker container:

- Check for the container id of `manage-channel-packages` docker container:

```bash
docker ps -a
```

- Open bash by using the container id of `manage-channel-packages` docker container:

```bash
docker exec -it <container-id> /bin/bash
```

#### Check List of Channel Packages on Host Machine

- List the channel packages available on the HAnS `backend` host machine:

```bash
python3 manage_channel_packages.py --list-host
```

- Output:

```bash
52da2021-1359-40e0-a4b6-d904e5bc67bb.tar.gz
6a31edcc-1b34-4343-bed7-047a1cf36383.tar.gz
8073825c-6428-4cf2-9805-f63391499e06.tar.gz
```

#### Install Channel Package on Backend

- Install the desired channel packge on the HAnS backend:

```bash
python3 manage_channel_packages.py --install --file 52da2021-1359-40e0-a4b6-d904e5bc67bb.tar.gz
```

- Output (last lines) if successful:

```bash
Published channel succesful: metadb:meta:post:id:...
```

The channel package was installed and the HAnS `webfrontend` should show the new channel,
e.g. on [http://localhost/channels](http://localhost/channels).

The channel should show the corresponding media items.
