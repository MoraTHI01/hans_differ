: # Builds and runs the backend for testing
:<<"::CMDLITERAL"
@ECHO OFF
GOTO :CMDSCRIPT
::CMDLITERAL
#!/bin/bash

flagBuild=0
flagTest=0
flagVerbose=0
flagReBuild=0
flagDebug=0

while getopts brtdv flag
do
    case "${flag}" in
        b) flagBuild=1;;
        t) flagTest=1;;
        r) flagReBuild=1;;
        d) flagDebug=1;;
        v) flagVerbose=1;;
    esac
done

echo "COMPOSE_PROJECT_NAME=hans-ml-backend" > ./.env
: # Copy config values from .env.config file on project root (if not available, copy defaults from .env.template)
if [ -f ./../.env.config ];
then
    echo "CONFIG: values from top-level .env.config file will be used"
    cat ./../.env.config >> ./.env
else
    echo "CONFIG: .env.config file was not found on top level - default values from .env.template will be used"
    cat ./../.env.template >> ./.env
fi
if [[ $(uname -a) == *"WSL"* ]];
then
    echo "HANS_HOST_PLATFORM=wsl" >> .env
else
    echo "HANS_HOST_PLATFORM=$(uname -s)" >> .env
fi

: # Stop and remove previous containers
./stop.cmd

docker_cmd="docker compose -f docker-compose.yaml"
export POSTGRESQL_VERSION=14

: # Workaround for Apple Silicon bug in Airflow postgresql connection
: # https://stackoverflow.com/questions/62807717/how-can-i-solve-postgresql-scram-authentifcation-problem
if [[ $(uname -s) = "Darwin" ]] || [[ $(uname -a) == *"WSL"* ]];
then
    if [[ $(uname -p) = "arm64" ]] || [[ $(uname -p) = "arm" ]]
    then
        export POSTGRESQL_VERSION=13
    else
        export POSTGRESQL_VERSION=14
    fi
    docker_cmd="$docker_cmd -f docker-compose.darwin.yaml"
fi

: # Create required airflow directories
mkdir -p ./logs ./plugins ./data
mkdir -p ./data/airflow-temp
chmod 777 ./data/airflow-temp

: # Sparse checkout airflow and set to release https://github.com/apache/airflow/releases/tag/2.5.3
if [[ ! -d airflow ]];
then
    git clone --filter=blob:none --branch 2.5.3 https://github.com/apache/airflow.git airflow
    cd airflow
    git sparse-checkout set /Dockerfile* /scripts/ /docker-context-files/ /empty/
    cd ..
fi

echo ""

if [[ $flagReBuild -eq 1 ]];
then
    flagBuild=1
    echo ""
    echo "Rebuilding images where git diff shows modifications"
    echo ""
fi

: # Helper to build docker image files for airflow docker operators
jobdir=""
build_flags=""

function create_docker_job_image {
    build_file="$jobdir/Dockerfile"
    if [[ $(uname -s) = "Darwin" ]];
    then
        if [[ $(uname -p) = "arm64" ]] || [[ $(uname -p) = "arm" ]];
        then
            if [[ -f "$jobdir/Dockerfile.darwin" ]];
            then
                build_file="$jobdir/Dockerfile.darwin"
            fi
        fi
    fi
    echo ""
    echo "Building docker image $build_file"
    echo ""
    echo "docker build $build_flags -f $build_file -t airflow_docker_${jobdir##*/} $jobdir/"
    echo ""
    docker build $build_flags -f $build_file -t airflow_docker_${jobdir##*/} $jobdir/
}

: # Build all docker image files for airflow docker operators
echo ""
echo "Docker build dags/docker_jobs images"
echo ""
for jobdir in dags/docker_jobs/*/
do
    jobdir=${jobdir%*/}
    : # provide connectors for assetdb-temp
    if [[ ! -d $jobdir/modules ]];
    then
        mkdir $jobdir/modules/
    fi
    touch $jobdir/modules/__init__.py
    if [[ ! -d $jobdir/modules/connectors ]];
    then
        mkdir $jobdir/modules/connectors/
    fi
    cp -r dags/modules/connectors/* $jobdir/modules/connectors/
    : # Clean pycache folder before building
    rm -Rf $jobdir/modules/__pycache__
    rm -Rf $jobdir/modules/connectors/__pycache__
    : # Provide common job files into each jobdir
    cp -r dags/docker_jobs_common/* $jobdir/
    build_flags="--force-rm"
    if [[ $flagBuild -eq 1 ]];
    then
        build_flags="$build_flags --no-cache"
    fi
    if [[ $flagVerbose -eq 1 ]];
    then
        build_flags="$build_flags --progress plain"
    fi
    buildImage=1
    if [[ $flagReBuild -eq 1 ]];
    then
        : # Rebuilding images where git diff shows modifications
        buildImage=0
        git diff --quiet $jobdir
        retVal=$?
        if [ $retVal -ne 0 ]; then
            buildImage=1
        fi
    fi
    : # Skip building if file "skip" exists, indicates that this image is
    : # currently not needed
    if [ -f "$jobdir/skip" ]; then
        buildImage=0
    fi
    if [[ $buildImage -eq 1 ]];
    then
        create_docker_job_image
        retVal=$?
        if [ $retVal -ne 0 ]; then
            : # Second try, e.g. large image files have sporadic connection issue during building
            create_docker_job_image
            retVal=$?
            if [ $retVal -ne 0 ]; then
                echo "Error building docker image: $jobdir/Dockerfile!"
                exit $retVal
            fi
        fi
    else
        echo ""
        echo "Building docker image $jobdir/Dockerfile skipped!"
        echo ""
    fi
done

: # Build and run backend
if [[ $flagReBuild -eq 1 ]];
then
    : # Rebuilding airflow if docker compose changed:
    : # Python DAG's or modules changes are propagated
    : # and don't need rebuild of the image.
    : # Disabling force build flag if no changes in docker-compose.yaml
    git diff --quiet docker-compose.yaml
    retVal=$?
    if [ $retVal -eq 0 ]; then
        flagBuild=0
    fi
fi

build_flags_compose=""
verbose_flag_compose=""
build_message_compose="Docker Compose Up"
if [[ $flagBuild -eq 1 ]];
then
    build_message_compose="$build_message_compose And Build"
    build_flags_compose="$build_flags_compose --force-recreate --build --always-recreate-deps "
fi
if [[ $flagVerbose -eq 1 ]];
then
    verbose_flag_compose="--verbose "
fi
build_message_compose="$build_message_compose ml-backend"

if [[ $flagTest -eq 1 ]];
then
  build_message_compose="$build_message_compose, including Testing containers"
  docker_cmd="$docker_cmd -f docker-compose.test.yaml"
fi
if [[ $flagDebug -eq 1 ]];
then
  build_message_compose="$build_message_compose, including Debugging containers"
  docker_cmd="$docker_cmd -f docker-compose.debug.yaml"
fi

echo ""
echo "$build_message_compose"
echo ""
echo "command: $docker_cmd ${verbose_flag_compose}up ${build_flags_compose}-d"
$docker_cmd ${verbose_flag_compose}up ${build_flags_compose}-d

exit $?

:CMDSCRIPT
ECHO Windows is currently not supported, please use WSL2 or Hyper-V and Docker Desktop!
