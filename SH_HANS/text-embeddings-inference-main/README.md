# text-embeddings-inference

Scripts to run [huggingface/text-embeddings-inference](https://github.com/huggingface/text-embeddings-inference) on ml-cluster.

## Setup

### Build

- Execute docker image build and image conversion on ```ml0``` node:

```bash
./build.sh
```

This builds the squash FS images for CPU, A100, and L40S.

### Run

Run the squash FS images by modifying one of the following Slurm scripts depending on resources and your purpose:

- ["run-A100.sh"](run-A100.sh) for running on ```ml1``` or ```ml2``` with Nvidia A100 GPU for **testing purposes** in ```qos interactive``` only
- ["run-CPU.sh"](./run-CPU.sh) for running on ```ml0```, ```ml1```, ```ml2```, or ```ml3``` on CPU only, **recommended default, should be used with small and medium models**
- ["run-L40S.sh"](./run-L40S.sh) for running on ```ml3``` with Nvidia L40S GPU for ```inference in production``` with large model

## Local Testing

- Forward the remote port to your local machine for testing:

```bash
ssh -N -L localhost:8096:localhost:8096 <YOUR_USER_ID>@<USED_ML_SERVER>.in.ohmhs.de
```

- Run the test script in test folder:

```bash
cd test
./test.sh
```
