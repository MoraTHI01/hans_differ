#!/bin/bash

git clone https://github.com/huggingface/text-embeddings-inference.git text-embeddings-inference

cd text-embeddings-inference
git checkout tags/v1.5.0

# For CPU
docker build . -t text-embeddings-inference:cpu-1.5 --build-arg DOCKER_LABEL=text-embeddings-inference:cpu-1.5

# For A100
runtime_compute_cap=80
# Build docker image on ml0
docker build . -f Dockerfile-cuda --build-arg CUDA_COMPUTE_CAP=$runtime_compute_cap -t text-embeddings-inference:1.5 --build-arg DOCKER_LABEL=text-embeddings-inference:1.5

# For Ada Lovelace (RTX 4000 series, ...)
runtime_compute_cap=89
# Build docker image on ml0
docker build . -f Dockerfile-cuda --build-arg CUDA_COMPUTE_CAP=$runtime_compute_cap -t text-embeddings-inference:89-1.5 --build-arg DOCKER_LABEL=text-embeddings-inference:89-1.5

cd ..

# Convert docker image to squashfs using enroot
enroot import --output text-embeddings-inference-cpu-1.5.sqsh 'dockerd://text-embeddings-inference:cpu-1.5'

# Convert docker image to squashfs using enroot
enroot import --output text-embeddings-inference-1.5.sqsh 'dockerd://text-embeddings-inference:1.5'

# Convert docker image to squashfs using enroot
enroot import --output text-embeddings-inference-89-1.5.sqsh 'dockerd://text-embeddings-inference:89-1.5'
