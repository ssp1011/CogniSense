"""
CogniSense — Audio Feature Extraction.

Extracts voice-stress-indicative features from audio chunks using
Librosa. Computes pitch (F0), jitter, shimmer, MFCCs, spectral
features, energy, and speaking rate.

Usage:
    from capture.audio_capture import AudioChunk
    chunk: AudioChunk = ...
    features = extract_audio_features(chunk)
    # Or from a window of chunks:
    features = extract_audio_features_window(chunks)
"""

import logging
from typing import Dict, List, Optional

import numpy as np
import librosa

from capture.audio_capture import AudioChunk

logger = logging.getLogger(__name__)

# Number of MFCCs to extract
N_MFCC = 13


def _extract_pitch(y: np.ndarray, sr: int) -> tuple:
    """
    Extract fundamental frequency (F0) using librosa's pyin.

    Returns:
        (pitch_mean, pitch_std) in Hz. NaN values are filtered.
    """
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y, fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"), sr=sr,
    )
    f0_valid = f0[~np.isnan(f0)]
    if len(f0_valid) == 0:
        return 0.0, 0.0
    return float(np.mean(f0_valid)), float(np.std(f0_valid))


def _extract_jitter(y: np.ndarray, sr: int) -> float:
    """
    Compute jitter (cycle-to-cycle pitch variation).

    Jitter = mean(|T_i - T_{i+1}|) / mean(T_i)
    where T_i are pitch period durations.
    """
    f0, _, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"), sr=sr,
    )
    f0_valid = f0[~np.isnan(f0)]
    if len(f0_valid) < 2:
        return 0.0
    periods = 1.0 / f0_valid
    period_diffs = np.abs(np.diff(periods))
    return float(np.mean(period_diffs) / np.mean(periods))


def _extract_shimmer(y: np.ndarray, sr: int) -> float:
    """
    Compute shimmer (cycle-to-cycle amplitude variation).

    Uses short-time energy of overlapping frames as amplitude proxy.
    Shimmer = mean(|A_i - A_{i+1}|) / mean(A_i)
    """
    frame_length = int(sr * 0.025)  # 25ms frames
    hop_length = int(sr * 0.010)    # 10ms hop
    rms = librosa.feature.rms(
        y=y, frame_length=frame_length, hop_length=hop_length
    )[0]
    if len(rms) < 2:
        return 0.0
    amp_diffs = np.abs(np.diff(rms))
    mean_rms = np.mean(rms)
    if mean_rms == 0:
        return 0.0
    return float(np.mean(amp_diffs) / mean_rms)


def _extract_speaking_rate(y: np.ndarray, sr: int) -> float:
    """
    Estimate speaking rate as syllable-like onsets per second.

    Uses librosa onset detection as a proxy for syllable boundaries.
    """
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onsets = librosa.onset.onset_detect(
        onset_envelope=onset_env, sr=sr, units="time"
    )
    duration = len(y) / sr
    if duration == 0:
        return 0.0
    return float(len(onsets) / duration)


def extract_audio_features(chunk: AudioChunk) -> Dict[str, float]:
    """
    Extract 15 audio features from a single AudioChunk.

    Features:
        - pitch_mean, pitch_std: Fundamental frequency stats (Hz)
        - jitter: Cycle-to-cycle pitch variation
        - shimmer: Cycle-to-cycle amplitude variation
        - mfcc_1..mfcc_13 means: Mel-frequency cepstral coefficients
        - spectral_centroid: Center of mass of spectrum (Hz)
        - spectral_rolloff: Frequency below which 85% of energy lies
        - rms_energy: Root mean square energy
        - zcr: Zero crossing rate
        - speaking_rate: Estimated syllables per second

    Args:
        chunk: AudioChunk from AudioCapture.

    Returns:
        Dict of feature_name → value.
    """
    y = chunk.samples.astype(np.float32)
    sr = chunk.sample_rate

    # Bail out on silence
    if np.max(np.abs(y)) < 1e-6:
        logger.debug("Silent chunk, returning zeros")
        return _zero_audio_features()

    features: Dict[str, float] = {}

    # ── Pitch (F0) ──────────────────────────────────────────────
    pitch_mean, pitch_std = _extract_pitch(y, sr)
    features["pitch_mean"] = pitch_mean
    features["pitch_std"] = pitch_std

    # ── Jitter & Shimmer ────────────────────────────────────────
    features["jitter"] = _extract_jitter(y, sr)
    features["shimmer"] = _extract_shimmer(y, sr)

    # ── MFCCs ───────────────────────────────────────────────────
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)
    for i in range(N_MFCC):
        features[f"mfcc_{i+1}_mean"] = float(np.mean(mfccs[i]))

    # ── Spectral features ───────────────────────────────────────
    spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    features["spectral_centroid"] = float(np.mean(spec_centroid))

    spec_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)[0]
    features["spectral_rolloff"] = float(np.mean(spec_rolloff))

    # ── Energy ──────────────────────────────────────────────────
    rms = librosa.feature.rms(y=y)[0]
    features["rms_energy"] = float(np.mean(rms))

    # ── Zero crossing rate ──────────────────────────────────────
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    features["zcr"] = float(np.mean(zcr))

    # ── Speaking rate ───────────────────────────────────────────
    features["speaking_rate"] = _extract_speaking_rate(y, sr)

    logger.debug("Extracted %d audio features", len(features))
    return features


def extract_audio_features_window(
    chunks: List[AudioChunk],
) -> Dict[str, float]:
    """
    Extract averaged audio features over a window of AudioChunks.

    Concatenates all chunk samples and runs extraction once for
    better spectral resolution.

    Args:
        chunks: List of AudioChunk objects for a time window.

    Returns:
        Dict of feature_name → value. Zeros if no chunks.
    """
    if not chunks:
        return _zero_audio_features()

    sr = chunks[0].sample_rate
    all_samples = np.concatenate([c.samples for c in chunks])

    combined_chunk = AudioChunk(
        timestamp=chunks[0].timestamp,
        samples=all_samples,
        sample_rate=sr,
        duration_sec=len(all_samples) / sr,
    )
    return extract_audio_features(combined_chunk)


def _zero_audio_features() -> Dict[str, float]:
    """Return zero-valued audio features."""
    keys = [
        "pitch_mean", "pitch_std", "jitter", "shimmer",
    ]
    keys += [f"mfcc_{i+1}_mean" for i in range(N_MFCC)]
    keys += [
        "spectral_centroid", "spectral_rolloff",
        "rms_energy", "zcr", "speaking_rate",
    ]
    return {k: 0.0 for k in keys}
