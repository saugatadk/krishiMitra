#!/usr/bin/env python3
"""
Stage 1 & 2: Background Removal (U2-Net) & Image Preprocessing Pipeline
- Saliency Segmentation via U2-Net
- Smart Adaptive Bypass for images that already have a clean black background
- Bitwise AND operation (cv2.bitwise_and) setting background to black (0, 0, 0)
- Image Resizer to 224x224x3
- Intermediate artifact logging (original, binary mask, segmented, resized_224)
- Standard Ultralytics classification directory structure (train/val/test)
"""

import os
import sys
import argparse
import logging
import shutil
import cv2
import numpy as np
from pathlib import Path

# Add project root to path
CURRENT_DIR = Path(__file__).resolve().parent
PIPELINE_ROOT = CURRENT_DIR.parent
PROJECT_ROOT = PIPELINE_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
from ml_pipeline.configs import pipeline_config as cfg
from ml_pipeline.models.u2net import load_u2net_model, predict_leaf_mask

# Optimize multi-core CPU inference
if torch.get_num_threads() < 8:
    torch.set_num_threads(min(8, os.cpu_count() or 4))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("preprocess")



def has_black_background(
    img_bgr: np.ndarray,
    threshold: int = 30,
    border_fraction: float = 0.60,
    min_overall_ratio: float = 0.25
) -> bool:
    """
    Detects if an image already has an isolated black background
    by inspecting the 4 image corners, edge perimeter borders, and overall dark ratio.
    Prevents running U2-Net on pre-segmented images to avoid lesion boundary erosion.
    """
    h, w = img_bgr.shape[:2]

    # 1. Sample 10x10 patches in the 4 corners
    patch_size = max(5, int(min(h, w) * 0.02))
    c_tl = np.mean(img_bgr[:patch_size, :patch_size]) <= threshold
    c_tr = np.mean(img_bgr[:patch_size, -patch_size:]) <= threshold
    c_bl = np.mean(img_bgr[-patch_size:, :patch_size]) <= threshold
    c_br = np.mean(img_bgr[-patch_size:, -patch_size:]) <= threshold
    dark_corners = sum([c_tl, c_tr, c_bl, c_br])

    # 2. Sample 4 perimeter borders
    bt = max(2, int(min(h, w) * 0.02))
    top = img_bgr[0:bt, :]
    bottom = img_bgr[-bt:, :]
    left = img_bgr[:, 0:bt]
    right = img_bgr[:, -bt:]

    border_pixels = np.vstack([
        top.reshape(-1, 3),
        bottom.reshape(-1, 3),
        left.reshape(-1, 3),
        right.reshape(-1, 3)
    ])

    border_black_ratio = np.mean(np.all(border_pixels <= threshold, axis=1))

    # 3. Overall image dark pixel ratio
    overall_black_ratio = np.mean(np.all(img_bgr <= threshold, axis=2))

    return dark_corners >= 3 and border_black_ratio >= border_fraction and overall_black_ratio >= min_overall_ratio



def process_single_image(
    img_path: Path,
    u2net_model,
    device: str,
    target_size: int = 224,
    smart_bypass: bool = True
):
    """
    Processes one leaf image:
    1. Checks if background is already black (smart bypass).
    2. If not, passes through U2-Net to generate binary mask.
    3. Applies cv2.bitwise_and to black out non-leaf background.
    4. Resizes to target_size x target_size x 3.
    Returns: (orig_bgr, binary_mask, segmented_bgr, resized_bgr, bypassed)
    """
    orig_bgr = cv2.imread(str(img_path))
    if orig_bgr is None:
        raise ValueError(f"Could not read image: {img_path}")

    h_orig, w_orig = orig_bgr.shape[:2]

    # Check for pre-existing black background
    if smart_bypass and has_black_background(orig_bgr):
        # Already black background - create clean identity mask
        binary_mask = (np.any(orig_bgr > 20, axis=2)).astype(np.uint8) * 255
        segmented_bgr = orig_bgr.copy()
        resized_bgr = cv2.resize(segmented_bgr, (target_size, target_size), interpolation=cv2.INTER_AREA)
        return orig_bgr, binary_mask, segmented_bgr, resized_bgr, True

    # Saliency segmentation with U2-Net
    binary_mask = predict_leaf_mask(orig_bgr, u2net_model, device=device, threshold=0.5)

    # Bitwise AND: retain only leaf pixels, turn background strictly black (0, 0, 0)
    segmented_bgr = cv2.bitwise_and(orig_bgr, orig_bgr, mask=binary_mask)

    # Resize to standardized classification resolution (224 x 224 x 3)
    resized_bgr = cv2.resize(segmented_bgr, (target_size, target_size), interpolation=cv2.INTER_AREA)

    return orig_bgr, binary_mask, segmented_bgr, resized_bgr, False


def run_preprocessing(
    raw_data_dir: Path,
    processed_data_dir: Path,
    target_size: int = 224,
    smart_bypass: bool = True,
    intermediates_count: int = 5,
    max_per_class: int = None,
    device: str = "cpu"
):
    """
    Traverses raw dataset splits (train, val, test), runs U2-Net background removal
    and resizes to 224x224x3 in the Ultralytics classification format.
    """
    logger.info("Initializing U2-Net background removal pipeline...")
    logger.info(f"Target Resolution: {target_size}x{target_size}x3")
    logger.info(f"Smart Background Bypass: {smart_bypass}")
    logger.info(f"Device: {device}")

    u2net_model = load_u2net_model(cfg.U2NET_WEIGHTS_PATH, device=device)

    # Create directories
    intermediates_dir = processed_data_dir / "intermediates"
    intermediates_dir.mkdir(parents=True, exist_ok=True)

    # Check source dataset
    source_dir = raw_data_dir if raw_data_dir.exists() else cfg.FALLBACK_RAW_DIR
    if not source_dir.exists():
        raise FileNotFoundError(f"Source dataset directory not found at {raw_data_dir} or {cfg.FALLBACK_RAW_DIR}")

    logger.info(f"Ingesting raw images from: {source_dir}")

    total_processed = 0
    total_bypassed = 0
    saved_intermediates = {cls_name: 0 for cls_name in cfg.CLASSES}

    # Iterate splits (train, val, test)
    splits = [d.name for d in source_dir.iterdir() if d.is_dir() and d.name in ["train", "val", "test"]]
    if not splits:
        # Flat directory structure fallback
        splits = ["train"]

    for split in sorted(splits):
        split_src = source_dir / split
        split_dst = processed_data_dir / split

        for raw_folder, std_class in cfg.RAW_FOLDER_MAP.items():
            class_src = split_src / raw_folder
            if not class_src.exists():
                continue

            class_dst = split_dst / std_class
            class_dst.mkdir(parents=True, exist_ok=True)

            image_files = sorted(list(class_src.glob("*.jpg")) + list(class_src.glob("*.png")) + list(class_src.glob("*.jpeg")))
            if max_per_class and max_per_class > 0:
                image_files = image_files[:max_per_class]

            logger.info(f"Processing [{split}] {std_class}: {len(image_files)} images...")

            for idx, img_path in enumerate(image_files):
                try:
                    orig, mask, segmented, resized, bypassed = process_single_image(
                        img_path,
                        u2net_model,
                        device=device,
                        target_size=target_size,
                        smart_bypass=smart_bypass
                    )

                    # Save preprocessed image in dataset destination
                    dst_filename = f"{std_class}_{split}_{idx:04d}.jpg"
                    dst_path = class_dst / dst_filename
                    cv2.imwrite(str(dst_path), resized)

                    total_processed += 1
                    if bypassed:
                        total_bypassed += 1

                    if (idx + 1) % 50 == 0 or (idx + 1) == len(image_files):
                        logger.info(f"  --> [{split}] {std_class}: {idx + 1}/{len(image_files)} processed (Total bypassed so far: {total_bypassed})")

                    # Save intermediate inspection outputs
                    if saved_intermediates[std_class] < intermediates_count:
                        sample_id = f"{std_class}_{saved_intermediates[std_class] + 1}"
                        cv2.imwrite(str(intermediates_dir / f"original_{sample_id}.jpg"), orig)
                        cv2.imwrite(str(intermediates_dir / f"mask_{sample_id}.png"), mask)
                        cv2.imwrite(str(intermediates_dir / f"segmented_{sample_id}.jpg"), segmented)
                        cv2.imwrite(str(intermediates_dir / f"resized_224_{sample_id}.jpg"), resized)
                        saved_intermediates[std_class] += 1


                except Exception as e:
                    logger.warning(f"Error processing {img_path.name}: {e}")

    logger.info("=" * 60)
    logger.info("✅ Preprocessing Complete!")
    logger.info(f"Total Images Processed: {total_processed}")
    logger.info(f"Smart Bypass (Already Black BG): {total_bypassed} ({total_bypassed/max(1, total_processed)*100:.1f}%)")
    logger.info(f"U2-Net Segmented: {total_processed - total_bypassed}")
    logger.info(f"Preprocessed Dataset Directory: {processed_data_dir}")
    logger.info(f"Visual Verification Intermediates: {intermediates_dir}")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Stage 1 & 2: Cardamom Leaf U2-Net Preprocessing")
    parser.add_argument("--raw-dir", type=str, default=str(cfg.FALLBACK_RAW_DIR), help="Path to raw dataset")
    parser.add_argument("--out-dir", type=str, default=str(cfg.PROCESSED_DATA_DIR), help="Path to preprocessed output")
    parser.add_argument("--imgsz", type=int, default=cfg.TARGET_IMG_SIZE, help="Target image size (default: 224)")
    parser.add_argument("--smart-bypass", action="store_true", default=True, help="Bypass U2-Net if background is already black")
    parser.add_argument("--force-unet", action="store_true", help="Force U2-Net on all images")
    parser.add_argument("--intermediates", type=int, default=5, help="Number of intermediate samples to save per class")
    parser.add_argument("--max-per-class", type=int, default=None, help="Optional image limit per class for fast testing")
    parser.add_argument("--device", type=str, default="auto", help="Hardware device (cpu/cuda/auto)")

    args = parser.parse_args()

    smart_bypass = False if args.force_unet else args.smart_bypass
    device = cfg.get_optimal_device(args.device)

    run_preprocessing(
        raw_data_dir=Path(args.raw_dir),
        processed_data_dir=Path(args.out_dir),
        target_size=args.imgsz,
        smart_bypass=smart_bypass,
        intermediates_count=args.intermediates,
        max_per_class=args.max_per_class,
        device=device
    )


if __name__ == "__main__":
    main()
