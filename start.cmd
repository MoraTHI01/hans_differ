: # Builds and runs all HAnS docker container
:<<"::CMDLITERAL"
@ECHO OFF
GOTO :CMDSCRIPT
::CMDLITERAL
#!/bin/bash

flagBuild=0
flagTest=0
flagNoCache=0
flagReBuild=0
flagDebug=0

while getopts bnrtd flag
do
    case "${flag}" in
        b) flagBuild=1;;
        n) flagNoCache=1;;
        r) flagReBuild=1;;
        t) flagTest=1;;
        d) flagDebug=1;;
    esac
done

: # Force complete re-build if -n specified, by disabling docker cache
if [[ $flagNoCache -eq 1 ]];
then
    export DOCKER_CACHE="disabled"
else
    export DOCKER_CACHE="local"
fi

: # Stop and remove all HAnS docker container
./stop.cmd

: # Setup environment
if [[ -f ./.env.config ]]; then
  export $(grep -v '^#' ./.env.config | xargs)
fi

: # Create hans-test-network for testing
if [[ $flagTest -eq 1 ]];
then
    docker network create ${HANS_TEST_NETWORK_NAME}
fi

: # Create hans-fb-network for connection between frontend and backend
docker network create ${HANS_FB_NETWORK_NAME}

: # Helper function to call start.cmd in subfolder
local_start () {
    cd "$1"
    flags=""
    if [[ $flagBuild -eq 1 ]]
    then
        flags="$flags -b"
    elif [[ $flagReBuild -eq 1 ]]
    then
        flags="$flags -b -r"
    fi
    if [[ $flagTest -eq 1 ]]
    then
        flags="$flags -t"
    fi
    if [[ $flagDebug -eq 1 ]]
    then
        flags="$flags -d"
    fi

    ./start.cmd "$flags"
    retVal=$?
    if [ $retVal -ne 0 ]; then
        echo "Error starting $1!"
        exit 1
    fi
    cd ..
}

: # Build and run all HAnS docker container
if [[ $flagBuild -eq 1 ]];
then
    echo "Docker Compose Up And Build HAnS"
else
    echo "Docker Compose Up HAnS"
fi

local_start "backend" && local_start "ml-backend" && local_start "frontend" && exit $?

:CMDSCRIPT
ECHO Windows is currently not supported
