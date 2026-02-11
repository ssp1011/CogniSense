"""
CogniSense — Training Pipeline.

End-to-end training orchestrator: generates synthetic data (or loads
real data), trains all model variants, evaluates, runs cross-validation,
and saves the best model.

Usage:
    python -m ml.training.train
    python -m ml.training.train --samples 1000
"""

import logging
import argparse
import json
from pathlib import Path
from datetime import datetime

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ml.models.random_forest import RandomForestModel
from ml.models.xgboost_clf import XGBoostModel
from ml.models.svm_clf import SVMModel
from ml.models.ensemble import EnsembleModel
from ml.training.evaluate import evaluate_model, print_evaluation
from ml.training.cross_val import compare_models
from ml.training.synthetic_labeler import SyntheticLabeler

logger = logging.getLogger(__name__)

# Paths
SAVED_MODELS_DIR = Path("ml/saved_models")
EXPERIMENTS_DIR = Path("ml/experiments")


def setup_logging() -> None:
    """Configure logging for the training script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def load_or_generate_data(
    n_samples: int = 500,
    data_path: str = None,
) -> tuple:
    """
    Load real data or generate synthetic training data.

    Args:
        n_samples: Number of synthetic samples if generating.
        data_path: Path to real data (npz format) if available.

    Returns:
        (X, y, feature_names) tuple.
    """
    if data_path and Path(data_path).exists():
        logger.info("Loading real data from %s", data_path)
        data = np.load(data_path, allow_pickle=True)
        return data["X"], data["y"], data["feature_names"].tolist()

    logger.info("Generating synthetic data (%d samples)...", n_samples)
    labeler = SyntheticLabeler()
    return labeler.generate_synthetic_dataset(n_samples=n_samples)


def run_training(n_samples: int = 500, data_path: str = None) -> dict:
    """
    Execute the full training pipeline.

    Steps:
      1. Load/generate data
      2. Train-test split (80/20)
      3. Scale features (StandardScaler)
      4. Train individual models + ensemble
      5. Evaluate on test set
      6. Cross-validate for comparison
      7. Save best model

    Args:
        n_samples: Synthetic sample count.
        data_path: Optional path to real data.

    Returns:
        Dict of results including evaluations and saved paths.
    """
    # ── 1. Data ─────────────────────────────────────────────────
    X, y, feature_names = load_or_generate_data(n_samples, data_path)
    logger.info("Dataset: %d samples, %d features, %d classes",
                X.shape[0], X.shape[1], len(np.unique(y)))

    # ── 2. Split ────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y,
    )
    logger.info("Split: train=%d, test=%d", len(X_train), len(X_test))

    # ── 3. Scale ────────────────────────────────────────────────
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ── 4. Train models ─────────────────────────────────────────
    models = {
        "RandomForest": RandomForestModel(),
        "XGBoost": XGBoostModel(),
        "SVM": SVMModel(),
        "Ensemble": EnsembleModel(),
    }

    evaluations = {}
    for name, model in models.items():
        logger.info("Training %s...", name)
        model.train(X_train_scaled, y_train, feature_names=feature_names)
        eval_result = evaluate_model(model, X_test_scaled, y_test)
        evaluations[name] = eval_result
        print(f"\n--- {name} ---")
        print_evaluation(eval_result)

    # ── 5. Cross-validation comparison ──────────────────────────
    cv_models = {
        "RandomForest": RandomForestModel(),
        "XGBoost": XGBoostModel(),
        "SVM": SVMModel(),
    }
    cv_results = compare_models(cv_models, X_train_scaled, y_train, k=5)

    # ── 6. Save best model ──────────────────────────────────────
    best_name = max(evaluations, key=lambda k: evaluations[k]["accuracy"])
    best_model = models[best_name]
    best_acc = evaluations[best_name]["accuracy"]

    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = str(SAVED_MODELS_DIR / "latest.pkl")
    best_model.save(model_path)

    # Also save scaler
    import joblib
    scaler_path = str(SAVED_MODELS_DIR / "scaler.pkl")
    joblib.dump(scaler, scaler_path)

    logger.info("Best model: %s (acc=%.3f) saved to %s", best_name, best_acc, model_path)

    # ── 7. Save experiment log ──────────────────────────────────
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_log = {
        "timestamp": timestamp,
        "n_samples": int(X.shape[0]),
        "n_features": int(X.shape[1]),
        "best_model": best_name,
        "best_accuracy": best_acc,
        "evaluations": {
            name: {
                "accuracy": res["accuracy"],
                "cohen_kappa": res["cohen_kappa"],
                "per_class": res["per_class"],
            }
            for name, res in evaluations.items()
        },
        "cv_results": {
            name: {
                "mean_accuracy": res["mean_accuracy"],
                "std_accuracy": res["std_accuracy"],
                "mean_f1_macro": res["mean_f1_macro"],
            }
            for name, res in cv_results.items()
        },
    }
    exp_path = EXPERIMENTS_DIR / f"exp_{timestamp}.json"
    with open(exp_path, "w") as f:
        json.dump(exp_log, f, indent=2)
    logger.info("Experiment log saved to %s", exp_path)

    return {
        "best_model": best_name,
        "best_accuracy": best_acc,
        "model_path": model_path,
        "scaler_path": scaler_path,
        "experiment_log": str(exp_path),
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="CogniSense Training Pipeline")
    parser.add_argument("--samples", type=int, default=500,
                        help="Number of synthetic samples")
    parser.add_argument("--data", type=str, default=None,
                        help="Path to real data (.npz)")
    args = parser.parse_args()

    setup_logging()
    results = run_training(n_samples=args.samples, data_path=args.data)

    print(f"\n{'='*50}")
    print(f"  Best Model:  {results['best_model']}")
    print(f"  Accuracy:    {results['best_accuracy']:.4f}")
    print(f"  Saved to:    {results['model_path']}")
    print(f"  Scaler:      {results['scaler_path']}")
    print(f"  Exp log:     {results['experiment_log']}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
