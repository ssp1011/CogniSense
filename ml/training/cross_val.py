"""
CogniSense — Cross-Validation.

Stratified K-Fold cross-validation for model comparison and
hyperparameter selection.

Usage:
    from ml.training.cross_val import cross_validate_model
    results = cross_validate_model(model, X, y, k=5)
"""

import logging
from typing import Dict, Any

import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score

logger = logging.getLogger(__name__)


def cross_validate_model(
    model, X: np.ndarray, y: np.ndarray,
    k: int = 5, random_state: int = 42,
) -> Dict[str, Any]:
    """
    Perform stratified K-fold cross-validation.

    Args:
        model: Model with train() and predict() methods.
        X: 2-D feature matrix.
        y: 1-D labels.
        k: Number of folds.
        random_state: Random seed for reproducibility.

    Returns:
        Dict with fold-wise and aggregate metrics.
    """
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=random_state)

    fold_metrics = []

    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        # Train a fresh model instance
        model.train(X_train, y_train)
        y_pred = model.predict(X_val)

        acc = accuracy_score(y_val, y_pred)
        f1_macro = f1_score(y_val, y_pred, average="macro", zero_division=0)
        f1_weighted = f1_score(y_val, y_pred, average="weighted", zero_division=0)

        fold_metrics.append({
            "fold": fold_idx + 1,
            "accuracy": float(acc),
            "f1_macro": float(f1_macro),
            "f1_weighted": float(f1_weighted),
            "train_size": len(train_idx),
            "val_size": len(val_idx),
        })

        logger.info(
            "Fold %d/%d — Acc: %.3f, F1(macro): %.3f",
            fold_idx + 1, k, acc, f1_macro,
        )

    # Aggregate
    accs = [m["accuracy"] for m in fold_metrics]
    f1s = [m["f1_macro"] for m in fold_metrics]

    results = {
        "k": k,
        "folds": fold_metrics,
        "mean_accuracy": float(np.mean(accs)),
        "std_accuracy": float(np.std(accs)),
        "mean_f1_macro": float(np.mean(f1s)),
        "std_f1_macro": float(np.std(f1s)),
    }

    logger.info(
        "CV Summary — Acc: %.3f ± %.3f, F1: %.3f ± %.3f",
        results["mean_accuracy"], results["std_accuracy"],
        results["mean_f1_macro"], results["std_f1_macro"],
    )
    return results


def compare_models(
    models: Dict[str, Any], X: np.ndarray, y: np.ndarray,
    k: int = 5,
) -> Dict[str, Dict[str, Any]]:
    """
    Compare multiple models via cross-validation.

    Args:
        models: Dict of model_name → model instance.
        X: Feature matrix.
        y: Labels.
        k: Number of folds.

    Returns:
        Dict of model_name → CV results, sorted by mean accuracy.
    """
    results = {}
    for name, model in models.items():
        logger.info("Cross-validating %s...", name)
        results[name] = cross_validate_model(model, X, y, k=k)

    # Print comparison
    print(f"\n{'Model':<20s} {'Acc':>10s} {'F1(macro)':>12s}")
    print("-" * 44)
    for name, res in sorted(
        results.items(), key=lambda x: x[1]["mean_accuracy"], reverse=True
    ):
        print(
            f"{name:<20s} {res['mean_accuracy']:.3f}±{res['std_accuracy']:.3f}"
            f"  {res['mean_f1_macro']:.3f}±{res['std_f1_macro']:.3f}"
        )

    return results
