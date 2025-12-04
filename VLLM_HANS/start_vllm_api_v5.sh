conda init
source ~/.bashrc
conda activate vllm_small_mistral_v5
#vllm serve mistralai/Pixtral-12B-2409 --tokenizer_mode mistral --limit_mm_per_prompt 'image=4' --host "0.0.0.0" --port 8092
#CUDA_VISIBLE_DEVICES=3 vllm serve mistralai/Pixtral-12B-2409 --tokenizer_mode mistral --limit_mm_per_prompt 'image=4' --host "0.0.0.0" --port 8192
CUDA_VISIBLE_DEVICES=4 vllm serve mistralai/Mistral-Small-3.1-24B-Instruct-2503 --tokenizer_mode mistral --limit_mm_per_prompt 'image=4' --config_format mistral --load_format mistral --tool-call-parser mistral --host "0.0.0.0" --port 8192

