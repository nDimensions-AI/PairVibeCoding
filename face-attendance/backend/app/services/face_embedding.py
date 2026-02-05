"""
Face Embedding Service using InsightFace (ArcFace).

This module generates 512-dimensional face embeddings using the ArcFace model,
which is the industry standard for high-accuracy face recognition.
"""

import logging
import numpy as np
import cv2
from typing import Optional, List, Tuple
import time

logger = logging.getLogger(__name__)

# Try to import insightface
try:
    from insightface.app import FaceAnalysis
    from insightface.model_zoo import get_model
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    logger.warning("InsightFace not available, using fallback embedding method")


class FaceEmbeddingService:
    """
    Face embedding service using InsightFace ArcFace model.

    Generates 512-dimensional face vectors for high-accuracy face matching.
    Achieves >99.5% accuracy on standard benchmarks.
    """

    def __init__(
        self,
        model_name: str = "buffalo_l",  # Options: buffalo_l, buffalo_m, buffalo_s
        providers: List[str] = None,
        embedding_size: int = 512
    ):
        """
        Initialize the face embedding service.

        Args:
            model_name: InsightFace model pack name
            providers: ONNX execution providers (e.g., ['CUDAExecutionProvider', 'CPUExecutionProvider'])
            embedding_size: Expected embedding dimension (512 for ArcFace)
        """
        self.model_name = model_name
        self.embedding_size = embedding_size
        self.providers = providers or ['CPUExecutionProvider']
        self.model = None

        if INSIGHTFACE_AVAILABLE:
            self._initialize_insightface()
        else:
            logger.warning("Running in fallback mode without InsightFace")

    def _initialize_insightface(self):
        """Initialize InsightFace model."""
        try:
            # Initialize FaceAnalysis app
            self.model = FaceAnalysis(
                name=self.model_name,
                providers=self.providers
            )
            # Prepare model (downloads if needed)
            self.model.prepare(ctx_id=0, det_size=(640, 640))
            logger.info(f"InsightFace model '{self.model_name}' initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize InsightFace: {e}")
            self.model = None

    def get_embedding(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Generate a 512-D embedding for a face image.

        Args:
            face_image: Aligned face image (112x112 BGR) or full image

        Returns:
            512-dimensional normalized embedding vector or None if failed
        """
        if face_image is None:
            logger.error("Received None face image")
            return None

        start_time = time.time()

        if self.model is not None and INSIGHTFACE_AVAILABLE:
            embedding = self._get_embedding_insightface(face_image)
        else:
            embedding = self._get_embedding_fallback(face_image)

        elapsed = (time.time() - start_time) * 1000
        logger.debug(f"Embedding generation took {elapsed:.2f}ms")

        return embedding

    def _get_embedding_insightface(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Get embedding using InsightFace.

        Args:
            face_image: BGR image

        Returns:
            512-D embedding or None
        """
        try:
            # If image is already 112x112 (aligned), we need to handle differently
            if face_image.shape[0] == 112 and face_image.shape[1] == 112:
                # Resize to a larger size for detection
                face_image = cv2.resize(face_image, (224, 224))

            # Get faces from InsightFace
            faces = self.model.get(face_image)

            if not faces:
                logger.warning("No faces found by InsightFace")
                return None

            # Get embedding from the first (or best) face
            embedding = faces[0].embedding

            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)

            return embedding

        except Exception as e:
            logger.error(f"Error getting InsightFace embedding: {e}")
            return None

    def _get_embedding_fallback(self, face_image: np.ndarray) -> np.ndarray:
        """
        Fallback embedding method using simple CNN features.
        This is for demo purposes when InsightFace is not available.

        Args:
            face_image: BGR face image

        Returns:
            512-D pseudo-embedding
        """
        logger.warning("Using fallback embedding method - accuracy will be limited")

        # Resize to standard size
        face_resized = cv2.resize(face_image, (112, 112))

        # Convert to grayscale and flatten
        gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)

        # Compute HOG-like features
        # This is a simplified approach for demo without ML models
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
        mag, ang = cv2.cartToPolar(gx, gy)

        # Compute histogram of gradients for 8x8 cells
        cell_size = 14  # 112 / 8 = 14
        n_bins = 8
        features = []

        for i in range(0, 112, cell_size):
            for j in range(0, 112, cell_size):
                cell_mag = mag[i:i+cell_size, j:j+cell_size]
                cell_ang = ang[i:i+cell_size, j:j+cell_size]
                hist, _ = np.histogram(
                    cell_ang.flatten(),
                    bins=n_bins,
                    range=(0, 2*np.pi),
                    weights=cell_mag.flatten()
                )
                features.extend(hist)

        # Pad or truncate to 512 dimensions
        features = np.array(features, dtype=np.float32)
        if len(features) < 512:
            features = np.pad(features, (0, 512 - len(features)))
        else:
            features = features[:512]

        # Normalize
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm

        return features

    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First 512-D embedding
            embedding2: Second 512-D embedding

        Returns:
            Similarity score between 0 and 1
        """
        # Both embeddings should be normalized, so dot product = cosine similarity
        similarity = np.dot(embedding1, embedding2)

        # Clamp to [0, 1] range
        similarity = max(0.0, min(1.0, (similarity + 1) / 2))

        return float(similarity)

    def find_best_match(
        self,
        query_embedding: np.ndarray,
        gallery_embeddings: List[np.ndarray],
        threshold: float = 0.45
    ) -> Tuple[int, float]:
        """
        Find the best matching embedding in a gallery.

        Args:
            query_embedding: Query face embedding
            gallery_embeddings: List of gallery embeddings
            threshold: Minimum similarity threshold

        Returns:
            Tuple of (best match index, similarity score) or (-1, 0) if no match
        """
        if not gallery_embeddings:
            return -1, 0.0

        best_idx = -1
        best_similarity = 0.0

        for idx, gallery_emb in enumerate(gallery_embeddings):
            similarity = self.compute_similarity(query_embedding, gallery_emb)
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_idx = idx

        return best_idx, best_similarity

    def batch_embeddings(
        self,
        face_images: List[np.ndarray]
    ) -> List[Optional[np.ndarray]]:
        """
        Generate embeddings for a batch of face images.

        Args:
            face_images: List of face images

        Returns:
            List of embeddings (None for failed extractions)
        """
        embeddings = []
        for face_img in face_images:
            embedding = self.get_embedding(face_img)
            embeddings.append(embedding)
        return embeddings

    def embedding_to_list(self, embedding: np.ndarray) -> List[float]:
        """Convert numpy embedding to Python list for JSON serialization."""
        return embedding.tolist()

    def list_to_embedding(self, embedding_list: List[float]) -> np.ndarray:
        """Convert Python list back to numpy embedding."""
        return np.array(embedding_list, dtype=np.float32)
