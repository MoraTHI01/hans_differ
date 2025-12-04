#!/bin/bash

# --- Configuration ---
PYTHON_SCRIPT_NAME="embedding_api_server.py"
VENV_DIR=".venv_embeddings"
DEFAULT_APP_PORT="8094" # Your desired default port
DEFAULT_HF_HOME="./data_cache"

export HUGGING_FACE_HUB_TOKEN="..."
APP_PORT="${APP_PORT:-$DEFAULT_APP_PORT}"
export HF_HOME="${HF_HOME:-$DEFAULT_HF_HOME}"

# --- Helper Functions ---
print_info() {
    echo "INFO: $1"
}
print_error() {
    echo "ERROR: $1" >&2
}
print_warning() {
    echo "WARNING: $1" >&2
}
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 could not be found. Please install it."
        exit 1
    fi
}

# --- Main Script ---
print_info "Starting Embedding API Server setup..."
check_command python3
check_command pip3

if [ ! -d "$VENV_DIR" ]; then
    print_info "Creating Python virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR" || { print_error "Failed to create venv."; exit 1; }
else
    print_info "Virtual environment $VENV_DIR already exists."
fi

print_info "Activating virtual environment..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate" || { print_error "Failed to activate venv."; exit 1; }

print_info "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install "uvicorn[standard]" fastapi "pydantic>=1.8,<3.0" "llama-index-embeddings-huggingface" torch sentence-transformers Pillow
if [ $? -ne 0 ]; then
    print_error "Failed to install Python dependencies."
    deactivate &> /dev/null || true
    exit 1
fi

print_info "Creating Python script: $PYTHON_SCRIPT_NAME..."
cat <<EOF > "$PYTHON_SCRIPT_NAME"
import os
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, root_validator, Field, __version__ as pydantic_version
from typing import List, Union, Optional, Any, Dict
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import logging # Moved import higher
from contextlib import asynccontextmanager
import base64
import io
from PIL import Image, UnidentifiedImageError

# --- Logging Configuration --- Moved UP
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] {%(levelname)s} %(message)s')
logger = logging.getLogger(__name__) # Define logger early

# --- Pydantic Version Check ---
PYDANTIC_V2 = pydantic_version.startswith("2.")
if PYDANTIC_V2:
    from pydantic import model_validator
    logger.info("Using Pydantic V2") # logger can be used now
else:
    logger.info(f"Using Pydantic V1 ({pydantic_version})")


# --- Configuration ---
MODEL_ID = os.getenv("MODEL_ID", "llamaindex/vdr-2b-multi-v1")
DEFAULT_DEVICE_FALLBACK_ORDER = ["cuda", "mps", "cpu"] 
USER_DEVICE_PREFERENCE = os.getenv("DEVICE") 

def get_optimal_device():
    devices_to_try = []
    if USER_DEVICE_PREFERENCE:
        devices_to_try.append(USER_DEVICE_PREFERENCE)
    devices_to_try.extend(DEFAULT_DEVICE_FALLBACK_ORDER)
    
    logger.info(f"Device selection order: {devices_to_try}") # logger is now defined

    for dev_name in devices_to_try:
        try:
            if dev_name.startswith("cuda"):
                if torch.cuda.is_available():
                    if ":" in dev_name: 
                        device_index = int(dev_name.split(":")[1])
                        if device_index < torch.cuda.device_count():
                            logger.info(f"Successfully selected user-preferred/specific CUDA device: {dev_name}")
                            return dev_name
                        else:
                            logger.warning(f"Specific CUDA device {dev_name} requested but not available (max index: {torch.cuda.device_count()-1}). Trying generic CUDA.")
                    else: # Generic "cuda"
                        logger.info(f"Successfully selected CUDA device: cuda")
                        return "cuda:2"
                else:
                    logger.warning(f"CUDA device '{dev_name}' requested but torch.cuda.is_available() is False.")
            elif dev_name == "mps":
                if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() and torch.backends.mps.is_built():
                    logger.info(f"Successfully selected MPS device: mps")
                    return "mps"
                else:
                    logger.warning(f"MPS device requested but not available/built.")
            elif dev_name == "cpu":
                logger.info(f"Successfully selected CPU device: cpu")
                return "cpu"
        except Exception as e:
            logger.warning(f"Could not select device {dev_name}: {e}. Trying next.")
            continue 
            
    logger.error("No suitable Torch device found through probing. Defaulting to CPU, but this may be an issue if a GPU was expected.")
    return "cpu" 

DEVICE = get_optimal_device()
logger.info(f"Final selected device: {DEVICE}") # Log the final device

CACHE_DIR = os.getenv("HF_HOME") or os.getenv("TRANSFORMERS_CACHE") or "/data"
if not os.path.exists(CACHE_DIR):
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        logger.info(f"Created cache directory: {CACHE_DIR}") # logger is defined
    except OSError as e:
        logger.warning(f"Could not create cache directory {CACHE_DIR}: {e}. Using default for HuggingFaceEmbedding.") # logger is defined
        CACHE_DIR = None


embed_model: Optional[HuggingFaceEmbedding] = None

# --- Pydantic Models for API ---
# Models for the "messages" structure (image embedding request)
class ImageUrlDetail(BaseModel):
    url: str

class ContentItem(BaseModel):
    type: str
    text: Optional[str] = None
    image_url: Optional[ImageUrlDetail] = None

class Message(BaseModel):
    role: str
    content: List[ContentItem]

# Unified request model for /v1/embeddings
class ServerEmbeddingRequest(BaseModel):
    input: Optional[Union[str, List[str]]] = None
    messages: Optional[List[Message]] = None
    
    model: Optional[str] = None
    encoding_format: Optional[str] = None
    dimensions: Optional[int] = None

    if PYDANTIC_V2:
        @model_validator(mode='before')
        @classmethod
        def check_exclusive_input_source_v2(cls, data: Any) -> Any:
            if isinstance(data, dict):
                has_input = data.get('input') is not None
                has_messages = data.get('messages') is not None
                if not (has_input ^ has_messages): 
                    raise ValueError("Exactly one of 'input' or 'messages' must be provided in the request body.")
            return data
    else: # Pydantic v1
        @root_validator(skip_on_failure=True)
        def check_exclusive_input_source_v1(cls, values: Dict[str, Any]) -> Dict[str, Any]:
            has_input = values.get('input') is not None
            has_messages = values.get('messages') is not None
            if not (has_input ^ has_messages): 
                raise ValueError("Exactly one of 'input' or 'messages' must be provided in the request body.")
            return values

# Common response models
class EmbeddingData(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int

class UsageInfo(BaseModel):
    prompt_tokens: int
    total_tokens: int

class EmbeddingListResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingData]
    model: str = MODEL_ID 
    usage: UsageInfo

class HealthResponse(BaseModel):
    status: str

class ModelInfoResponse(BaseModel):
    model_id: str
    model_dtype: str
    model_device: str
    max_batch_prefill_tokens: Optional[int] = None 
    engine: str = "LlamaIndex HuggingFaceEmbedding"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global embed_model
    logger.info(f"FastAPI lifespan: Starting up application.") # logger is defined
    logger.info(f"Loading model: {MODEL_ID} on computed device: {DEVICE}")
    logger.info(f"Using Pydantic version: {pydantic_version}")
    logger.info(f"Using cache directory (effective): {CACHE_DIR if CACHE_DIR else 'HuggingFaceEmbedding default'}")
    
    if not os.getenv("HUGGING_FACE_HUB_TOKEN"):
         logger.warning("HUGGING_FACE_HUB_TOKEN not detected by Python script.")
    else:
        logger.info("HUGGING_FACE_HUB_TOKEN detected by Python script.")

    try:
        embed_model = HuggingFaceEmbedding(
            model_name=MODEL_ID,
            device=DEVICE,
            trust_remote_code=True,
            cache_folder=CACHE_DIR,
        )
        logger.info("Performing a warm-up inference for text...")
        _ = embed_model.get_text_embedding("warmup_text")
        logger.info("Model loaded and warmed up successfully.")
    except Exception as e:
        logger.error(f"Failed to load model {MODEL_ID}: {e}", exc_info=True)
        embed_model = None 
    
    yield 
    
    logger.info("FastAPI lifespan: Shutting down and cleaning up model.")
    embed_model = None

app = FastAPI(lifespan=lifespan)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    if embed_model is not None and hasattr(embed_model, '_model'): 
        return HealthResponse(status="ok")
    else:
        logger.error("Health check failed: Model not loaded or not ready.")
        raise HTTPException(status_code=503, detail="Model not ready")

@app.get("/", response_model=ModelInfoResponse)
@app.get("/info", response_model=ModelInfoResponse)
async def get_model_info():
    if embed_model is None or not hasattr(embed_model, '_model'):
        raise HTTPException(status_code=503, detail="Model not loaded or not ready.")
    model_dtype = "unknown"
    if hasattr(embed_model._model, 'dtype'): model_dtype = str(embed_model._model.dtype)
    elif hasattr(embed_model._model, 'config') and hasattr(embed_model._model.config, 'torch_dtype'): model_dtype = str(embed_model._model.config.torch_dtype)
    elif hasattr(embed_model._model, '_first_module') and hasattr(embed_model._model._first_module(), 'dtype'):
        try: model_dtype = str(embed_model._model._first_module().dtype)
        except Exception: pass
    
    max_prefill_env = os.getenv("MAX_BATCH_PREFILL_TOKENS") 
    max_prefill = int(max_prefill_env) if max_prefill_env and max_prefill_env.isdigit() else 40

    return ModelInfoResponse(model_id=MODEL_ID, model_dtype=model_dtype, model_device=str(DEVICE), max_batch_prefill_tokens=max_prefill)

@app.post("/v1/embeddings", response_model=EmbeddingListResponse)
async def create_embeddings(request: ServerEmbeddingRequest):
    if embed_model is None:
        logger.error("Embeddings request failed: Model not loaded.")
        raise HTTPException(status_code=503, detail="Embedding model is not available.")

    embeddings_list: List[List[float]] = []
    prompt_tokens = 0
    
    try:
        if request.input is not None: 
            logger.info("Processing TEXT embedding request (received 'input' field).")
            text_inputs = [request.input] if isinstance(request.input, str) else request.input
            if not all(isinstance(i, str) for i in text_inputs): 
                raise HTTPException(status_code=400, detail="Invalid 'input' field for text embedding.")
            
            embeddings_list = embed_model.get_text_embedding_batch(text_inputs, show_progress=False)
            
            if hasattr(embed_model, '_tokenizer') and embed_model._tokenizer is not None:
                for text_item in text_inputs:
                    try: prompt_tokens += len(embed_model._tokenizer.encode(text_item, add_special_tokens=False))
                    except Exception: prompt_tokens += len(text_item) 
            else: prompt_tokens = sum(len(text_item) for text_item in text_inputs)
            logger.info(f"Successfully generated text embeddings. Tokens: {prompt_tokens}")

        elif request.messages is not None: 
            logger.info("Processing IMAGE embedding request (received 'messages' field).")
            image_url_str = None
            if request.messages and request.messages[0].content:
                for item in request.messages[0].content:
                    if item.type == "image_url" and item.image_url:
                        image_url_str = item.image_url.url
                        break
            
            if not image_url_str:
                logger.error("Image URL not found in 'messages' payload or payload structure incorrect.")
                raise HTTPException(status_code=400, detail="Image URL ('image_url.url') not found in 'messages' payload.")

            if not image_url_str.startswith("data:image/") or ';base64,' not in image_url_str:
                logger.error(f"Invalid base64 data URI format for image: {image_url_str[:100]}...")
                raise HTTPException(status_code=400, detail="Invalid base64 data URI format for image. Expected 'data:image/...;base64,...'.")
            
            try:
                base64_data_part = image_url_str.split(',', 1)[1]
                image_bytes = base64.b64decode(base64_data_part)
                pil_image = Image.open(io.BytesIO(image_bytes))
            except (IndexError, base64.binascii.Error, UnidentifiedImageError) as decode_e: 
                logger.error(f"Failed to decode base64 image or open as PIL Image: {decode_e}", exc_info=True)
                raise HTTPException(status_code=400, detail=f"Invalid base64 image data or unsupported image format: {str(decode_e)}")
            
            embedding = embed_model.get_image_embedding(pil_image)
            embeddings_list.append(embedding)
            prompt_tokens = 1 
            logger.info("Successfully generated image embedding.")
        
        else:
            logger.error("Invalid request: Neither 'input' nor 'messages' field was provided or validated by Pydantic.")
            raise HTTPException(status_code=400, detail="Invalid request: Could not determine embedding type from payload.")

        embeddings_data: List[EmbeddingData] = [EmbeddingData(embedding=emb, index=i) for i, emb in enumerate(embeddings_list)]
        usage = UsageInfo(prompt_tokens=prompt_tokens, total_tokens=prompt_tokens)
        return EmbeddingListResponse(data=embeddings_data, model=MODEL_ID, usage=usage)

    except HTTPException: raise 
    except ValueError as ve: 
        logger.error(f"ValueError during embedding processing: {ve}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error processing embedding request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "$DEFAULT_APP_PORT"))
    host = os.getenv("APP_HOST", "0.0.0.0")
    logger.info(f"Starting Uvicorn server on {host}:{port}")
    logger.info(f"Model cache (HF_HOME) is set to: {os.getenv('HF_HOME')}")
    if os.getenv("HUGGING_FACE_HUB_TOKEN"): logger.info("HUGGING_FACE_HUB_TOKEN is set and detected by Python script.")
    else: logger.warning("HUGGING_FACE_HUB_TOKEN is NOT set or not detected. This may be an issue for private/gated models.")
    uvicorn.run(f"{os.path.splitext(os.path.basename(__file__))[0]}:app", host=host, port=port, reload=False)

EOF
if [ $? -ne 0 ]; then
    print_error "Failed to create Python script $PYTHON_SCRIPT_NAME."
    deactivate &> /dev/null || true
    exit 1
fi

if [ ! -d "$HF_HOME" ]; then
    print_info "Creating cache directory $HF_HOME..."
    mkdir -p "$HF_HOME"
    if [ $? -ne 0 ]; then
        print_warning "Could not create cache directory $HF_HOME."
    fi
fi

print_info "Starting the FastAPI application on port $APP_PORT..."
print_info "Model cache (HF_HOME) will be: $HF_HOME"
if [ -n "$HUGGING_FACE_HUB_TOKEN" ]; then
    print_info "HUGGING_FACE_HUB_TOKEN is set in the environment for the Python script."
else
    print_error "HUGGING_FACE_HUB_TOKEN is NOT set. Critical for private models."
fi
export APP_PORT
export DEVICE # Export user-preferred device to be read by Python script
python3 "$PYTHON_SCRIPT_NAME"
trap 'deactivate &> /dev/null || true; print_info "Exiting script."' EXIT INT TERM
print_info "Embedding API Server setup and execution script finished."
