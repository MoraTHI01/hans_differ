#!/bin/bash
#SBATCH --job-name=tgi-dl-wg       # Short name for the job
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
#SBATCH --container-image=/nfs/scratch/staff/<YOUR_USER_ID>/tgi/text-generation-inference-v2.2.0.sqsh # Loading the previously saved image
#SBATCH --container-mounts=/nfs/scratch/staff/<YOUR_USER_ID>/tgi/data:/data

text-generation-server download-weights "meta-llama/Llama-2-13b-chat-hf"
