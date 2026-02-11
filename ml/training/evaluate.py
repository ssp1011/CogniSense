"""
CogniSense — Model Evaluation.

Comprehensive evaluation metrics for cognitive load classifiers:
accuracy, per-class precision/recall/F1, confusion matrix, and
classification report.

Usage:
    from ml.training.evaluate import evaluate_model
    results = evaluate_model(model, X_test, y_test)
    print(results["classification_report"])
"""

import logging
from typing import Dict, Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
    cohen_kappa_score,
)

logger = logging.getLogger(__name__)

LABEL_NAMES = ["low", "medium", "high"]


def evaluate_model(
    model, X_test: np.ndarray, y_test: np.ndarray
) -> Dict[str, Any]:
    """
    Evaluate a trained model on test data.

    Args:
        model: Any model with .predict() and .predict_proba() methods.
        X_test: 2-D test features.
        y_test: 1-D true labels.

    Returns:
        Dict with accuracy, per_class metrics, confusion_matrix,
        classification_report text, and cohen_kappa.
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    acc = accuracy_score(y_test, y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, labels=[0, 1, 2], zero_division=0,
    )
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2])
    report = classification_report(
        y_test, y_pred, target_names=LABEL_NAMES, zero_division=0,
    )
    kappa = cohen_kappa_score(y_test, y_pred)

    # Mean confidence of correct predictions
    correct_mask = y_pred == y_test
    if np.any(correct_mask):
        correct_probs = y_proba[correct_mask]
        correct_conf = float(np.mean(
            [correct_probs[i, y_pred[correct_mask][i]]
             for i in range(len(correct_probs))]
        ))
    else:
        correct_conf = 0.0

    results = {
        "accuracy": float(acc),
        "cohen_kappa": float(kappa),
        "mean_confidence_correct": correct_conf,
        "per_class": {
            name: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
            for i, name in enumerate(LABEL_NAMES)
        },
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
    }

    logger.info(
        "Evaluation — Acc: %.3f, Kappa: %.3f, F1(macro): %.3f",
        acc, kappa, float(np.mean(f1)),
    )
    return results


def print_evaluation(results: Dict[str, Any]) -> None:
    """Pretty-print evaluation results."""
    print(f"\n{'='*50}")
    print(f"  Accuracy:      {results['accuracy']:.4f}")
    print(f"  Cohen's Kappa: {results['cohen_kappa']:.4f}")
    print(f"  Mean Conf:     {results['mean_confidence_correct']:.4f}")
    print(f"{'='*50}")
    print(results["classification_report"])
    print("Confusion Matrix:")
    cm = np.array(results["confusion_matrix"])
    print(f"            {'  '.join(LABEL_NAMES)}")
    for i, name in enumerate(LABEL_NAMES):
        row = "  ".join(f"{v:5d}" for v in cm[i])
        print(f"  {name:>6s}  {row}")
    print()
