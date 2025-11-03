: # Builds and runs the webfrontend for testing
:<<"::CMDLITERAL"
@ECHO OFF
GOTO :CMDSCRIPT
::CMDLITERAL
#!/bin/bash

flagBuild=0
flagTest=0
flagReBuild=0

while getopts brt flag
do
    case "${flag}" in
        b) flagBuild=1;;
        r) flagReBuild=1;;
        t) flagTest=1;;
    esac
done

echo "COMPOSE_PROJECT_NAME=hans-frontend" > ./.env
: # Copy config values from .env.config file on project root (if not available, copy defaults from .env.template)
if [ -f ./../.env.config ];
then
    echo "CONFIG: values from top-level .env.config file will be used"
    cat ./../.env.config >> ./.env
else
    echo "CONFIG: .env.config file was not found on top level - default values from .env.template will be used"
    cat ./../.env.template >> ./.env
fi
: # https://jasonwatmore.com/post/2022/05/28/vue-3-vite-access-environment-variables-from-dotenv-env
cat ./.env > ./vue/.env
: # Remove blank lines
sed -i -e '/^$/d' ./vue/.env
: # Add VITE_ prefix to access env variables in vue
sed -i -e 's/^/VITE_/' ./vue/.env
: # Add .env.config to flask api auth config
cat ./.env > ./flask/api/auth/.env
: # Remove blank lines
sed -i -e '/^$/d' ./flask/api/auth/.env

: # Activate env config to create e.g. hans-fb-network
export $(grep -v '^#' ./flask/api/auth/.env | xargs)

: # Stop and remove previous containers
./stop.cmd

: # Configure Authorization
python3 flask/api/auth/gen_auth_config.py

: # Create hans-fb-network for connection between frontend and backend
docker network create ${HANS_FB_NETWORK_NAME}

: # Build and run backend
if [[ $flagBuild -eq 1 ]];
then
    if [[ $flagTest -eq 1 ]];
    then
        echo "Docker Compose Up And Build frontend for Testing"
        docker compose -f docker-compose.yaml -f docker-compose.test.yaml up --force-recreate --build --always-recreate-deps -d
    else
        echo "Docker Compose Up And Build frontend"
        docker compose up --force-recreate --build --always-recreate-deps -d
    fi
else
    echo "Docker Compose Up frontend"
    if [[ $flagTest -eq 1 ]];
    then
        echo "Docker Compose Up frontend for Testing"
        docker compose -f docker-compose.yaml -f docker-compose.test.yaml up -d
    else
        echo "Docker Compose Up frontend"
        docker compose up -d
    fi
fi
exit $?

:CMDSCRIPT
ECHO Windows is currently not supported, please use WSL2 or Hyper-V and Docker Desktop!
