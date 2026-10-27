"""
Evaluation Metrics & Visualization Utilities
- StratifiedKFold splitter (with sklearn and native NumPy fallback)
- Classification metrics: Accuracy, Precision, Recall, F1 (macro and per-class)
- Publication-quality Confusion Matrix heatmap plotting
- Training/Validation learning curves plotter
"""

import json
import logging
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

logger = logging.getLogger(__name__)

# Attempt importing scikit-learn; provide mathematically exact fallback if not present
try:
    from sklearn.model_selection import StratifiedKFold as SklearnKFold
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class NativeStratifiedKFold:
    """
    Exact pure-Python/NumPy implementation of Stratified K-Fold cross-validation.
    Ensures identical class representation across all K partitions.
    """
    def __init__(self, n_splits=5, shuffle=True, random_state=42):
        self.n_splits = n_splits
        self.shuffle = shuffle
        self.random_state = random_state

    def split(self, X, y):
        y = np.array(y)
        n_samples = len(y)
        unique_classes, y_inversed = np.unique(y, return_inverse=True)
        n_classes = len(unique_classes)

        rng = np.random.RandomState(self.random_state) if self.shuffle else None

        # Collect indices per class
        class_indices = [np.where(y_inversed == c)[0] for c in range(n_classes)]
        if self.shuffle:
            for idxs in class_indices:
                rng.shuffle(idxs)

        # Distribute into K folds
        folds = [[] for _ in range(self.n_splits)]
        for idxs in class_indices:
            splits = np.array_split(idxs, self.n_splits)
            for k in range(self.n_splits):
                folds[k].extend(splits[k])

        all_indices = np.arange(n_samples)
        for k in range(self.n_splits):
            val_idx = np.array(folds[k])
            train_idx = np.setdiff1d(all_indices, val_idx)
            yield train_idx, val_idx


def get_stratified_kfold(n_splits=5, shuffle=True, random_state=42):
    """Returns StratifiedKFold instance (sklearn if available, else native)."""
    if SKLEARN_AVAILABLE:
        return SklearnKFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)
    return NativeStratifiedKFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)


def compute_confusion_matrix(y_true, y_pred, num_classes=3):
    """Computes a num_classes x num_classes confusion matrix."""
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        if 0 <= t < num_classes and 0 <= p < num_classes:
            cm[t, p] += 1
    return cm


def compute_metrics(y_true, y_pred, class_names):
    """
    Computes overall Accuracy, macro Precision, Recall, F1,
    and class-wise breakdown.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    num_classes = len(class_names)

    cm = compute_confusion_matrix(y_true, y_pred, num_classes=num_classes)
    total_samples = len(y_true)
    correct_samples = np.trace(cm)
    accuracy = float(correct_samples / max(1, total_samples))

    class_metrics = {}
    precisions = []
    recalls = []
    f1s = []

    for i, cls_name in enumerate(class_names):
        tp = cm[i, i]
        fp = np.sum(cm[:, i]) - tp
        fn = np.sum(cm[i, :]) - tp
        support = int(np.sum(cm[i, :]))

        prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

        class_metrics[cls_name] = {
            "precision": round(prec * 100, 2),
            "recall": round(rec * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "support": support
        }

    macro_prec = float(np.mean(precisions))
    macro_rec = float(np.mean(recalls))
    macro_f1 = float(np.mean(f1s))

    return {
        "accuracy": round(accuracy * 100, 2),
        "macro_precision": round(macro_prec * 100, 2),
        "macro_recall": round(macro_rec * 100, 2),
        "macro_f1": round(macro_f1 * 100, 2),
        "total_samples": int(total_samples),
        "per_class": class_metrics,
        "confusion_matrix": cm.tolist()
    }


def plot_confusion_matrix(cm, class_names, output_path: Path, title: str = "Confusion Matrix", normalize: bool = True):
    """
    Renders a high-resolution confusion matrix heatmap using Matplotlib.
    """
    cm = np.array(cm)
    if normalize:
        row_sums = cm.sum(axis=1)[:, np.newaxis]
        cm_norm = np.divide(cm.astype('float'), row_sums, out=np.zeros_like(cm, dtype=float), where=row_sums > 0)
    else:
        cm_norm = cm


    plt.figure(figsize=(7.8, 6.2), dpi=300)
    plt.imshow(cm_norm, interpolation='nearest', cmap=plt.cm.Greens)
    plt.title(title, fontsize=12, fontweight='bold', pad=18)
    plt.colorbar(fraction=0.046, pad=0.04)


    tick_marks = np.arange(len(class_names))
    # Abbreviate long names for clear axis layout
    clean_labels = [c.replace("_", " ") for c in class_names]
    plt.xticks(tick_marks, clean_labels, rotation=25, ha='right', fontsize=10)
    plt.yticks(tick_marks, clean_labels, fontsize=10)

    thresh = cm_norm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            pct = cm_norm[i, j] * 100 if normalize else 0
            text_str = f"{val}\n({pct:.1f}%)" if normalize else f"{val}"
            plt.text(
                j, i, text_str,
                horizontalalignment="center",
                verticalalignment="center",
                color="white" if cm_norm[i, j] > thresh else "black",
                fontsize=10,
                fontweight='bold'
            )

    plt.ylabel('Ground Truth (Actual)', fontsize=12, fontweight='bold')
    plt.xlabel('YOLOv8 Prediction', fontsize=12, fontweight='bold')
    plt.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), bbox_inches='tight')
    plt.close()
    logger.info(f"Saved confusion matrix plot: {output_path}")


def plot_learning_curves(train_losses, val_losses, val_accuracies, output_path: Path):
    """Plots training/validation loss and accuracy curves."""
    epochs = range(1, len(train_losses) + 1)

    fig, ax1 = plt.subplots(figsize=(8, 5), dpi=300)

    # Loss curve
    ax1.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Loss', color='#d32f2f', fontsize=12, fontweight='bold')
    l1 = ax1.plot(epochs, train_losses, color='#e53935', linestyle='-', label='Train Loss')
    l2 = ax1.plot(epochs, val_losses, color='#ef5350', linestyle='--', label='Val Loss')
    ax1.tick_params(axis='y', labelcolor='#d32f2f')

    # Top-1 Accuracy curve
    ax2 = ax1.twinx()
    ax2.set_ylabel('Validation Top-1 Accuracy (%)', color='#2e7d32', fontsize=12, fontweight='bold')
    l3 = ax2.plot(epochs, val_accuracies, color='#2e7d32', linestyle='-', linewidth=2, label='Val Top-1 Acc')
    ax2.tick_params(axis='y', labelcolor='#2e7d32')

    lines = l1 + l2 + l3
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center right')

    plt.title('Cardamom YOLOv8 Classification Learning Curves', fontsize=13, fontweight='bold', pad=12)
    plt.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), bbox_inches='tight')
    plt.close()
    logger.info(f"Saved learning curves plot: {output_path}")
