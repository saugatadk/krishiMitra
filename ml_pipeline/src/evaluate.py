#!/usr/bin/env python3
"""
Stage 4: Evaluation Protocol Pipeline
Supports 3 Distinct Modes:
1. Internal Testing (90:10 Holdout Split)
2. External Testing (Unseen external cardamom test directory)
3. 5-Fold Stratified Cross-Validation (100 epochs/fold with StratifiedKFold)
Generates:
- Macro & per-class Accuracy, Precision, Recall, F1-Score
- High-resolution Confusion Matrix heatmaps (raw counts and normalized percentages)
- Metrics export to JSON and CSV
"""

import os
import sys
import argparse
import json
import csv
import logging
import shutil
import numpy as np
from pathlib import Path

# Add project root to path
CURRENT_DIR = Path(__file__).resolve().parent
PIPELINE_ROOT = CURRENT_DIR.parent
PROJECT_ROOT = PIPELINE_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ultralytics import YOLO
from ml_pipeline.configs import pipeline_config as cfg
from ml_pipeline.src.utils import (
    get_stratified_kfold,
    compute_metrics,
    plot_confusion_matrix,
    plot_learning_curves
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("evaluate")


def run_model_inference_on_dir(model: YOLO, test_dir: Path, class_names: list, device: str = "cpu"):
    """
    Runs batched classification inference across class subfolders in test_dir.
    Returns: (y_true, y_pred, details, aligned_class_names)
    """
    # Dynamically extract and align class names from the trained YOLO model
    if hasattr(model, 'names') and isinstance(model.names, dict):
        aligned_classes = [model.names[i] for i in range(len(model.names))]
    else:
        aligned_classes = class_names

    y_true = []
    y_pred = []
    details = []

    for cls_idx, cls_name in enumerate(aligned_classes):
        cls_dir = test_dir / cls_name
        if not cls_dir.exists():
            continue

        images = sorted(list(cls_dir.glob("*.jpg")) + list(cls_dir.glob("*.png")) + list(cls_dir.glob("*.jpeg")))
        logger.info(f"Evaluating {cls_name}: {len(images)} images...")


        for img_path in images:
            results = model.predict(source=str(img_path), imgsz=cfg.TARGET_IMG_SIZE, device=device, verbose=False)
            if results and len(results) > 0:
                top1_idx = int(results[0].probs.top1)
                top1_conf = float(results[0].probs.top1conf)
                y_true.append(cls_idx)
                y_pred.append(top1_idx)
                details.append({
                    "image": img_path.name,
                    "true_class": cls_name,
                    "pred_class": aligned_classes[top1_idx] if top1_idx < len(aligned_classes) else "Unknown",
                    "confidence": round(top1_conf * 100, 2),
                    "correct": top1_idx == cls_idx
                })

    return y_true, y_pred, details, aligned_classes


def evaluate_holdout(
    weights_path: Path,
    data_dir: Path,
    output_dir: Path,
    split_name: str = "test",
    device: str = "auto"
):
    """
    Mode 1: Internal Testing on the holdout test split.
    """
    opt_device = cfg.get_optimal_device(device)
    logger.info("=" * 60)
    logger.info(f"Running Mode 1: Internal Holdout Testing [{split_name}]")
    logger.info(f"Model Checkpoint: {weights_path}")
    logger.info(f"Dataset Split: {data_dir / split_name}")
    logger.info("=" * 60)

    model = YOLO(str(weights_path))
    test_dir = data_dir / split_name
    if not test_dir.exists():
        raise FileNotFoundError(f"Holdout directory not found at {test_dir}")

    y_true, y_pred, details, eval_classes = run_model_inference_on_dir(
        model, test_dir, cfg.CLASSES, device=opt_device
    )

    metrics = compute_metrics(y_true, y_pred, eval_classes)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save metrics JSON and CSV
    with open(output_dir / "internal_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    with open(output_dir / "internal_predictions.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "true_class", "pred_class", "confidence", "correct"])
        writer.writeheader()
        writer.writerows(details)

    # Plot Confusion Matrix
    cm_path = output_dir / "internal_confusion_matrix.png"
    plot_confusion_matrix(
        metrics["confusion_matrix"],
        eval_classes,
        cm_path,
        title=f"Cardamom YOLOv8 Internal Test Confusion Matrix (Acc: {metrics['accuracy']}%)"
    )

    _print_metrics_summary("Internal Holdout Test (Mode 1)", metrics)
    return metrics



def evaluate_external(
    weights_path: Path,
    external_dir: Path,
    output_dir: Path,
    device: str = "auto"
):
    """
    Mode 2: External Testing on an unseen external directory.
    """
    opt_device = cfg.get_optimal_device(device)
    logger.info("=" * 60)
    logger.info("Running Mode 2: External Generalization Testing")
    logger.info(f"Model Checkpoint: {weights_path}")
    logger.info(f"External Folder: {external_dir}")
    logger.info("=" * 60)

    model = YOLO(str(weights_path))
    if not external_dir.exists():
        raise FileNotFoundError(f"External directory not found at {external_dir}")

    y_true, y_pred, details, eval_classes = run_model_inference_on_dir(
        model, external_dir, cfg.CLASSES, device=opt_device
    )

    metrics = compute_metrics(y_true, y_pred, eval_classes)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "external_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    with open(output_dir / "external_predictions.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "true_class", "pred_class", "confidence", "correct"])
        writer.writeheader()
        writer.writerows(details)

    cm_path = output_dir / "external_confusion_matrix.png"
    plot_confusion_matrix(
        metrics["confusion_matrix"],
        eval_classes,
        cm_path,
        title=f"Cardamom YOLOv8 External Generalization (Acc: {metrics['accuracy']}%)"
    )


    _print_metrics_summary("External Test (Mode 2)", metrics)
    return metrics


def run_stratified_kfold_cv(
    data_dir: Path,
    output_dir: Path,
    model_type: str = "yolov8n-cls",
    n_splits: int = 5,
    epochs: int = 100,
    batch: int = 16,
    pretrained: bool = True,
    device: str = "auto"
):
    """
    Mode 3: Automated 5-Fold Stratified Cross-Validation.
    Trains for `epochs` per fold, logs fold metrics, and calculates Mean ± Std.
    """
    opt_device = cfg.get_optimal_device(device)
    logger.info("=" * 60)
    logger.info(f"Running Mode 3: {n_splits}-Fold Stratified Cross-Validation")
    logger.info(f"Model: {model_type} | Epochs per fold: {epochs} | Pretrained: {pretrained}")
    logger.info(f"Device: {opt_device}")
    logger.info("=" * 60)

    # Collect all images and class labels across train and val splits
    all_images = []
    all_labels = []

    for split in ["train", "val"]:
        for cls_idx, cls_name in enumerate(cfg.CLASSES):
            cls_folder = data_dir / split / cls_name
            if cls_folder.exists():
                for p in cls_folder.glob("*.jpg"):
                    all_images.append(p)
                    all_labels.append(cls_idx)

    total_cv_samples = len(all_images)
    logger.info(f"Total dataset samples for Stratified CV: {total_cv_samples}")

    skf = get_stratified_kfold(n_splits=n_splits, shuffle=True, random_state=42)

    fold_metrics_list = []
    aggregated_cm = np.zeros((len(cfg.CLASSES), len(cfg.CLASSES)), dtype=int)
    cv_working_dir = output_dir / "kfold_splits"

    for fold_idx, (train_indices, val_indices) in enumerate(skf.split(all_images, all_labels)):
        fold_num = fold_idx + 1
        logger.info("-" * 50)
        logger.info(f"🔥 Starting Fold {fold_num}/{n_splits} ({len(train_indices)} train, {len(val_indices)} val)...")
        logger.info("-" * 50)

        fold_dir = cv_working_dir / f"fold_{fold_num}"
        fold_train = fold_dir / "train"
        fold_val = fold_dir / "val"

        # Create fold directory structures
        for cls_name in cfg.CLASSES:
            (fold_train / cls_name).mkdir(parents=True, exist_ok=True)
            (fold_val / cls_name).mkdir(parents=True, exist_ok=True)

        # Populate fold with symlinks / copies
        for idx in train_indices:
            src = all_images[idx]
            dst = fold_train / cfg.CLASSES[all_labels[idx]] / src.name
            if not dst.exists():
                shutil.copy(str(src), str(dst))

        for idx in val_indices:
            src = all_images[idx]
            dst = fold_val / cfg.CLASSES[all_labels[idx]] / src.name
            if not dst.exists():
                shutil.copy(str(src), str(dst))

        # Initialize model for this fold
        model_name = cfg.get_model_weights_path(model_type) if pretrained else f"{model_type}.yaml"
        model = YOLO(model_name)
        aug = cfg.PATHOLOGY_AUGMENTATIONS


        # Train fold
        model.train(
            data=str(fold_dir),
            epochs=epochs,
            imgsz=cfg.TARGET_IMG_SIZE,
            batch=batch,
            device=opt_device,
            workers=4,
            cache='ram',
            project=str(output_dir / "kfold_training"),
            name=f"fold_{fold_num}",
            hsv_h=aug["hsv_h"],
            hsv_s=aug["hsv_s"],
            hsv_v=aug["hsv_v"],
            degrees=aug["degrees"],
            translate=aug["translate"],
            scale=aug["scale"],
            fliplr=aug["fliplr"],
            flipud=aug["flipud"],
            verbose=False
        )

        # Evaluate fold on validation partition
        y_true, y_pred, _, eval_classes = run_model_inference_on_dir(
            model, fold_val, cfg.CLASSES, device=opt_device
        )
        fold_m = compute_metrics(y_true, y_pred, eval_classes)
        fold_metrics_list.append(fold_m)
        aggregated_cm += np.array(fold_m["confusion_matrix"])

        logger.info(f"Fold {fold_num} Result: Accuracy={fold_m['accuracy']}% | F1={fold_m['macro_f1']}%")

    # Compute Cross-Validation Summary (Mean ± Std)
    accuracies = [m["accuracy"] for m in fold_metrics_list]
    f1_scores = [m["macro_f1"] for m in fold_metrics_list]
    precisions = [m["macro_precision"] for m in fold_metrics_list]
    recalls = [m["macro_recall"] for m in fold_metrics_list]

    cv_summary = {
        "n_splits": n_splits,
        "epochs_per_fold": epochs,
        "mean_accuracy": round(float(np.mean(accuracies)), 2),
        "std_accuracy": round(float(np.std(accuracies)), 2),
        "mean_macro_f1": round(float(np.mean(f1_scores)), 2),
        "std_macro_f1": round(float(np.std(f1_scores)), 2),
        "mean_macro_precision": round(float(np.mean(precisions)), 2),
        "std_macro_precision": round(float(np.std(precisions)), 2),
        "mean_macro_recall": round(float(np.mean(recalls)), 2),
        "std_macro_recall": round(float(np.std(recalls)), 2),
        "per_fold_accuracies": accuracies,
        "per_fold_f1_scores": f1_scores,
        "aggregated_confusion_matrix": aggregated_cm.tolist()
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "cross_validation_report.json", "w") as f:
        json.dump(cv_summary, f, indent=2)

    with open(output_dir / "cross_validation_report.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Mean", "StdDev"])
        writer.writerow(["Accuracy (%)", cv_summary["mean_accuracy"], cv_summary["std_accuracy"]])
        writer.writerow(["Macro F1-Score (%)", cv_summary["mean_macro_f1"], cv_summary["std_macro_f1"]])
        writer.writerow(["Macro Precision (%)", cv_summary["mean_macro_precision"], cv_summary["std_macro_precision"]])
        writer.writerow(["Macro Recall (%)", cv_summary["mean_macro_recall"], cv_summary["std_macro_recall"]])

    # Plot Aggregated 5-Fold Confusion Matrix
    cm_path = output_dir / "kfold_aggregated_confusion_matrix.png"
    plot_confusion_matrix(
        aggregated_cm,
        eval_classes,
        cm_path,
        title=f"5-Fold Cross-Validation Aggregated Confusion Matrix (Mean: {cv_summary['mean_accuracy']} ± {cv_summary['std_accuracy']}%)"
    )


    logger.info("=" * 60)
    logger.info(f"🏆 5-Fold Stratified Cross-Validation Complete!")
    logger.info(f"Mean Accuracy:     {cv_summary['mean_accuracy']}% ± {cv_summary['std_accuracy']}%")
    logger.info(f"Mean Macro F1:     {cv_summary['mean_macro_f1']}% ± {cv_summary['std_macro_f1']}%")
    logger.info(f"Mean Precision:    {cv_summary['mean_macro_precision']}% ± {cv_summary['std_macro_precision']}%")
    logger.info(f"Mean Recall:       {cv_summary['mean_macro_recall']}% ± {cv_summary['std_macro_recall']}%")
    logger.info(f"Summary Report:    {output_dir / 'cross_validation_report.json'}")
    logger.info(f"Confusion Matrix:  {cm_path}")
    logger.info("=" * 60)

    return cv_summary


def _print_metrics_summary(title: str, metrics: dict):
    logger.info("=" * 60)
    logger.info(f"📊 {title} Summary")
    logger.info(f"Total Evaluated:   {metrics['total_samples']}")
    logger.info(f"Overall Accuracy:  {metrics['accuracy']}%")
    logger.info(f"Macro Precision:   {metrics['macro_precision']}%")
    logger.info(f"Macro Recall:      {metrics['macro_recall']}%")
    logger.info(f"Macro F1-Score:    {metrics['macro_f1']}%")
    logger.info("-" * 50)
    logger.info("Class-wise Metrics:")
    for cls_name, vals in metrics["per_class"].items():
        logger.info(f"  * {cls_name:24s} | Prec: {vals['precision']:5.1f}% | Rec: {vals['recall']:5.1f}% | F1: {vals['f1_score']:5.1f}% | Support: {vals['support']}")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Stage 4: Cardamom Leaf Multi-Mode Evaluation Protocol")
    parser.add_argument("--mode", type=str, default="holdout", choices=["holdout", "external", "kfold"], help="Evaluation mode")
    parser.add_argument("--weights", type=str, default=str(cfg.MODELS_DIR / "cardamom_classifier_best.pt"), help="Path to trained YOLOv8 model checkpoint")
    parser.add_argument("--data-dir", type=str, default=str(cfg.PROCESSED_DATA_DIR), help="Path to preprocessed dataset")
    parser.add_argument("--external-dir", type=str, default=None, help="Path to external test directory (for mode 'external')")
    parser.add_argument("--out-dir", type=str, default=str(cfg.RUNS_DIR / "evaluation"), help="Output directory for reports & plots")
    parser.add_argument("--splits", type=int, default=5, help="Number of folds for cross-validation")
    parser.add_argument("--epochs", type=int, default=cfg.DEFAULT_EPOCHS, help="Epochs per fold for cross-validation")
    parser.add_argument("--batch", type=int, default=cfg.DEFAULT_BATCH_SIZE, help="Batch size for cross-validation")
    parser.add_argument("--device", type=str, default="auto", help="Hardware device")

    args = parser.parse_args()
    out_path = Path(args.out_dir)

    if args.mode == "holdout":
        evaluate_holdout(
            weights_path=Path(args.weights),
            data_dir=Path(args.data_dir),
            output_dir=out_path,
            split_name="test",
            device=args.device
        )
    elif args.mode == "external":
        if not args.external_dir:
            logger.error("--external-dir is required when --mode external is selected.")
            sys.exit(1)
        evaluate_external(
            weights_path=Path(args.weights),
            external_dir=Path(args.external_dir),
            output_dir=out_path,
            device=args.device
        )
    elif args.mode == "kfold":
        run_stratified_kfold_cv(
            data_dir=Path(args.data_dir),
            output_dir=out_path,
            model_type=cfg.DEFAULT_YOLO_MODEL,
            n_splits=args.splits,
            epochs=args.epochs,
            batch=args.batch,
            pretrained=True,
            device=args.device
        )


if __name__ == "__main__":
    main()
