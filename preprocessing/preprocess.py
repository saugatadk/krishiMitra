#!/usr/bin/env python3
"""
Wrapper for Stage 1 & 2: Background Removal & Preprocessing
Delegates to ml_pipeline.src.preprocess
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml_pipeline.src.preprocess import main

if __name__ == "__main__":
    main()
