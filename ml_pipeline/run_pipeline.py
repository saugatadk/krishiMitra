#!/usr/bin/env python3
"""
Master Orchestrator: End-to-End Cardamom Leaf Disease Detection Pipeline
Stages:
  1 & 2: Background Removal (U2-Net) & Preprocessing (Resizer to 224x224x3)
  3:     YOLOv8 Classification Training (Scratch vs Transfer Learning)
  4:     Evaluation Protocol (Internal Holdout, External Test, 5-Fold Stratified CV)
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml_pipeline.configs import pipeline_config as cfg
from ml_pipeline.src.preprocess import run_preprocessing
from ml_pipeline.src.train_yolo import train_classifier
from ml_pipeline.src.evaluate import evaluate_holdout, evaluate_external, run_stratified_kfold_cv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pipeline_runner")


def main():
    parser = argparse.ArgumentParser(
        description="🌿 KrishiMitra Cardamom Leaf Disease Detection Pipeline (U2-Net + YOLOv8)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--stage",
        type=str,
        default="all",
        choices=["all", "preprocess", "train", "evaluate"],
        help="Pipeline stage to execute"
    )
    parser.add_argument("--raw-dir", type=str, default=str(cfg.FALLBACK_RAW_DIR), help="Path to raw cardamom dataset")
    parser.add_argument("--processed-dir", type=str, default=str(cfg.PROCESSED_DATA_DIR), help="Path to preprocessed dataset")
    parser.add_argument("--model", type=str, default=cfg.DEFAULT_YOLO_MODEL, choices=cfg.SUPPORTED_MODELS, help="YOLOv8 classification model")
    parser.add_argument("--pretrained", action="store_true", default=True, help="Use transfer learning with pretrained weights")
    parser.add_argument("--from-scratch", action="store_true", help="Train from scratch without pretrained weights")
    parser.add_argument("--epochs", type=int, default=cfg.DEFAULT_EPOCHS, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=cfg.DEFAULT_BATCH_SIZE, help="Batch size")
    parser.add_argument("--eval-mode", type=str, default="holdout", choices=["holdout", "external", "kfold"], help="Evaluation mode")
    parser.add_argument("--external-dir", type=str, default=None, help="Path to external test folder (for eval-mode 'external')")
    parser.add_argument("--splits", type=int, default=5, help="Number of folds for cross-validation")
    parser.add_argument("--device", type=str, default="auto", help="Hardware device (auto/cpu/0)")
    parser.add_argument("--intermediates", type=int, default=5, help="Number of visual verification samples per class")
    parser.add_argument("--force-unet", action="store_true", help="Disable smart bypass and force U2-Net on all images")

    args = parser.parse_args()
    pretrained = False if args.from_scratch else args.pretrained
    smart_bypass = not args.force_unet
    device = cfg.get_optimal_device(args.device)

    logger.info("=" * 70)
    logger.info("🚀 KrishiMitra Cardamom Leaf Disease Detection Pipeline")
    logger.info(f"Target Stage:       {args.stage.upper()}")
    logger.info(f"Target Classes:     {', '.join(cfg.CLASSES)}")
    logger.info(f"YOLO Model:         {args.model} ({'Pretrained' if pretrained else 'From Scratch'})")
    logger.info(f"Hardware Device:    {device}")
    logger.info(f"Smart Bypass:       {smart_bypass}")
    logger.info("=" * 70)

    # ----------------------------------------------------
    # Stage 1 & 2: Preprocessing & Background Removal
    # ----------------------------------------------------
    if args.stage in ["all", "preprocess"]:
        logger.info("\n>>> STAGE 1 & 2: U2-Net Background Removal & 224x224 Resizing <<<")
        run_preprocessing(
            raw_data_dir=Path(args.raw_dir),
            processed_data_dir=Path(args.processed_dir),
            target_size=cfg.TARGET_IMG_SIZE,
            smart_bypass=smart_bypass,
            intermediates_count=args.intermediates,
            device=device
        )

    # ----------------------------------------------------
    # Stage 3: YOLOv8 Classification Training
    # ----------------------------------------------------
    best_weights = cfg.MODELS_DIR / "cardamom_classifier_best.pt"
    if args.stage in ["all", "train"]:
        logger.info("\n>>> STAGE 3: YOLOv8 Classification Training <<<")
        train_res = train_classifier(
            data_dir=Path(args.processed_dir),
            model_type=args.model,
            pretrained=pretrained,
            epochs=args.epochs,
            imgsz=cfg.TARGET_IMG_SIZE,
            batch=args.batch,
            device=device,
            project=str(cfg.RUNS_DIR),
            name=f"{args.model}_{'pretrained' if pretrained else 'scratch'}"
        )
        best_weights = Path(train_res["best_pt"])

    # ----------------------------------------------------
    # Stage 4: Multi-Mode Evaluation Protocol
    # ----------------------------------------------------
    if args.stage in ["all", "evaluate"]:
        logger.info(f"\n>>> STAGE 4: Evaluation Protocol [Mode: {args.eval_mode.upper()}] <<<")
        eval_out = cfg.RUNS_DIR / "evaluation"

        if args.eval_mode == "holdout":
            evaluate_holdout(
                weights_path=best_weights,
                data_dir=Path(args.processed_dir),
                output_dir=eval_out / "holdout_test",
                split_name="test",
                device=device
            )
        elif args.eval_mode == "external":
            if not args.external_dir:
                logger.error("--external-dir must be provided for external evaluation.")
                sys.exit(1)
            evaluate_external(
                weights_path=best_weights,
                external_dir=Path(args.external_dir),
                output_dir=eval_out / "external_test",
                device=device
            )
        elif args.eval_mode == "kfold":
            run_stratified_kfold_cv(
                data_dir=Path(args.processed_dir),
                output_dir=eval_out / f"kfold_{args.splits}",
                model_type=args.model,
                n_splits=args.splits,
                epochs=args.epochs,
                batch=args.batch,
                pretrained=pretrained,
                device=device
            )

    logger.info("\n" + "=" * 70)
    logger.info("🎉 Pipeline execution successfully completed!")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
