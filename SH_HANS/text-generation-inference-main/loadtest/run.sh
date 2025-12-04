#!/bin/bash
#SBATCH --job-name=tgi-llama2     # Short name for the job
#SBATCH --nodes=1                 # Nodes
#SBATCH --ntasks=32                # Complete number of tasks over all nodes
#SBATCH --partition=p1            # Used partition (e.g. p1 or p2), currently only p1 (ml1) is possible, p2 has virtualized GPUs which is not supported
#SBATCH --time=23:59:00           # Timelimit for the runtime of the job (Format: HH:MM:SS)
#SBATCH --cpus-per-task=1        # CPU cores per task
#SBATCH --qos=ultimate            # Quality-of-Service
#SBATCH --mail-type=ALL           # Type of mail delivery (possible values: e.g. ALL, BEGIN, END, FAIL oder REQUEUE)
#SBATCH --mail-user=<USERNAME>@th-nuernberg.de # mail adress for status mail (Replace <USERNAME> with your correct username please!) 

echo "=================================================================="
echo "Starting Batch Job at $(date)"
echo "Job submitted to partition ${SLURM_JOB_PARTITION} on ${SLURM_CLUSTER_NAME}"
echo "Job name: ${SLURM_JOB_NAME}, Job ID: ${SLURM_JOB_ID}"
echo "Requested ${SLURM_CPUS_ON_NODE} CPUs on compute node $(hostname)"
echo "Working directory: $(pwd)"
echo "=================================================================="

###################### Setup #######################
# ML_CLUSTER_ROLE could be 'students' or 'staff'
export ML_CLUSTER_ROLE=staff
if [ -f setup.sh ]; then
      . setup.sh; else
         echo "missing setup.sh"; exit 1;
fi
####################################################


srun python3 loadtest.py -s 127.0.0.1 -p 8080 -i train-v2.0.json -n 1
