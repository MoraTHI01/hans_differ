: # Stops and removes HAnS docker container
:<<"::CMDLITERAL"
@ECHO OFF
GOTO :CMDSCRIPT
::CMDLITERAL
#!/bin/bash

flagRemove=0

while getopts r flag
do
    case "${flag}" in
        r) flagRemove=1;;
    esac
done

: # Helper function to call stop.cmd in subfolder
local_stop () {
    cd "$1"
    if [[ $flagRemove -eq 1 ]]
    then
        ./stop.cmd -r
    else
        ./stop.cmd
    fi
    cd ..
}

: # Stop and remove all HAnS docker container
if [[ $flagRemove -eq 1 ]];
then
    echo "Docker Compose Down And Remove HAnS"
else
    echo "Docker Compose Down HAnS"
fi

local_stop "frontend" && local_stop "ml-backend" && local_stop "backend"

if [[ $flagRemove -eq 1 ]];
then
    docker system prune -a
    docker volume prune
    docker network prune
fi
exit $?

:CMDSCRIPT
ECHO Windows is currently not supported
