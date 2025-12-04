conda init
source ~/.bashrc
conda activate vllm2
#vllm serve mistralai/Pixtral-12B-2409 --tokenizer_mode mistral --limit_mm_per_prompt 'image=4' --host "0.0.0.0" --port 8092
#CUDA_VISIBLE_DEVICES=3 vllm serve mistralai/Pixtral-12B-2409 --tokenizer_mode mistral --limit_mm_per_prompt 'image=4' --host "0.0.0.0" --port 8192
CUDA_VISIBLE_DEVICES=5 vllm serve NousResearch/DeepHermes-3-Mistral-24B-Preview --host "0.0.0.0" --port 8090


