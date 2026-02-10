"""
CogniSense — Feature Fusion Engine.

Merges features from all modalities into a single feature vector
for the cognitive load classifier.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


def fuse_features(
    visual: Dict[str, float],
    behavioral: Dict[str, float],
    audio: Dict[str, float],
) -> Dict[str, float]:
    """
    Merge per-modality feature dicts into a single fused vector.

    Prefixes each feature with its modality for traceability.

    Args:
        visual: Features from face landmarks.
        behavioral: Features from keystroke + mouse.
        audio: Features from voice analysis (may be empty).

    Returns:
        Combined dict of all features.
    """
    fused = {}
    for k, v in visual.items():
        fused[f"vis_{k}"] = v
    for k, v in behavioral.items():
        fused[f"beh_{k}"] = v
    for k, v in audio.items():
        fused[f"aud_{k}"] = v

    logger.debug("Fused %d features (%d vis, %d beh, %d aud)",
                 len(fused), len(visual), len(behavioral), len(audio))
    return fused
