#!/bin/bash
#SBATCH --job-name=tei-mxbai-de-l # Short name for the job
#SBATCH --nodes=1                  # Nodes
#SBATCH --ntasks=1                 # Complete number of tasks over all nodes
#SBATCH --partition=p1             # Used partition (e.g. p1 or p2 or p3)
#SBATCH --time=07:59:00            # Timelimit for the runtime of the job (Format: HH:MM:SS)
#SBATCH --cpus-per-task=32         # CPU cores per task
#SBATCH --mem-per-cpu=1GB
#SBATCH --gres=gpu:0               # Complete number of GPUs per node, max 4
#SBATCH --qos=ultimate             # Quality-of-Service, For more than one gpu you need to request for gpuultimate
#SBATCH --mail-type=ALL            # Type of mail delivery (possible values: e.g. ALL, BEGIN, END, FAIL oder REQUEUE)
#SBATCH --mail-user=<YOUR_USER_EMAIL>@th-nuernberg.de # mail adress for status mail (Replace <USERNAME> with your correct username please!)
#SBATCH --container-image=/nfs/scratch/staff/<YOUR_USER_ID>/tei/text-embeddings-inference-cpu-1.5.sqsh # Loading the previously saved image
#SBATCH --container-mounts=/nfs/scratch/staff/<YOUR_USER_ID>/tei/data:/data

# config threads for ninja and use for other toolchains
# should be the same as for slurm config --cpus-per-task if --ntasks==1
export MAX_JOBS=32

# service port, usually configured e.g. by orchestrator
service_port=8096
if [ $# -eq 0 ]; then
    echo "Warning: No service port provided, using default: $service_port"
else
    service_port=$1
fi

# first startup to download and create /data/models--mixedbread-ai... folders
text-embeddings-router --model-id "mixedbread-ai/deepset-mxbai-embed-de-large-v1" \
--port $service_port --uds-path /tmp/tei \
--tokenization-workers $MAX_JOBS --huggingface-hub-cache /data --revision bf64f853a489a263ca7b064fcc2d0d973c1cef15

# use cached model second startup
#text-embeddings-router --model-id "/data/models--mixedbread-ai--deepset-mxbai-embed-de-large-v1/snapshots/bf64f853a489a263ca7b064fcc2d0d973c1cef15" \
#--port $service_port --uds-path /tmp/tei \
#--tokenization-workers $MAX_JOBS --huggingface-hub-cache /data --revision bf64f853a489a263ca7b064fcc2d0d973c1cef15
