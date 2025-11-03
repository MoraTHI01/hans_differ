: # Stops and removes the built backend for testing
:<<"::CMDLITERAL"
@ECHO OFF
GOTO :CMDSCRIPT
::CMDLITERAL
#!/bin/bash

imagename=hans-ml-backend
flagRemove=0

while getopts r flag
do
    case "${flag}" in
        r) flagRemove=1;;
    esac
done

: # Workaround for Apple Silicon bug in Airflow postgresql connection
: # https://stackoverflow.com/questions/62807717/how-can-i-solve-postgresql-scram-authentifcation-problem
if [[ $(uname -p) = "arm64" ]] || [[ $(uname -p) = "arm" ]];
then
    export POSTGRESQL_VERSION=13
else
    export POSTGRESQL_VERSION=14
fi

: # Stop and remove previous container
if [[ $flagRemove -eq 1 ]];
then
    echo ""
    echo "Docker Compose Down And Remove ml-backend"
    echo ""
    if [[ $(uname -s) = "Darwin" ]] || [[ $(uname -a) == *"WSL"* ]];
    then
        docker compose -f docker-compose.darwin.yaml down --rmi all -v
    fi
    docker compose down --rmi all -v

    : # Remove all docker image files for airflow docker operators
    echo "WARNING! This will remove:"
    echo "  - all Apache Airflow Docker Operator docker images"
    echo ""
    read -r -p "Are you sure you want to continue? [y/N] " response
    response=${response:l}
    if [[ $response =~ ^(yes|y| ) ]] || [[ -z $response ]]; then
        cd dags
        for jobdir in docker_jobs/*/
        do
            jobdir=${jobdir%*/}
            docker rmi -f airflow_docker_${jobdir##*/}
        done
        cd ..
    fi

    : # Remove all ml-backend data
    echo "WARNING! This will remove:"
    echo "  - all stored ml-backend data and logs"
    echo ""
    read -r -p "Are you sure you want to continue? [y/N] " response
    response=${response:l}
    if [[ $response =~ ^(yes|y| ) ]] || [[ -z $response ]]; then
        rm -rf data
        rm -rf logs
    fi
else
    echo ""
    echo "Docker Compose Stop ml-backend"
    echo ""
    docker compose stop
fi
exit $?

:CMDSCRIPT
ECHO Windows is currently not supported, please use WSL2 or Hyper-V and Docker Desktop!
