#!/usr/bin/env python3
"""
Stage 3: YOLOv8 Classification Training Pipeline
- Supports Ultralytics classification models: yolov8n-cls, yolov8s-cls, yolov8m-cls, yolov8l-cls
- Toggles between training from scratch (pretrained=False) and transfer learning (pretrained=True)
- Pathology-safe augmentations preserving diagnostic lesion hue
- 100 epochs default at 224x224
- Exports best checkpoint to backend/api/ml_models/ and ONNX format
"""

import os
import sys
import argparse
import shutil
import logging
from pathlib import Path

# Add project root to path
CURRENT_DIR = Path(__file__).resolve().parent
PIPELINE_ROOT = CURRENT_DIR.parent
PROJECT_ROOT = PIPELINE_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ultralytics import YOLO
from ml_pipeline.configs import pipeline_config as cfg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_yolo")


def train_classifier(
    data_dir: Path,
    model_type: str = "yolov8n-cls",
    pretrained: bool = True,
    epochs: int = 100,
    imgsz: int = 224,
    batch: int = 16,
    device: str = "auto",
    project: str = None,
    name: str = None,
    export_onnx: bool = True
):
    """
    Executes YOLOv8 classification training.
    """
    opt_device = cfg.get_optimal_device(device)
    logger.info("=" * 60)
    logger.info(f"Starting YOLOv8 Cardamom Classification Training")
    logger.info(f"Model: {model_type}")
    logger.info(f"Transfer Learning (Pretrained): {pretrained}")
    logger.info(f"Epochs: {epochs} | Image Size: {imgsz} | Batch Size: {batch}")
    logger.info(f"Device: {opt_device}")
    logger.info(f"Dataset Path: {data_dir}")
    logger.info("=" * 60)

    # Model initialization
    if pretrained:
        # Transfer learning from ImageNet checkpoint (use local weights if available)
        weights_name = cfg.get_model_weights_path(model_type)
        logger.info(f"Initializing transfer learning with weights: {weights_name}")
        model = YOLO(weights_name)

    else:
        # Train from scratch using YAML architecture specification
        yaml_name = f"{model_type}.yaml"
        logger.info(f"Initializing model from scratch with architecture: {yaml_name}")
        model = YOLO(yaml_name)

    project_dir = project or str(cfg.RUNS_DIR)
    exp_name = name or f"{model_type}_{'pretrained' if pretrained else 'scratch'}"

    # Pathology-safe augmentation configuration
    aug = cfg.PATHOLOGY_AUGMENTATIONS

    # Execute training
    results = model.train(
        data=str(data_dir),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=opt_device,
        project=project_dir,
        name=exp_name,
        # Pathology-safe augmentations
        hsv_h=aug["hsv_h"],
        hsv_s=aug["hsv_s"],
        hsv_v=aug["hsv_v"],
        degrees=aug["degrees"],
        translate=aug["translate"],
        scale=aug["scale"],
        fliplr=aug["fliplr"],
        flipud=aug["flipud"],
        erasing=aug["erasing"],
        verbose=True,
        save=True,
        plots=True,
        workers=4,
        exist_ok=True
    )



    save_dir = Path(results.save_dir) if hasattr(results, "save_dir") else Path(project_dir) / exp_name
    best_pt = save_dir / "weights" / "best.pt"

    logger.info(f"Training completed. Checkpoint saved at: {best_pt}")

    # Copy best model to backend/api/ml_models/
    target_models_dir = cfg.MODELS_DIR
    target_models_dir.mkdir(parents=True, exist_ok=True)
    prod_target = target_models_dir / f"cardamom_{model_type}_{'pretrained' if pretrained else 'scratch'}.pt"

    if best_pt.exists():
        shutil.copy(str(best_pt), str(prod_target))
        # Also copy as active default classifier
        shutil.copy(str(best_pt), str(target_models_dir / "cardamom_classifier_best.pt"))
        logger.info(f"✅ Exported production weights to: {prod_target}")

    # Export to ONNX if requested
    onnx_path = None
    if export_onnx and best_pt.exists():
        try:
            logger.info("Exporting trained model to ONNX format...")
            onnx_model = YOLO(str(best_pt))
            onnx_path = onnx_model.export(format="onnx", imgsz=imgsz, dynamic=False)
            logger.info(f"✅ ONNX Export complete: {onnx_path}")
        except Exception as e:
            logger.warning(f"ONNX export warning: {e}")

    return {
        "save_dir": str(save_dir),
        "best_pt": str(best_pt),
        "prod_weights": str(prod_target),
        "onnx_path": str(onnx_path) if onnx_path else None
    }


def main():
    parser = argparse.ArgumentParser(description="Stage 3: Cardamom Leaf YOLOv8 Classification Training")
    parser.add_argument("--data-dir", type=str, default=str(cfg.PROCESSED_DATA_DIR), help="Path to preprocessed dataset")
    parser.add_argument("--model", type=str, default=cfg.DEFAULT_YOLO_MODEL, choices=cfg.SUPPORTED_MODELS, help="YOLOv8-cls model architecture")
    parser.add_argument("--pretrained", action="store_true", default=True, help="Enable transfer learning (default: True)")
    parser.add_argument("--from-scratch", action="store_true", help="Train from scratch (disables pretrained weights)")
    parser.add_argument("--epochs", type=int, default=cfg.DEFAULT_EPOCHS, help="Number of epochs (default: 100)")
    parser.add_argument("--imgsz", type=int, default=cfg.IMG_SIZE, help="Image resolution (default: 224)")
    parser.add_argument("--batch", type=int, default=cfg.DEFAULT_BATCH_SIZE, help="Batch size (default: 16)")
    parser.add_argument("--device", type=str, default="auto", help="Hardware device (auto/cpu/0)")
    parser.add_argument("--project", type=str, default=str(cfg.RUNS_DIR), help="Output project directory")
    parser.add_argument("--name", type=str, default=None, help="Experiment run name")
    parser.add_argument("--no-onnx", action="store_true", help="Skip ONNX export")

    args = parser.parse_args()

    pretrained = False if args.from_scratch else args.pretrained

    train_classifier(
        data_dir=Path(args.data_dir),
        model_type=args.model,
        pretrained=pretrained,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
        export_onnx=not args.no_onnx
    )


if __name__ == "__main__":
    main()
