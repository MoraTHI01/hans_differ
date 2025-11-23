#!/bin/bash
#SBATCH --job-name=tgilx-m8x7b-I01 # Short name for the job
#SBATCH --nodes=1                  # Nodes
#SBATCH --ntasks=1                 # Complete number of tasks over all nodes
#SBATCH --partition=p1             # Used partition (p1 or p2 for A100)
#SBATCH --time=07:59:00            # Timelimit for the runtime of the job (Format: HH:MM:SS)
#SBATCH --cpus-per-task=16         # CPU cores per task
#SBATCH --mem-per-cpu=1GB
#SBATCH --gres=gpu:1               # Complete number of GPUs per node, max 4
#SBATCH --qos=interactive          # Quality-of-Service, For more than one gpu you need to request for gpuultimate
#SBATCH --mail-type=ALL            # Type of mail delivery (possible values: e.g. ALL, BEGIN, END, FAIL oder REQUEUE)
#SBATCH --mail-user=<YOUR_USER_EMAIL>@th-nuernberg.de # mail adress for status mail (Replace <USERNAME> with your correct username please!)
#SBATCH --container-image=/nfs/scratch/staff/<YOUR_USER_ID>/tgi/lorax-v0.10.0.sqsh # Loading the previously saved image
#SBATCH --container-mounts=/nfs/scratch/staff/<YOUR_USER_ID>/tgi/data:/data

# config threads for ninja and use for other toolchains
# should be the same as for slurm config --cpus-per-task if --ntasks==1
export MAX_JOBS=16

# service port, usually configured e.g. by orchestrator
service_port=8092
if [ $# -eq 0 ]; then
    echo "Warning: No service port provided, using default: $service_port"
else
    service_port=$1
fi

# first startup to download and create /data/models--mistralai--Mixtral-8x7B-Instruct-v0.1... folders
lorax-launcher \
--model-id "mistralai/Mixtral-8x7B-Instruct-v0.1" \
--revision 1e637f2d7cb0a9d6fb1922f305cb784995190a83 \
--port $service_port --huggingface-hub-cache /data \
--num-shard 1 --shard-uds-path /tmp/tgi \
--quantize bitsandbytes-nf4  --max-input-length 8192 --max-total-tokens 16384 --max-batch-prefill-tokens 8192

# use cached model second startup:
#lorax-launcher \
#--model-id "/data/models--mistralai--Mixtral-8x7B-Instruct-v0.1/snapshots/1e637f2d7cb0a9d6fb1922f305cb784995190a83" \
#--revision 1e637f2d7cb0a9d6fb1922f305cb784995190a83 \
#--port $service_port --huggingface-hub-cache /data \
#--num-shard 1 --shard-uds-path /tmp/tgi \
#--quantize bitsandbytes-nf4  --max-input-length 8192 --max-total-tokens 16384 --max-batch-prefill-tokens 8192
