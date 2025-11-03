: # Stops and removes the built webfrontend for testing
:<<"::CMDLITERAL"
@ECHO OFF
GOTO :CMDSCRIPT
::CMDLITERAL
#!/bin/bash

imagename=hans-backend
flagRemove=0

while getopts r flag
do
    case "${flag}" in
        r) flagRemove=1;;
    esac
done

: # Stop and remove previous container
if [[ $flagRemove -eq 1 ]];
then
    echo "Docker Compose Down And Remove backend"
    docker compose down --rmi all -v

    : # Remove all backend data
    echo "WARNING! This will remove:"
    echo "  - all stored backend data"
    echo ""
    read -r -p "Are you sure you want to continue? [y/N] " response
    response=${response:l}
    if [[ $response =~ ^(yes|y| ) ]] || [[ -z $response ]]; then
        rm -rf data
    fi

    : # Remove all backend channel packages
    echo "WARNING! This will remove:"
    echo "  - all stored channel packages"
    echo ""
    read -r -p "Are you sure you want to continue? [y/N] " response
    response=${response:l}
    if [[ $response =~ ^(yes|y| ) ]] || [[ -z $response ]]; then
        rm -rf channel-packages
    fi
else
    echo "Docker Compose Stop backend"
    docker compose stop
fi
exit $?

:CMDSCRIPT
ECHO Windows is currently not supported, please use WSL2 or Hyper-V and Docker Desktop!
