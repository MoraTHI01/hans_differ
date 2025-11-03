#!/bin/bash

user="<user>"
tra_port="8099"

# Define the commands you want to run in each terminal
commands=(
    "ssh -N -L 8067:localhost:8067 $user@141.75.89.10"
    "ssh -N -L 8092:localhost:8092 $user@141.75.89.10"
    "ssh -N -L 8093:localhost:8093 $user@141.75.89.10"
    "ssh -N -L 8094:localhost:8094 $user@141.75.89.14"
    "ssh -N -L 8095:localhost:8095 $user@141.75.89.14"
    "ssh -N -L $tra_port:localhost:$tra_port $user@141.75.89.4"
)

# Loop through the commands array and open a new terminal for each
for cmd in "${commands[@]}"; do
    osascript -e "tell application \"Terminal\" to do script \"$cmd\""
done
