"""
Face Detection Service using Google MediaPipe.

This module provides high-performance face detection optimized for mobile devices.
MediaPipe is chosen for its industry-standard mobile performance and accuracy.
"""

import logging
import numpy as np
import cv2
from typing import Optional, Tuple, List
import mediapipe as mp
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DetectedFace:
    """Data class for a detected face."""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    landmarks: List[Tuple[float, float]]  # List of (x, y) landmark points
    confidence: float
    aligned_face: Optional[np.ndarray] = None


class FaceDetectionService:
    """
    Face detection service using MediaPipe Face Detection.

    Uses MediaPipe's short-range model optimized for faces within 2 meters,
    which is ideal for selfie-based attendance systems.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.7,
        model_selection: int = 0  # 0 for short-range (within 2m), 1 for full-range
    ):
        """
        Initialize the face detection service.

        Args:
            min_detection_confidence: Minimum confidence threshold for face detection
            model_selection: 0 for short-range model, 1 for full-range model
        """
        self.min_detection_confidence = min_detection_confidence
        self.model_selection = model_selection

        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh

        # Create face detector
        self.face_detection = self.mp_face_detection.FaceDetection(
            min_detection_confidence=min_detection_confidence,
            model_selection=model_selection
        )

        # Create face mesh for detailed landmarks (used for alignment)
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence
        )

        # Standard alignment points (eye positions for 112x112 ArcFace input)
        self.ARCFACE_DST = np.array([
            [38.2946, 51.6963],
            [73.5318, 51.5014],
            [56.0252, 71.7366],
            [41.5493, 92.3655],
            [70.7299, 92.2041]
        ], dtype=np.float32)

        logger.info(f"Face Detection Service initialized with confidence={min_detection_confidence}")

    def detect_faces(self, image: np.ndarray) -> List[DetectedFace]:
        """
        Detect faces in an image.

        Args:
            image: BGR image as numpy array

        Returns:
            List of DetectedFace objects
        """
        if image is None:
            logger.error("Received None image")
            return []

        # Convert to RGB for MediaPipe
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = image.shape[:2]

        # Detect faces
        results = self.face_detection.process(rgb_image)

        detected_faces = []
        if results.detections:
            for detection in results.detections:
                # Get bounding box
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * width)
                y = int(bbox.ymin * height)
                w = int(bbox.width * width)
                h = int(bbox.height * height)

                # Ensure bbox is within image bounds
                x = max(0, x)
                y = max(0, y)
                w = min(w, width - x)
                h = min(h, height - y)

                # Get confidence score
                confidence = detection.score[0] if detection.score else 0.0

                # Get key points (6 points from MediaPipe)
                landmarks = []
                if detection.location_data.relative_keypoints:
                    for keypoint in detection.location_data.relative_keypoints:
                        landmarks.append((
                            keypoint.x * width,
                            keypoint.y * height
                        ))

                detected_faces.append(DetectedFace(
                    bbox=(x, y, w, h),
                    landmarks=landmarks,
                    confidence=confidence
                ))

        logger.info(f"Detected {len(detected_faces)} faces in image")
        return detected_faces

    def get_face_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Get detailed face landmarks using Face Mesh.

        Args:
            image: BGR image as numpy array

        Returns:
            5 key landmarks (left eye, right eye, nose, left mouth, right mouth)
            or None if no face detected
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = image.shape[:2]

        results = self.face_mesh.process(rgb_image)

        if not results.multi_face_landmarks:
            return None

        face_landmarks = results.multi_face_landmarks[0]

        # Extract 5 key points for face alignment
        # MediaPipe Face Mesh indices:
        # Left eye center: 33, Right eye center: 263
        # Nose tip: 1
        # Left mouth corner: 61, Right mouth corner: 291
        key_indices = [33, 263, 1, 61, 291]

        landmarks = np.zeros((5, 2), dtype=np.float32)
        for i, idx in enumerate(key_indices):
            landmark = face_landmarks.landmark[idx]
            landmarks[i] = [landmark.x * width, landmark.y * height]

        return landmarks

    def align_face(
        self,
        image: np.ndarray,
        landmarks: np.ndarray,
        output_size: Tuple[int, int] = (112, 112)
    ) -> np.ndarray:
        """
        Align face using 5-point landmarks for ArcFace input.

        Args:
            image: BGR image as numpy array
            landmarks: 5 key landmarks (left eye, right eye, nose, left mouth, right mouth)
            output_size: Output image size (default 112x112 for ArcFace)

        Returns:
            Aligned face image
        """
        # Scale destination points to output size
        dst = self.ARCFACE_DST * (output_size[0] / 112.0)

        # Calculate similarity transform
        tform = cv2.estimateAffinePartial2D(landmarks, dst)[0]

        # Apply transformation
        aligned = cv2.warpAffine(
            image,
            tform,
            output_size,
            borderMode=cv2.BORDER_REPLICATE
        )

        return aligned

    def extract_and_align_face(
        self,
        image: np.ndarray,
        padding: float = 0.25
    ) -> Optional[Tuple[np.ndarray, DetectedFace]]:
        """
        Detect, extract, and align a face from an image.

        Args:
            image: BGR image as numpy array
            padding: Padding ratio around the face bbox

        Returns:
            Tuple of (aligned face image, DetectedFace) or None if no face
        """
        # Detect faces
        faces = self.detect_faces(image)
        if not faces:
            logger.warning("No faces detected in image")
            return None

        if len(faces) > 1:
            logger.warning(f"Multiple faces detected ({len(faces)}), using largest")
            # Select the largest face
            faces = sorted(faces, key=lambda f: f.bbox[2] * f.bbox[3], reverse=True)

        face = faces[0]

        # Get detailed landmarks for alignment
        landmarks = self.get_face_landmarks(image)
        if landmarks is None:
            logger.warning("Could not get face landmarks, using basic crop")
            # Fall back to basic crop
            x, y, w, h = face.bbox
            pad_w = int(w * padding)
            pad_h = int(h * padding)
            x1 = max(0, x - pad_w)
            y1 = max(0, y - pad_h)
            x2 = min(image.shape[1], x + w + pad_w)
            y2 = min(image.shape[0], y + h + pad_h)
            face_crop = image[y1:y2, x1:x2]
            face.aligned_face = cv2.resize(face_crop, (112, 112))
            return face.aligned_face, face

        # Align face for ArcFace
        aligned_face = self.align_face(image, landmarks)
        face.aligned_face = aligned_face

        return aligned_face, face

    def calculate_face_quality(self, image: np.ndarray, face: DetectedFace) -> float:
        """
        Calculate a quality score for the detected face.

        Factors considered:
        - Face size relative to image
        - Detection confidence
        - Face position (centered is better)
        - Blur detection

        Args:
            image: Original image
            face: Detected face object

        Returns:
            Quality score between 0 and 1
        """
        height, width = image.shape[:2]
        x, y, w, h = face.bbox

        scores = []

        # 1. Detection confidence (weight: 0.3)
        scores.append(face.confidence * 0.3)

        # 2. Face size score (weight: 0.25)
        # Ideal: face is 30-60% of image height
        face_ratio = h / height
        if 0.3 <= face_ratio <= 0.6:
            size_score = 1.0
        elif face_ratio < 0.3:
            size_score = face_ratio / 0.3
        else:
            size_score = max(0, 1 - (face_ratio - 0.6) / 0.4)
        scores.append(size_score * 0.25)

        # 3. Face position score (weight: 0.2)
        # Face center should be near image center
        face_center_x = x + w / 2
        face_center_y = y + h / 2
        center_offset_x = abs(face_center_x - width / 2) / (width / 2)
        center_offset_y = abs(face_center_y - height / 2) / (height / 2)
        position_score = 1 - (center_offset_x + center_offset_y) / 2
        scores.append(position_score * 0.2)

        # 4. Blur detection score (weight: 0.25)
        # Using Laplacian variance
        face_region = image[y:y+h, x:x+w]
        if face_region.size > 0:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            # Normalize (typical range 0-500 for good images)
            blur_score = min(1.0, laplacian_var / 300)
        else:
            blur_score = 0.0
        scores.append(blur_score * 0.25)

        total_score = sum(scores)
        logger.debug(f"Face quality scores: conf={face.confidence:.2f}, size={size_score:.2f}, "
                     f"pos={position_score:.2f}, blur={blur_score:.2f}, total={total_score:.2f}")

        return total_score

    def close(self):
        """Release resources."""
        self.face_detection.close()
        self.face_mesh.close()
        logger.info("Face Detection Service closed")
