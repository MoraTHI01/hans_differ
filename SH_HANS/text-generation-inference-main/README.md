# text-generation-inference

Scripts to run [huggingface/text-generation-inference](https://github.com/huggingface/text-generation-inference) (tgi) on ml-cluster.

- tgi supports loading of LoRA adapters for each request on the fly, see [https://huggingface.co/docs/text-generation-inference/conceptual/lora](https://huggingface.co/docs/text-generation-inference/conceptual/lora).

- tgi supports structured generation (also called constrained decoding), see [guidance](https://huggingface.co/docs/text-generation-inference/basic_tutorials/using_guidance).

## Setup

### Build

- Use `rsync` to upload the complete files to your network storage on the ml-cluster, replace `<USERNAME>` with your user id:

```bash
cd ..
rsync -v -a -h text-generation-inference <USERNAME>@ml1.in.ohmhs.de:///nfs/scratch/staff/<USERNAME>
```

- Execute docker image build and image conversion on ```ml0``` node:

```bash
./build.sh
```

This builds the squash FS images for text-generation-inference.

### Run

Run the squash FS images by modifying ["run.sh"](./run.sh) Slurm script depending on resources and your purpose:

**⚠️ IMPORTANT:**
**Use ```qos interactive``` on ```ml0```, ```ml1``` or ```ml2``` for testing!**

**⚠️ IMPORTANT:**
**Run on ```ml3``` with Nvidia L40S GPU for ```inference in production```!**

```bash
sbatch run.sh
```

#### OPTIONAL download your model

- Configure slurm parameters, your model and email in [`download.sh`](./run.sh), see [Slurm User Guide](https://github.com/th-nuernberg/mladm/blob/main/doc/slurm_user_guide.md)

- Download your model with [`download.sh`](./download.sh):

```bash
sbatch download.sh
```

## Test on your local machine

- Test inference by starting a seperate terminal with a ssh tunnel to your used ml-server:

```bash
ssh -N -L localhost:8092:localhost:8092 <YOUR_USER_ID>@<USED_ML_SERVER>.in.ohmhs.de
```

- Call [`test.sh`](./test.sh) to test inference:

```bash
./test.sh
```

- Call [`test_context_length.sh`](./test_context_length.sh) to test large input token length on inference:

```bash
./test_context_length.sh
```

## Load Test

### Load Test on your local machine

- Test inference instance using [`loadtest.py`](./loadtest/loadtest.py) in folder [`loadtest`](./loadtest)

- Install dataset and requirements

```bash
cd loadtest
./install.sh
pip3 install -r requirements.txt
```

- Execute single loadtest with 32 random questions

```bash
cd loadtest
python3 loadtest.py -s 127.0.0.1 -p 8092 -i train-v2.0.json -n 32
```

- Execute multiple loadtests with [`loadtest.sh`](./loadtest/loadtest.sh)

```bash
cd loadtest
./loadtest.sh
```

### Load Test using cluster

- Configure slurm parameters and email in [`loadtest/run.sh`](./loadtest/run.sh), see [Slurm User Guide](https://github.com/th-nuernberg/mladm/blob/main/doc/slurm_user_guide.md)

- Start building and running loadtest using [`loadtest/run.sh`](./loadtest/run.sh):

```bash
cd loadtest
sbatch run.sh
```
