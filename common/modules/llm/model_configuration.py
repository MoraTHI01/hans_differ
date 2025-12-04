#!/usr/bin/env python
"""
Models configuration
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"

MODEL_TASKS = ["generate", "embed", "transcribe", "translate"]

MODEL_CONFIGRUATION = {
    "generate": [
        {
            "model_id": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "temperature": 0.7,
            "max_new_tokens": 8192,
            "engine": "tgi",  # Valid: tgi, vllm, openai
            "timeout": 360.0,
            "frequency_penalty": 0.3,  # Used for json schema only
            "is_mm": False,  # Multimodal
            "is_reasoning": False,  # Reasoning
        },
        {
            "model_id": "mistralai/Mistral-Small-24B-Instruct-2501",
            "temperature": 0.15,
            "max_new_tokens": 16384,
            "engine": "tgi",  # Valid: tgi, vllm, openai
            "timeout": 360.0,
            "frequency_penalty": 0.3,  # Used for json schema only
            "is_mm": False,  # Multimodal
            "is_reasoning": False,  # Reasoning
        },
        {
            "model_id": "mistralai/Pixtral-12B-2409",
            "temperature": 0.7,
            "max_new_tokens": 16384,
            "engine": "vllm",  # Valid: tgi, vllm, openai
            "timeout": 360.0,
            "frequency_penalty": 0.3,  # Used for json schema only
            "is_mm": True,  # Multimodal
            "is_reasoning": False,  # Reasoning
        },
        {
            "model_id": "mistralai/Mistral-Small-3.1-24B-Instruct-2503",
            "temperature": 0.15,
            "max_new_tokens": 20480,
            "engine": "vllm",  # Valid: tgi, vllm, openai
            "timeout": 360.0,
            "frequency_penalty": 0.3,  # Used for json schema only
            "is_mm": True,  # Multimodal
            "is_reasoning": False,  # Reasoning
        },
        {
            "model_id": "NousResearch/DeepHermes-3-Mistral-24B-Preview",
            "temperature": 0.15,
            "max_new_tokens": 16384,
            "engine": "vllm",  # Valid: tgi, vllm, openai
            "timeout": 600.0,
            "frequency_penalty": 0.3,  # Used for json schema only
            "is_mm": False,  # Multimodal
            "is_reasoning": True,  # Reasoning
        },
        {
            "model_id": "Qwen/Qwen3-30B-A3B-FP8",
            "temperature": 0.6,
            "max_new_tokens": 16384,
            "engine": "vllm",  # Valid: tgi, vllm, openai
            "timeout": 600.0,
            "frequency_penalty": 0.3,  # Used for json schema only
            "is_mm": False,  # Multimodal
            "is_reasoning": True,  # Reasoning
        },
    ],
    "translate": [
        {
            "model_id": "google/madlad400-7b-mt",
            "temperature": None,
            "max_new_tokens": 4096,
            "engine": "tgi",  # Valid: tgi, vllm, openai
            "timeout": 360.0,
            "frequency_penalty": None,
            "is_mm": False,  # Multimodal
            "is_reasoning": False,  # Reasoning
        }
    ],
    "transcribe": [
        {
            "model_id": "medium-low-vram-local",
            "engine": "OPENAI",  # Valid: OPENAI
            "batch_size": 8,
            "asr_model": "medium",
            "num_cpus": 4.0,
            "ram_limit_docker": "10g",
            "use_gpu": False,
            "is_remote": False,
        },
        {
            "model_id": "large-v3-low-vram-remote",
            "engine": "WHISPER_S2T",  # Valid: WHISPER_S2T, mod9
            "timeout": 360.0,
            "batch_size": 8,  # 8 for smaller GPU's e.g. RTX 2080 Ti 11GB VRAM
            "asr_model": "large-v3",
            "is_remote": True,
        },
        {
            "model_id": "large-v3-high-vram-remote",
            "engine": "WHISPER_S2T",  # Valid: WHISPER_S2T, mod9
            "timeout": 360.0,
            "batch_size": 48,  # for data center gpus e.g. A100 40GB VRAM
            "asr_model": "large-v3",
            "is_remote": True,
        },
    ],
    "embed": [
        {
            "model_id": "mixedbread-ai/deepset-mxbai-embed-de-large-v1",
            "temperature": None,
            "max_new_tokens": 16384,
            "engine": "tei",  # Valid: tei, vllm, openai
            "timeout": 360.0,
            "frequency_penalty": None,
            "is_mm": False,  # Multimodal embedding support
            "is_reasoning": False,  # Reasoning
        },
        {
            "model_id": "llamaindex/vdr-2b-multi-v1",
            "temperature": None,
            "max_new_tokens": 16384,
            "engine": "vllm",  # Valid: tei, vllm, openai
            "timeout": 360.0,
            "frequency_penalty": None,
            "is_mm": True,  # Multimodal embedding support
            "is_reasoning": False,  # Reasoning
        },
    ],
}


def get_model_config(model_task="generate", model_id="mistralai/Mistral-Small-3.1-24B-Instruct-2503") -> dict:
    """Get model configuration by model type and model id"""
    if model_task not in MODEL_TASKS:
        raise TypeError("Model task not supported!")

    curr_type_config = MODEL_CONFIGRUATION[model_task]
    matches = list(filter(lambda x: x["model_id"] == model_id, curr_type_config))
    result = matches[0] if matches else None
    return result
