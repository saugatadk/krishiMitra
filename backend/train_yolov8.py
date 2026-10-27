#!/usr/bin/env python3
"""
Backward-compatible wrapper for YOLOv8 Object Detection training.
Canonical location: backend/scripts/train_yolov8_detector.py
"""
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

if __name__ == "__main__":
    from train_yolov8_detector import main
    main()
