#!/bin/bash

###################### Optional for Python Users #######################
# The following environment variables omit the storage of
# Huggingface model weights, models and PIP packages below user folder
# /home/$USER/.cache
# and use the network drive user space instead
CACHE_DIR=$PWD/.cache
export PIP_CACHE_DIR=$CACHE_DIR
export TRANSFORMERS_CACHE=$CACHE_DIR
export HF_HOME=$CACHE_DIR
mkdir -p .cache
########################################################

########## Setup Virtual Environment ###############################################
module purge
module load python/anaconda3 cuda/11
eval "$(conda shell.bash hook)"
export TGI_VENV="venv-tgi-loadtest"
if [[ ! -d $PWD/$TGI_VENV ]]
then
    conda create -y --prefix $PWD/$TGI_VENV python=3.9
fi
conda activate $PWD/$TGI_VENV
export PATH=$PWD/$TGI_VENV/bin:$PATH
pip3 install -r requirements.txt
####################################################################################
