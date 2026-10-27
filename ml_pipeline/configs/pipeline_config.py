"""
Centralized Configuration for Cardamom Leaf Disease Detection Pipeline
Stages:
1. Saliency Segmentation (U2-Net)
2. Background Masking & 224x224 Resizing
3. YOLOv8 Classification (yolov8-cls)
4. Multi-Mode Evaluation Protocol
"""

import os
import torch
from pathlib import Path

# Base Paths
CONFIG_DIR = Path(__file__).resolve().parent
PIPELINE_ROOT = CONFIG_DIR.parent
PROJECT_ROOT = PIPELINE_ROOT.parent

# Dataset Directories
RAW_DATA_DIR = PIPELINE_ROOT / "data" / "raw"
FALLBACK_RAW_DIR = RAW_DATA_DIR
PROCESSED_DATA_DIR = PIPELINE_ROOT / "data" / "processed"
INTERMEDIATES_DIR = PROCESSED_DATA_DIR / "intermediates"


# Model Checkpoints & Output Runs
MODELS_DIR = PROJECT_ROOT / "backend" / "api" / "ml_models"
U2NET_WEIGHTS_PATH = MODELS_DIR / "u2net.pth"
RUNS_DIR = PIPELINE_ROOT / "runs" / "cardamom_cls"


def get_model_weights_path(model_type: str = "yolov8n-cls") -> str:
    """
    Returns path to local cached weights in MODELS_DIR if present,
    preventing rogue downloads into the root directory.
    """
    local_weights = MODELS_DIR / f"{model_type}.pt"
    if local_weights.exists():
        return str(local_weights)
    return f"{model_type}.pt"


# Target Classes & Raw Folder Mapping
CLASSES = [
    "Colletotrichum_Blight",
    "Healthy",
    "Phyllosticta_Leaf_Spot"
]

CLASS_TO_IDX = {cls_name: idx for idx, cls_name in enumerate(CLASSES)}
IDX_TO_CLASS = {idx: cls_name for idx, cls_name in enumerate(CLASSES)}


RAW_FOLDER_MAP = {
    "Blight1000": "Colletotrichum_Blight",
    "Phylosticta_LS_1000": "Phyllosticta_Leaf_Spot",
    "Healthy_1000": "Healthy",
    # Direct matches if already standardized
    "Colletotrichum_Blight": "Colletotrichum_Blight",
    "Phyllosticta_Leaf_Spot": "Phyllosticta_Leaf_Spot",
    "Healthy": "Healthy"
}

# Image Dimension Specifications
U2NET_INPUT_SIZE = 320     # (320, 320) for U2-Net saliency map generation
TARGET_IMG_SIZE = 224      # (224, 224, 3) for YOLOv8 classification input
IMG_SIZE = TARGET_IMG_SIZE

# Training Hyperparameters
DEFAULT_YOLO_MODEL = "yolov8n-cls"
SUPPORTED_MODELS = ["yolov8n-cls", "yolov8s-cls", "yolov8m-cls", "yolov8l-cls"]
DEFAULT_EPOCHS = 100
DEFAULT_BATCH_SIZE = 16
DEFAULT_LR = 0.001

# Pathology-Safe Augmentation Parameters
# Crucial: Disable aggressive hue shifts (hsv_h) to preserve diagnostic lesion discoloration
PATHOLOGY_AUGMENTATIONS = {
    "hsv_h": 0.01,         # Minimal hue jitter (prevents turning brown necrosis green or yellow halo blue)
    "hsv_s": 0.4,          # Modest saturation change
    "hsv_v": 0.4,          # Light intensity change
    "degrees": 15.0,       # Foliage rotation
    "translate": 0.1,      # Slight translation
    "scale": 0.2,          # Random scaling
    "fliplr": 0.5,         # Horizontal flip (pathology-invariant)
    "flipud": 0.5,         # Vertical flip (pathology-invariant)
    "erasing": 0.1,        # Minimal random erasing
}


def get_optimal_device(requested_device: str = "auto") -> str:
    """
    Selects the optimal hardware device.
    Supports CUDA on GPUs with CC >= 6.0 (e.g. GeForce MX230 CC 6.1).
    """
    req = str(requested_device).lower().strip()
    if req in ["cpu"]:
        return "cpu"

    if req in ["0", "cuda", "cuda:0", "gpu"]:
        if torch.cuda.is_available():
            major, minor = torch.cuda.get_device_capability(0)
            if major >= 6:
                return "0"
            return "cpu"
        return "cpu"

    # Auto mode
    if torch.cuda.is_available():
        major, minor = torch.cuda.get_device_capability(0)
        if major >= 6:
            return "0"
    return "cpu"
