#!/usr/bin/env python3
"""
KrishiMitra YOLOv8 Cardamom Disease Detection Training Pipeline
Trains a YOLOv8 Nano model to detect cardamom leaf lesions, viral streaks, and rot.
Supports dataset generation, training, validation, and export to ONNX and TFLite.
"""

import os
import sys
import argparse
import random
from pathlib import Path
from PIL import Image, ImageDraw


# Cardamom Disease Classes
CLASSES = [
    'Cardamom_Leaf_Blight',      # Class 0: Colletotrichum gloeosporioides (अलैंची पात डढुवा)
    'Chhirke_Streak_Virus',      # Class 1: Cardamom mosaic streak virus (छिरके भाइरस)
    'Foorkey_Bushy_Stunt',       # Class 2: Cardamom bushy dwarf stunt (फुर्के भाइरस)
    'Rhizome_Rot',               # Class 3: Pythium clump & rhizome rot (गाना तथा जरा कुहिने)
    'Healthy_Leaf'               # Class 4: Normal cardamom foliage (स्वस्थ पात)
]


def create_cardamom_yaml(dataset_dir: Path) -> Path:
    """Generates the data.yaml file required by YOLOv8."""
    yaml_content = f"""# Cardamom Leaf Disease Detection Dataset Configuration
path: {dataset_dir.resolve()}
train: images/train
val: images/val

names:
  0: Cardamom_Leaf_Blight
  1: Chhirke_Streak_Virus
  2: Foorkey_Bushy_Stunt
  3: Rhizome_Rot
  4: Healthy_Leaf
"""
    yaml_path = dataset_dir / "cardamom_data.yaml"
    yaml_path.write_text(yaml_content)
    print(f"Generated dataset YAML: {yaml_path}")
    return yaml_path


def generate_synthetic_training_data(dataset_dir: Path, num_train: int = 40, num_val: int = 10):
    """
    Generates a starter dataset with simulated cardamom leaves and realistic bounding boxes.
    Allows testing the entire training and export pipeline immediately without manual annotation.
    """
    for split, count in [('train', num_train), ('val', num_val)]:
        img_dir = dataset_dir / "images" / split
        lbl_dir = dataset_dir / "labels" / split
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)

        for i in range(count):
            # Base cardamom leaf green canvas
            img_size = 640
            bg_green = (random.randint(35, 65), random.randint(110, 160), random.randint(35, 60))
            img = Image.new('RGB', (img_size, img_size), bg_green)
            draw = ImageDraw.Draw(img)

            # Draw leaf veins
            for v in range(50, 600, 40):
                draw.line([(50, v), (590, v + random.randint(-15, 15))], fill=(30, 90, 30), width=2)

            labels = []
            disease_class = random.choices([0, 1, 2, 3, 4], weights=[0.4, 0.2, 0.15, 0.15, 0.1])[0]

            if disease_class != 4:  # If not purely healthy
                num_lesions = random.randint(1, 4)
                for _ in range(num_lesions):
                    # Random lesion bounding box
                    box_w = random.randint(60, 150)
                    box_h = random.randint(50, 130)
                    x_center = random.randint(box_w, img_size - box_w)
                    y_center = random.randint(box_h, img_size - box_h)

                    # Lesion color based on disease
                    if disease_class == 0:  # Blight (Brown / Necrotic yellow halo)
                        color = (random.randint(130, 180), random.randint(80, 110), 30)
                    elif disease_class == 1:  # Chhirke (Yellowish chlorotic streak)
                        color = (random.randint(200, 230), random.randint(180, 210), 50)
                    elif disease_class == 2:  # Foorkey (Dwarf clustered nodes)
                        color = (random.randint(70, 90), random.randint(80, 100), 40)
                    else:  # Rhizome Rot (Dark rotting clump)
                        color = (random.randint(40, 70), random.randint(30, 50), 25)

                    draw.ellipse(
                        [x_center - box_w // 2, y_center - box_h // 2, x_center + box_w // 2, y_center + box_h // 2],
                        fill=color
                    )

                    # Normalized YOLO coordinates (class x_center y_center width height)
                    labels.append(f"{disease_class} {x_center / img_size:.6f} {y_center / img_size:.6f} {box_w / img_size:.6f} {box_h / img_size:.6f}")

            # Save image and label
            img_path = img_dir / f"leaf_{split}_{i:03d}.jpg"
            lbl_path = lbl_dir / f"leaf_{split}_{i:03d}.txt"

            img.save(img_path, quality=85)
            lbl_path.write_text("\n".join(labels))

    print(f"Generated {num_train} training and {num_val} validation cardamom images.")


def train_yolo(data_yaml: Path, epochs: int = 5, imgsz: int = 640, output_dir: Path = None):
    """Executes YOLOv8 training using Ultralytics."""
    from ultralytics import YOLO
    import shutil

    print(f"Loading pretrained YOLOv8n weights...")
    model = YOLO('yolov8n.pt')

    print(f"Starting Cardamom Disease Detection training on CPU for {epochs} epochs...")
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=4,
        device='cpu',
        name="cardamom_detector",
        project=str(output_dir or Path("runs/detect")),
        augment=True,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=15.0,
        flipud=0.5,
        fliplr=0.5,
        verbose=True
    )

    # Save trained weights to api/ml_models
    backend_root = Path(__file__).resolve().parent.parent
    ml_models_dir = backend_root / "api" / "ml_models"
    ml_models_dir.mkdir(parents=True, exist_ok=True)
    best_weights = Path(results.save_dir) / "weights" / "best.pt"
    target_weights = ml_models_dir / "cardamom_yolov8n.pt"

    if best_weights.exists():
        shutil.copy(best_weights, target_weights)
        print(f"✅ Successfully copied trained weights to {target_weights}")

    print("Training complete! Exporting to ONNX format...")
    onnx_path = model.export(format="onnx", imgsz=imgsz, dynamic=False)
    print(f"Model exported to ONNX: {onnx_path}")
    return model, onnx_path


def main():
    parser = argparse.ArgumentParser(description="KrishiMitra YOLOv8 Cardamom Training Pipeline")
    parser.add_argument("--dataset-dir", type=str, default="cardamom_dataset", help="Path to dataset root")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size for training")
    parser.add_argument("--generate-demo", action="store_true", help="Generate starter training dataset")
    args = parser.parse_args()

    dataset_path = Path(args.dataset_dir)
    if args.generate_demo or not (dataset_path / "images").exists():
        print("Dataset directory not found or demo requested. Creating starter cardamom dataset...")
        generate_synthetic_training_data(dataset_path)

    yaml_path = create_cardamom_yaml(dataset_path)
    train_yolo(yaml_path, epochs=args.epochs, imgsz=args.imgsz)


if __name__ == "__main__":
    main()
