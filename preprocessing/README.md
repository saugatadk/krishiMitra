# 🔧 Preprocessing Directory

This directory contains:
1. **`app.py`**: Legacy lightweight Flask microservice (used for initial cloud/AWS preprocessing demonstrations).
2. **`preprocess.py`**, **`train_yolo.py`**, **`evaluate.py`**: Backward-compatible execution forwarders pointing to the canonical `ml_pipeline/` modules.

---

### 🚀 Production Deep Learning Pipeline
The full 4-stage Computer Vision pipeline for Cardamom Disease Detection (U2-Net segmentation + YOLOv8 classification) is located in [`../ml_pipeline/`](../ml_pipeline/):
- **Stage 1 & 2 (U2-Net Saliency & Smart Bypass Preprocessing)**: [`../ml_pipeline/src/preprocess.py`](../ml_pipeline/src/preprocess.py)
- **Stage 3 (YOLOv8 Classification Training)**: [`../ml_pipeline/src/train_yolo.py`](../ml_pipeline/src/train_yolo.py)
- **Stage 4 (Multi-Mode Evaluation Protocol)**: [`../ml_pipeline/src/evaluate.py`](../ml_pipeline/src/evaluate.py)
- **Master Pipeline CLI**: [`../ml_pipeline/run_pipeline.py`](../ml_pipeline/run_pipeline.py)
