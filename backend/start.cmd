: # Builds and runs the data-backend
:<<"::CMDLITERAL"
@ECHO OFF
GOTO :CMDSCRIPT
::CMDLITERAL
#!/bin/bash

flagBuild=0
flagTest=0
flagReBuild=0
flagDebug=0

while getopts btrd flag
do
    case "${flag}" in
        b) flagBuild=1;;
        r) flagReBuild=1;;
        t) flagTest=1;;
        d) flagDebug=1;;
    esac
done

echo "COMPOSE_PROJECT_NAME=hans-backend" > ./.env
: # Copy config values from .env.config file on project root (if not available, copy defaults from .env.template)
if [ -f ./../.env.config ];
then
    echo "CONFIG: values from top-level .env.config file will be used"
    cat ./../.env.config >> ./.env
else
    echo "CONFIG: .env.config file was not found on top level - default values from .env.template will be used"
    cat ./../.env.template >> ./.env
fi

: # Activate env config to create e.g. hans-fb-network
export $(grep -v '^#' .env | xargs)

: # Stop and remove previous containers
./stop.cmd

if [[ ! -d data ]];
then
    mkdir data
    mkdir data/data-assetdb
    mkdir data/data-mediadb
    mkdir data/data-metadb
    mkdir data/data-searchengine-node1
    mkdir data/data-searchengine-node1/nodes
    mkdir data/data-searchengine-node2
    mkdir data/data-searchengine-node2/nodes
    mkdir data/matomo
    mkdir data/matomo_mysql
    mkdir data/matomo_export
    if [[ ! $DOCKER_USER == "" ]]
    then
        chown -R $DOCKER_USER data/data-searchengine-node1
        chown -R $DOCKER_USER data/data-searchengine-node2
        chown -R $DOCKER_USER data/matomo
        chown -R $DOCKER_USER data/matomo_mysql
        chown -R $DOCKER_USER data/matomo_export
    fi
fi

: # Create nginx default config file
python3 nginx/create_default_config.py $flagDebug

: # Create hans-fb-network for connection between frontend and backend
docker network create ${HANS_FB_NETWORK_NAME}

: # Configure docker compose command
docker_cmd="docker compose -f docker-compose.yaml"
if [[ $flagTest -eq 1 ]];
then
  echo "Building backend: Also start containers for testing"
  docker_cmd="$docker_cmd -f docker-compose.test.yaml"
fi
if [[ $flagDebug -eq 1 ]];
then
  echo "Building backend: Also start containers for debugging"
  docker_cmd="$docker_cmd -f docker-compose.debug.yaml"
fi

: # Build and run data-backend
if [[ $flagBuild -eq 1 ]];
then
    echo "Docker Compose Build and Up backend"
    $docker_cmd up --force-recreate --build --always-recreate-deps -d
else
    echo "Docker Compose Up backend"
    $docker_cmd up -d
fi
exit $?

:CMDSCRIPT
ECHO Windows is currently not supported, please use WSL2 or Hyper-V and Docker Desktop!
