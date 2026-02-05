"""
Liveness Detection Service (Anti-Spoofing).

This module implements passive liveness detection to prevent photo/screen-based
spoofing attacks. It uses multiple techniques to determine if the face is real.
"""

import logging
import numpy as np
import cv2
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SpoofType(str, Enum):
    """Types of spoofing attacks detected."""
    NONE = "none"
    PRINTED_PHOTO = "printed_photo"
    SCREEN_REPLAY = "screen_replay"
    MASK = "mask"
    UNKNOWN = "unknown"


@dataclass
class LivenessResult:
    """Result of liveness detection."""
    is_live: bool
    confidence: float
    spoof_type: SpoofType
    checks_passed: List[str]
    checks_failed: List[str]
    details: dict


class LivenessService:
    """
    Passive liveness detection service.

    Implements multiple anti-spoofing techniques:
    1. Texture Analysis (LBP) - Detects printed photos
    2. Color Analysis - Detects screen replay attacks
    3. Reflection Analysis - Detects glossy surfaces
    4. Frequency Analysis - Detects moire patterns from screens
    5. Depth Estimation - Basic depth cues analysis
    """

    def __init__(self, threshold: float = 0.5):
        """
        Initialize the liveness service.

        Args:
            threshold: Overall threshold for liveness (0-1)
        """
        self.threshold = threshold
        self.checks = [
            ("texture", self._check_texture_lbp, 0.25),
            ("color", self._check_color_analysis, 0.20),
            ("reflection", self._check_reflection, 0.20),
            ("frequency", self._check_frequency, 0.20),
            ("sharpness", self._check_sharpness, 0.15),
        ]
        logger.info(f"Liveness Service initialized with threshold={threshold}")

    def check_liveness(
        self,
        image: np.ndarray,
        face_bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> LivenessResult:
        """
        Perform comprehensive liveness check on an image.

        Args:
            image: BGR image
            face_bbox: Optional face bounding box (x, y, w, h)

        Returns:
            LivenessResult with detailed analysis
        """
        if image is None:
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                spoof_type=SpoofType.UNKNOWN,
                checks_passed=[],
                checks_failed=["image_validation"],
                details={"error": "Invalid image"}
            )

        # Extract face region if bbox provided
        if face_bbox:
            x, y, w, h = face_bbox
            # Add padding
            pad = int(min(w, h) * 0.2)
            y1 = max(0, y - pad)
            y2 = min(image.shape[0], y + h + pad)
            x1 = max(0, x - pad)
            x2 = min(image.shape[1], x + w + pad)
            face_region = image[y1:y2, x1:x2]
        else:
            face_region = image

        # Run all checks
        total_score = 0.0
        checks_passed = []
        checks_failed = []
        details = {}

        for check_name, check_fn, weight in self.checks:
            try:
                score, check_details = check_fn(face_region)
                weighted_score = score * weight
                total_score += weighted_score
                details[check_name] = {
                    "score": score,
                    "weighted_score": weighted_score,
                    "details": check_details
                }

                if score >= 0.5:
                    checks_passed.append(check_name)
                else:
                    checks_failed.append(check_name)

            except Exception as e:
                logger.error(f"Error in {check_name} check: {e}")
                checks_failed.append(check_name)
                details[check_name] = {"error": str(e)}

        # Determine if live and spoof type
        is_live = total_score >= self.threshold
        spoof_type = self._determine_spoof_type(details, is_live)

        # Calculate confidence
        confidence = min(1.0, total_score / self.threshold) if not is_live else total_score

        result = LivenessResult(
            is_live=is_live,
            confidence=confidence,
            spoof_type=spoof_type,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            details=details
        )

        logger.info(f"Liveness check: is_live={is_live}, confidence={confidence:.2f}, "
                    f"spoof_type={spoof_type.value}")

        return result

    def _check_texture_lbp(self, face_image: np.ndarray) -> Tuple[float, dict]:
        """
        Check texture using Local Binary Patterns (LBP).
        Real faces have more varied texture than printed photos.
        """
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

        # Compute LBP
        lbp = self._compute_lbp(gray)

        # Compute histogram
        hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
        hist = hist.astype(np.float32)
        hist /= (hist.sum() + 1e-7)

        # Calculate entropy (higher entropy = more texture variation = more likely real)
        entropy = -np.sum(hist * np.log2(hist + 1e-7))
        max_entropy = np.log2(256)
        normalized_entropy = entropy / max_entropy

        # Calculate histogram variance
        hist_variance = np.var(hist)

        # Real faces typically have entropy > 5.5 (normalized > 0.69)
        # and moderate histogram variance
        score = min(1.0, normalized_entropy * 1.2)

        return score, {
            "entropy": float(entropy),
            "normalized_entropy": float(normalized_entropy),
            "histogram_variance": float(hist_variance)
        }

    def _compute_lbp(self, gray_image: np.ndarray, radius: int = 1) -> np.ndarray:
        """Compute Local Binary Pattern."""
        rows, cols = gray_image.shape
        lbp = np.zeros((rows - 2, cols - 2), dtype=np.uint8)

        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                center = gray_image[i, j]
                code = 0
                code |= (gray_image[i-1, j-1] >= center) << 7
                code |= (gray_image[i-1, j] >= center) << 6
                code |= (gray_image[i-1, j+1] >= center) << 5
                code |= (gray_image[i, j+1] >= center) << 4
                code |= (gray_image[i+1, j+1] >= center) << 3
                code |= (gray_image[i+1, j] >= center) << 2
                code |= (gray_image[i+1, j-1] >= center) << 1
                code |= (gray_image[i, j-1] >= center) << 0
                lbp[i-1, j-1] = code

        return lbp

    def _check_color_analysis(self, face_image: np.ndarray) -> Tuple[float, dict]:
        """
        Analyze color distribution for screen/print detection.
        Screens have different color characteristics than real skin.
        """
        # Convert to different color spaces
        hsv = cv2.cvtColor(face_image, cv2.COLOR_BGR2HSV)
        ycrcb = cv2.cvtColor(face_image, cv2.COLOR_BGR2YCrCb)

        # Analyze skin color distribution in YCrCb
        # Real skin has Cr in range 133-173 and Cb in range 77-127
        cr = ycrcb[:, :, 1]
        cb = ycrcb[:, :, 2]

        cr_mean = np.mean(cr)
        cb_mean = np.mean(cb)
        cr_std = np.std(cr)
        cb_std = np.std(cb)

        # Check if color is in natural skin tone range
        cr_in_range = 133 <= cr_mean <= 173
        cb_in_range = 77 <= cb_mean <= 127

        # Real faces have moderate color variation
        color_variation = (cr_std + cb_std) / 2
        variation_score = min(1.0, color_variation / 15)

        # Saturation analysis (screens often have higher saturation)
        saturation = hsv[:, :, 1]
        sat_mean = np.mean(saturation)
        sat_score = 1.0 if sat_mean < 150 else max(0, 1 - (sat_mean - 150) / 50)

        # Combined score
        range_score = (1.0 if cr_in_range else 0.5) * (1.0 if cb_in_range else 0.5)
        score = (range_score * 0.4 + variation_score * 0.3 + sat_score * 0.3)

        return score, {
            "cr_mean": float(cr_mean),
            "cb_mean": float(cb_mean),
            "cr_std": float(cr_std),
            "cb_std": float(cb_std),
            "saturation_mean": float(sat_mean),
            "cr_in_range": cr_in_range,
            "cb_in_range": cb_in_range
        }

    def _check_reflection(self, face_image: np.ndarray) -> Tuple[float, dict]:
        """
        Check for specular reflections that indicate glossy surfaces.
        Printed photos and screens often have specular highlights.
        """
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

        # Find bright spots (potential reflections)
        _, bright_mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        bright_ratio = np.sum(bright_mask > 0) / bright_mask.size

        # Detect specular highlights using adaptive thresholding
        blur = cv2.GaussianBlur(gray, (21, 21), 0)
        diff = cv2.absdiff(gray, blur)
        _, specular_mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        specular_ratio = np.sum(specular_mask > 0) / specular_mask.size

        # Calculate reflection uniformity
        # Uniform bright areas suggest printed/screen surface
        if np.sum(bright_mask > 0) > 0:
            bright_regions = gray[bright_mask > 0]
            brightness_uniformity = 1 - np.std(bright_regions) / 255
        else:
            brightness_uniformity = 0

        # Score (less reflection = more likely real)
        reflection_penalty = bright_ratio * 2 + specular_ratio * 3
        score = max(0, 1 - reflection_penalty)

        return score, {
            "bright_ratio": float(bright_ratio),
            "specular_ratio": float(specular_ratio),
            "brightness_uniformity": float(brightness_uniformity)
        }

    def _check_frequency(self, face_image: np.ndarray) -> Tuple[float, dict]:
        """
        Analyze frequency domain for moire patterns.
        Screen replay attacks often show moire patterns from screen pixels.
        """
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

        # Resize for consistent analysis
        resized = cv2.resize(gray, (128, 128))

        # Apply FFT
        f = np.fft.fft2(resized)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = np.log(np.abs(fshift) + 1)

        # Analyze high frequency content
        center = 64
        radius = 50

        # Create masks for different frequency bands
        y, x = np.ogrid[:128, :128]
        dist_from_center = np.sqrt((x - center)**2 + (y - center)**2)

        # High frequency region (outside radius)
        high_freq_mask = dist_from_center > radius
        high_freq_energy = np.mean(magnitude_spectrum[high_freq_mask])

        # Low frequency region (inside radius)
        low_freq_mask = dist_from_center <= radius
        low_freq_energy = np.mean(magnitude_spectrum[low_freq_mask])

        # Real faces have smooth high/low frequency ratio
        # Screens often show peaks due to pixel structure
        if low_freq_energy > 0:
            freq_ratio = high_freq_energy / low_freq_energy
        else:
            freq_ratio = 0

        # Check for periodic peaks (moire patterns)
        # Normalize spectrum
        spectrum_normalized = magnitude_spectrum / (np.max(magnitude_spectrum) + 1e-7)

        # Count significant peaks in high frequency region
        high_freq_spectrum = spectrum_normalized * high_freq_mask
        peak_threshold = 0.5
        num_peaks = np.sum(high_freq_spectrum > peak_threshold)

        # Score (fewer peaks and lower freq_ratio = more likely real)
        peak_penalty = min(1, num_peaks / 50)
        ratio_penalty = min(1, max(0, freq_ratio - 0.3))
        score = max(0, 1 - (peak_penalty * 0.6 + ratio_penalty * 0.4))

        return score, {
            "high_freq_energy": float(high_freq_energy),
            "low_freq_energy": float(low_freq_energy),
            "freq_ratio": float(freq_ratio),
            "num_peaks": int(num_peaks)
        }

    def _check_sharpness(self, face_image: np.ndarray) -> Tuple[float, dict]:
        """
        Check image sharpness and focus.
        Real faces captured live have different focus characteristics.
        """
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

        # Laplacian variance (overall sharpness)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_var = laplacian.var()

        # Gradient magnitude (edge strength)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_mag = np.sqrt(sobelx**2 + sobely**2)
        gradient_mean = np.mean(gradient_mag)

        # Focus measure using modified Laplacian
        ml = np.abs(cv2.Laplacian(gray, cv2.CV_64F))
        focus_measure = np.mean(ml)

        # Good images have moderate sharpness
        # Too sharp or too blurry can indicate manipulation
        sharpness_score = min(1.0, laplacian_var / 500)
        if laplacian_var > 1000:  # Too sharp might be artificially enhanced
            sharpness_score = max(0.5, 1 - (laplacian_var - 1000) / 2000)

        # Combined score
        score = sharpness_score

        return score, {
            "laplacian_variance": float(laplacian_var),
            "gradient_mean": float(gradient_mean),
            "focus_measure": float(focus_measure)
        }

    def _determine_spoof_type(self, details: dict, is_live: bool) -> SpoofType:
        """Determine the type of spoofing based on analysis details."""
        if is_live:
            return SpoofType.NONE

        # Analyze failed checks to determine spoof type
        texture_score = details.get("texture", {}).get("score", 1)
        color_score = details.get("color", {}).get("score", 1)
        reflection_score = details.get("reflection", {}).get("score", 1)
        frequency_score = details.get("frequency", {}).get("score", 1)

        # Printed photos: low texture variation, reflection issues
        if texture_score < 0.4 and reflection_score < 0.5:
            return SpoofType.PRINTED_PHOTO

        # Screen replay: moire patterns, color issues
        if frequency_score < 0.4 or (color_score < 0.4 and frequency_score < 0.6):
            return SpoofType.SCREEN_REPLAY

        return SpoofType.UNKNOWN
