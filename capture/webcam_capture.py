"""
CogniSense — Webcam Capture Module.

Captures video frames using OpenCV and extracts 468 face landmarks
via MediaPipe Face Mesh. Computes Eye Aspect Ratio (EAR), blink
detection, and head pose estimation per frame.

Usage:
    cam = WebcamCapture(camera_index=0, fps=15)
    cam.start()
    data = cam.read_frame()  # Returns LandmarkFrame or None
    cam.stop()
"""

import time
import logging
import threading
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

import cv2
import numpy as np
import mediapipe as mp

logger = logging.getLogger(__name__)

# ── MediaPipe landmark indices ───────────────────────────────────────
# Eyes (for EAR calculation)
LEFT_EYE_IDX = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]

# Nose tip + chin + left/right eye corner + left/right ear (for head pose)
POSE_LANDMARKS = [1, 152, 33, 263, 61, 291]


@dataclass
class LandmarkFrame:
    """Single frame of extracted face data."""
    timestamp: float
    landmarks: np.ndarray            # (468, 3) array
    left_ear: float                  # Left Eye Aspect Ratio
    right_ear: float                 # Right Eye Aspect Ratio
    avg_ear: float                   # Average EAR
    blink_detected: bool             # True if EAR below threshold
    head_pose: dict                  # pitch, yaw, roll in degrees
    face_detected: bool = True


def _compute_ear(landmarks: np.ndarray, eye_indices: List[int]) -> float:
    """
    Compute Eye Aspect Ratio for one eye.

    EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)

    Args:
        landmarks: (468, 3) array of face mesh points.
        eye_indices: 6 landmark indices defining the eye contour.

    Returns:
        EAR value (float). Higher = more open, lower = more closed.
    """
    pts = landmarks[eye_indices]
    vertical_1 = np.linalg.norm(pts[1] - pts[5])
    vertical_2 = np.linalg.norm(pts[2] - pts[4])
    horizontal = np.linalg.norm(pts[0] - pts[3])
    if horizontal == 0:
        return 0.0
    return (vertical_1 + vertical_2) / (2.0 * horizontal)


def _estimate_head_pose(
    landmarks: np.ndarray, frame_w: int, frame_h: int
) -> dict:
    """
    Estimate head pose (pitch, yaw, roll) using solvePnP.

    Args:
        landmarks: (468, 3) normalized face mesh landmarks.
        frame_w: Frame width in pixels.
        frame_h: Frame height in pixels.

    Returns:
        Dict with pitch, yaw, roll in degrees.
    """
    # 3D model points (generic face model)
    model_points = np.array([
        [0.0, 0.0, 0.0],             # Nose tip
        [0.0, -330.0, -65.0],        # Chin
        [-225.0, 170.0, -135.0],     # Left eye corner
        [225.0, 170.0, -135.0],      # Right eye corner
        [-150.0, -150.0, -125.0],    # Left mouth corner
        [150.0, -150.0, -125.0],     # Right mouth corner
    ], dtype=np.float64)

    # 2D image points from landmarks
    image_points = np.array([
        [landmarks[idx][0] * frame_w, landmarks[idx][1] * frame_h]
        for idx in POSE_LANDMARKS
    ], dtype=np.float64)

    # Camera matrix (approximate)
    focal_length = frame_w
    center = (frame_w / 2, frame_h / 2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1],
    ], dtype=np.float64)
    dist_coeffs = np.zeros((4, 1))

    success, rotation_vec, translation_vec = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )

    if not success:
        return {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}

    rotation_mat, _ = cv2.Rodrigues(rotation_vec)
    pose_mat = cv2.hconcat([rotation_mat, translation_vec])
    _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(
        cv2.hconcat([pose_mat, np.array([[0, 0, 0, 1]], dtype=np.float64).T])
    )

    # decomposeProjectionMatrix returns angles differently, use simple approach
    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_mat)

    return {
        "pitch": float(angles[0]),
        "yaw": float(angles[1]),
        "roll": float(angles[2]),
    }


class WebcamCapture:
    """
    Manages webcam video stream and MediaPipe Face Mesh processing.

    Attributes:
        camera_index: Index of the video capture device.
        fps: Target frames per second.
        ear_threshold: EAR value below which a blink is detected.
    """

    EAR_BLINK_THRESHOLD = 0.21

    def __init__(self, camera_index: int = 0, fps: int = 15):
        self.camera_index = camera_index
        self.fps = fps
        self._cap: Optional[cv2.VideoCapture] = None
        self._face_mesh = None
        self._running = False
        self._lock = threading.Lock()
        logger.info(
            "WebcamCapture initialized (camera=%d, fps=%d)",
            camera_index, fps,
        )

    def start(self) -> None:
        """Open camera and initialize MediaPipe Face Mesh."""
        self._cap = cv2.VideoCapture(self.camera_index)
        if not self._cap.isOpened():
            raise RuntimeError(
                f"Cannot open camera at index {self.camera_index}"
            )
        self._cap.set(cv2.CAP_PROP_FPS, self.fps)

        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._running = True
        logger.info("Webcam capture started")

    def read_frame(self) -> Optional[LandmarkFrame]:
        """
        Read a single frame, run face mesh, and return extracted data.

        Returns:
            LandmarkFrame with landmarks, EAR, blink, head pose.
            None if no frame available or face not detected.
        """
        if not self._running or self._cap is None:
            return None

        with self._lock:
            ret, frame = self._cap.read()

        if not ret or frame is None:
            return None

        frame_h, frame_w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return LandmarkFrame(
                timestamp=time.time(),
                landmarks=np.zeros((468, 3)),
                left_ear=0.0, right_ear=0.0, avg_ear=0.0,
                blink_detected=False,
                head_pose={"pitch": 0.0, "yaw": 0.0, "roll": 0.0},
                face_detected=False,
            )

        face = results.multi_face_landmarks[0]
        landmarks = np.array(
            [[lm.x, lm.y, lm.z] for lm in face.landmark],
            dtype=np.float64,
        )

        # Eye Aspect Ratio
        left_ear = _compute_ear(landmarks, LEFT_EYE_IDX)
        right_ear = _compute_ear(landmarks, RIGHT_EYE_IDX)
        avg_ear = (left_ear + right_ear) / 2.0
        blink = avg_ear < self.EAR_BLINK_THRESHOLD

        # Head pose
        head_pose = _estimate_head_pose(landmarks, frame_w, frame_h)

        return LandmarkFrame(
            timestamp=time.time(),
            landmarks=landmarks,
            left_ear=left_ear,
            right_ear=right_ear,
            avg_ear=avg_ear,
            blink_detected=blink,
            head_pose=head_pose,
        )

    def stop(self) -> None:
        """Release camera and cleanup MediaPipe resources."""
        self._running = False
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        if self._face_mesh is not None:
            self._face_mesh.close()
            self._face_mesh = None
        logger.info("Webcam capture stopped")

    @property
    def is_running(self) -> bool:
        """Return whether the capture is active."""
        return self._running
