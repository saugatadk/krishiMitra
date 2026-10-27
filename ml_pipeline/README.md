# 🌿 Cardamom Leaf Disease Detection ML Pipeline

Production Computer Vision pipeline utilizing **U2-Net** for complex farm-field background removal and **YOLOv8** for high-accuracy disease classification across 3 classes:
1. `Colletotrichum_Blight` (अलैंची पात डढुवा)
2. `Phyllosticta_Leaf_Spot` (अलैंची पात थोप्ले रोग)
3. `Healthy` (स्वस्थ अलैंची पात)

---

## 📁 Architecture & Directory Structure

```text
ml_pipeline/
├── configs/
│   └── pipeline_config.py       # Centralized hyperparameters, classes, paths, pathology augmentations
├── data/
│   ├── raw/                     # Raw farm-field cardamom dataset (train, val, test)
│   └── processed/               # Standard Ultralytics classification dataset (224x224x3)

│       ├── train/
│       ├── val/
│       ├── test/
│       └── intermediates/       # Intermediate visual artifacts (original, mask, segmented, resized_224)
├── models/
│   ├── __init__.py
│   └── u2net.py                 # Native PyTorch U2-Net (RSU blocks) with leaf saliency extraction
├── runs/
│   └── cardamom_cls/            # Ultralytics training logs, confusion matrices, weights, and plots
├── src/
│   ├── __init__.py
│   ├── preprocess.py            # Stage 1 & 2: U2-Net segmentation, smart bypass, bitwise AND, 224x224 resize
│   ├── train_yolo.py            # Stage 3: YOLOv8 classification training (scratch/transfer, pathology aug)
│   ├── evaluate.py              # Stage 4: Multi-mode evaluation (Holdout, External, 5-Fold Stratified CV)
│   └── utils.py                 # Pure-NumPy StratifiedKFold, macro/per-class metrics, confusion matrices
├── requirements.txt             # ML pipeline dependencies
├── run_pipeline.py              # Master CLI runner orchestrating stages end-to-end
└── README.md
```

---

## ⚡ 4-Stage Pipeline Overview

### Stage 1 & 2: Saliency Segmentation & Preprocessing (`src/preprocess.py`)
- **U2-Net Leaf Extraction**: Passes farm-field RGB images through U2-Net, generating a probability saliency map thresholded at $0.5$ into a binary mask.
- **Smart Background Detection Bypass (`--smart-bypass`)**:
  - Blight leaf photos that already have an isolated black background bypass U2-Net to prevent lesion boundary erosion (dark necrosis misclassified as black background).
  - Images with complex agricultural backgrounds (soil, weeds, neighboring leaves) undergo full U2-Net segmentation.
- **Bitwise Masking (`cv2.bitwise_and`)**: Isolates the leaf canopy, setting background pixels strictly to `(0, 0, 0)`.
- **Standardized Resolution**: Resizes all leaves to $224 \times 224 \times 3$ with area interpolation and saves intermediate inspection samples to `data/processed/intermediates/`.

### Stage 3: YOLOv8 Classification Training (`src/train_yolo.py`)
- **Model Architectures**: Supports `yolov8n-cls`, `yolov8s-cls`, `yolov8m-cls`, `yolov8l-cls`.
- **Pretrained vs. Scratch**: Supports both transfer learning (`--pretrained`) and training from scratch (`--from-scratch`).
- **Pathology-Safe Augmentations**: Caps HSV hue jitter at `hsv_h=0.01` to preserve diagnostic lesion discoloration (preventing chlorotic yellow halos from turning blue or necrotic brown from turning green) while enabling full geometric rotation and reflection invariance.
- **Production Export**: Automatically copies best weights to `backend/api/ml_models/cardamom_classifier_best.pt` and exports to ONNX format.

### Stage 4: Multi-Mode Evaluation Protocol (`src/evaluate.py`)
- **Mode 1 (Holdout Test)**: Evaluates the model on the stratified holdout test split (`test/`).
- **Mode 2 (External Test)**: Evaluates generalization on an unseen external cardamom directory.
- **Mode 3 (5-Fold Stratified Cross-Validation)**: Runs automated 5-Fold Stratified CV for 100 epochs per fold, aggregating metrics (Accuracy, Precision, Recall, F1-Score) with Mean $\pm$ Std Dev and saving high-DPI confusion matrices.

---

## 🚀 Usage Guide

### 1. Run Complete End-to-End Pipeline
```bash
python ml_pipeline/run_pipeline.py --stage all --model yolov8n-cls --epochs 100 --batch 16
```

### 2. Stage 1 & 2: Run Preprocessing with Smart Bypass
```bash
python ml_pipeline/src/preprocess.py --smart-bypass --imgsz 224
```

### 3. Stage 3: Train YOLOv8 Classifier
```bash
# Transfer Learning (Pretrained on ImageNet)
python ml_pipeline/src/train_yolo.py --model yolov8n-cls --epochs 100 --batch 16

# Training from Scratch
python ml_pipeline/src/train_yolo.py --model yolov8n-cls --from-scratch --epochs 100 --batch 16
```

### 4. Stage 4: Evaluate Model
```bash
# Mode 1: Holdout Test Set Evaluation
python ml_pipeline/src/evaluate.py --mode holdout --weights backend/api/ml_models/cardamom_classifier_best.pt

# Mode 2: External Dataset Evaluation
python ml_pipeline/src/evaluate.py --mode external --weights backend/api/ml_models/cardamom_classifier_best.pt --external-dir /path/to/external_test

# Mode 3: 5-Fold Stratified Cross-Validation
python ml_pipeline/src/evaluate.py --mode kfold --splits 5 --epochs 100 --batch 16
```
