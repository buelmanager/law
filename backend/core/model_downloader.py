"""
Model download utility using huggingface_hub
Downloads Qwen2.5-7B-Instruct GGUF model for CPU inference
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Default model configuration
# Using bartowski's quantized GGUF model (well-maintained community repo)
DEFAULT_MODEL_REPO = "bartowski/Qwen2.5-7B-Instruct-GGUF"
DEFAULT_MODEL_FILE = "Qwen2.5-7B-Instruct-Q4_K_M.gguf"
DEFAULT_MODEL_DIR = "./models"


def download_model(
    repo_id: str = DEFAULT_MODEL_REPO,
    filename: str = DEFAULT_MODEL_FILE,
    local_dir: str = DEFAULT_MODEL_DIR,
    force: bool = False,
) -> str:
    """
    Download GGUF model from HuggingFace Hub

    Args:
        repo_id: HuggingFace repository ID
        filename: Model filename to download
        local_dir: Local directory to save the model
        force: Force re-download even if file exists

    Returns:
        Path to the downloaded model file
    """
    from huggingface_hub import hf_hub_download

    local_path = Path(local_dir) / filename

    # Check if model already exists
    if local_path.exists() and not force:
        logger.info(f"Model already exists at {local_path}")
        return str(local_path)

    # Create directory if not exists
    Path(local_dir).mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading model {repo_id}/{filename}...")
    logger.info("This may take a few minutes depending on your connection...")

    try:
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
        )
        logger.info(f"Model downloaded successfully to {downloaded_path}")
        return downloaded_path
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        raise


def ensure_model_exists(
    model_path: str = None,
    repo_id: str = DEFAULT_MODEL_REPO,
    filename: str = DEFAULT_MODEL_FILE,
) -> str:
    """
    Ensure model exists at the specified path, download if necessary

    Args:
        model_path: Expected path to the model file
        repo_id: HuggingFace repository ID (used if download needed)
        filename: Model filename (used if download needed)

    Returns:
        Path to the model file
    """
    if model_path is None:
        model_path = os.path.join(DEFAULT_MODEL_DIR, filename)

    if os.path.exists(model_path):
        logger.info(f"Model found at {model_path}")
        return model_path

    # Model not found, download it
    logger.info(f"Model not found at {model_path}, downloading...")
    local_dir = os.path.dirname(model_path)
    return download_model(repo_id=repo_id, filename=filename, local_dir=local_dir)


def get_model_info() -> dict:
    """
    Get information about the default model

    Returns:
        Dictionary with model info
    """
    return {
        "repo_id": DEFAULT_MODEL_REPO,
        "filename": DEFAULT_MODEL_FILE,
        "local_dir": DEFAULT_MODEL_DIR,
        "expected_path": os.path.join(DEFAULT_MODEL_DIR, DEFAULT_MODEL_FILE),
    }
