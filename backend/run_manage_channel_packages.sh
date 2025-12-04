#!/bin/bash
# Usage: ./run_manage_channel_packages.sh <filename>
# The script will use the file located at /data/data-assetdb/packages/<filename>

# Unset DOCKER_HOST environment variable
unset DOCKER_HOST

# Check if a filename is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

# Define the base path and construct the full file path
base_path=""
file_arg="${1}"

# Get the container ID for hans-backend-manage-channel-packages
container_id=$(docker ps -qf "name=hans-backend-manage-channel-packages")

if [ -z "$container_id" ]; then
    echo "Error: Container 'hans-backend-manage-channel-packages' not found."
    exit 1
fi

echo "Container ID: $container_id"
echo "Using file: $file_arg"

# Execute commands inside the container:
# Run the download command
docker exec -it "$container_id" python3 manage_channel_packages.py --download --file "$file_arg"

# Run the install command using the same file argument
docker exec -it "$container_id" python3 manage_channel_packages.py --install --file "$file_arg"

