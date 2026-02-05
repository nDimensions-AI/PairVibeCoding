"""
Database Service for Face Attendance System.

This module handles all database operations using Supabase with pgvector
for efficient vector similarity search across 5,000+ face embeddings.
"""

import logging
import time
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import uuid4
import numpy as np

logger = logging.getLogger(__name__)

# Try to import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase not available, using in-memory storage")


class DatabaseService:
    """
    Database service for managing students and attendance records.

    Uses Supabase with pgvector extension for efficient vector similarity search.
    Falls back to in-memory storage if Supabase is not configured.
    """

    def __init__(self, supabase_url: str = "", supabase_key: str = ""):
        """
        Initialize the database service.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client: Optional[Client] = None

        # In-memory storage (fallback/demo mode)
        self._students: dict = {}  # student_id -> student data
        self._embeddings: dict = {}  # student_id -> embedding
        self._attendance: List[dict] = []  # attendance records

        if SUPABASE_AVAILABLE and supabase_url and supabase_key:
            self._initialize_supabase()
        else:
            logger.warning("Running in demo mode with in-memory storage")

    def _initialize_supabase(self):
        """Initialize Supabase client."""
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            self.client = None

    # ==================== Student Operations ====================

    async def create_student(
        self,
        student_id: str,
        name: str,
        embedding: np.ndarray,
        email: Optional[str] = None,
        department: Optional[str] = None,
        face_quality: float = 0.0
    ) -> dict:
        """
        Create a new student record with face embedding.

        Args:
            student_id: Unique student identifier
            name: Student's full name
            embedding: 512-D face embedding vector
            email: Optional email address
            department: Optional department/class
            face_quality: Quality score of the enrollment image

        Returns:
            Created student record
        """
        record_id = str(uuid4())
        now = datetime.utcnow().isoformat()

        student_data = {
            "id": record_id,
            "student_id": student_id,
            "name": name,
            "email": email,
            "department": department,
            "face_quality": face_quality,
            "registered_at": now,
            "updated_at": now
        }

        if self.client:
            try:
                # Store student info
                result = self.client.table("students").insert(student_data).execute()

                # Store embedding separately (pgvector)
                embedding_data = {
                    "id": str(uuid4()),
                    "student_id": student_id,
                    "embedding": embedding.tolist()
                }
                self.client.table("face_embeddings").insert(embedding_data).execute()

                logger.info(f"Created student in Supabase: {student_id}")
                return student_data

            except Exception as e:
                logger.error(f"Supabase error creating student: {e}")
                # Fall through to in-memory storage

        # In-memory storage
        self._students[student_id] = student_data
        self._embeddings[student_id] = embedding
        logger.info(f"Created student in memory: {student_id}")

        return student_data

    async def get_student(self, student_id: str) -> Optional[dict]:
        """Get a student by ID."""
        if self.client:
            try:
                result = self.client.table("students").select("*").eq(
                    "student_id", student_id
                ).execute()
                if result.data:
                    return result.data[0]
            except Exception as e:
                logger.error(f"Error fetching student from Supabase: {e}")

        return self._students.get(student_id)

    async def get_student_embedding(self, student_id: str) -> Optional[np.ndarray]:
        """Get a student's face embedding."""
        if self.client:
            try:
                result = self.client.table("face_embeddings").select("embedding").eq(
                    "student_id", student_id
                ).execute()
                if result.data:
                    return np.array(result.data[0]["embedding"], dtype=np.float32)
            except Exception as e:
                logger.error(f"Error fetching embedding from Supabase: {e}")

        return self._embeddings.get(student_id)

    async def update_student_embedding(
        self,
        student_id: str,
        embedding: np.ndarray
    ) -> bool:
        """Update a student's face embedding."""
        if self.client:
            try:
                self.client.table("face_embeddings").update({
                    "embedding": embedding.tolist(),
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("student_id", student_id).execute()
                return True
            except Exception as e:
                logger.error(f"Error updating embedding in Supabase: {e}")

        if student_id in self._embeddings:
            self._embeddings[student_id] = embedding
            return True

        return False

    async def delete_student(self, student_id: str) -> bool:
        """Delete a student and their embedding."""
        if self.client:
            try:
                self.client.table("face_embeddings").delete().eq(
                    "student_id", student_id
                ).execute()
                self.client.table("students").delete().eq(
                    "student_id", student_id
                ).execute()
                logger.info(f"Deleted student from Supabase: {student_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting student from Supabase: {e}")

        if student_id in self._students:
            del self._students[student_id]
            del self._embeddings[student_id]
            return True

        return False

    async def list_students(
        self,
        department: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """List all students, optionally filtered by department."""
        if self.client:
            try:
                query = self.client.table("students").select("*")
                if department:
                    query = query.eq("department", department)
                result = query.range(offset, offset + limit - 1).execute()
                return result.data
            except Exception as e:
                logger.error(f"Error listing students from Supabase: {e}")

        students = list(self._students.values())
        if department:
            students = [s for s in students if s.get("department") == department]
        return students[offset:offset + limit]

    async def get_student_count(self) -> int:
        """Get total number of registered students."""
        if self.client:
            try:
                result = self.client.table("students").select(
                    "id", count="exact"
                ).execute()
                return result.count or 0
            except Exception as e:
                logger.error(f"Error counting students: {e}")

        return len(self._students)

    # ==================== Vector Search Operations ====================

    async def find_matching_student(
        self,
        query_embedding: np.ndarray,
        threshold: float = 0.45
    ) -> Tuple[Optional[str], float, float]:
        """
        Find the best matching student for a query embedding.

        Uses cosine similarity with pgvector or in-memory comparison.

        Args:
            query_embedding: 512-D query face embedding
            threshold: Minimum similarity threshold (cosine similarity)

        Returns:
            Tuple of (student_id, similarity_score, search_time_ms)
        """
        start_time = time.time()

        if self.client:
            try:
                # Use pgvector's cosine similarity search
                # Note: pgvector uses cosine distance, so we need 1 - distance for similarity
                result = self.client.rpc(
                    "match_face_embedding",
                    {
                        "query_embedding": query_embedding.tolist(),
                        "match_threshold": 1 - threshold,  # Convert similarity to distance
                        "match_count": 1
                    }
                ).execute()

                search_time = (time.time() - start_time) * 1000

                if result.data:
                    match = result.data[0]
                    similarity = 1 - match.get("distance", 1)  # Convert back to similarity
                    return match["student_id"], similarity, search_time

                return None, 0.0, search_time

            except Exception as e:
                logger.error(f"pgvector search error: {e}")
                # Fall through to in-memory search

        # In-memory search using cosine similarity
        best_match = None
        best_similarity = 0.0

        for student_id, stored_embedding in self._embeddings.items():
            # Cosine similarity (embeddings should be normalized)
            similarity = np.dot(query_embedding, stored_embedding)
            # Convert from [-1, 1] to [0, 1]
            similarity = (similarity + 1) / 2

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = student_id

        search_time = (time.time() - start_time) * 1000

        if best_similarity >= threshold:
            logger.info(f"Match found: {best_match} with similarity {best_similarity:.4f} "
                        f"in {search_time:.2f}ms")
            return best_match, best_similarity, search_time

        logger.info(f"No match found above threshold {threshold} in {search_time:.2f}ms")
        return None, best_similarity, search_time

    async def get_all_embeddings(self) -> List[Tuple[str, np.ndarray]]:
        """Get all student embeddings for batch processing."""
        if self.client:
            try:
                result = self.client.table("face_embeddings").select(
                    "student_id, embedding"
                ).execute()
                return [
                    (r["student_id"], np.array(r["embedding"], dtype=np.float32))
                    for r in result.data
                ]
            except Exception as e:
                logger.error(f"Error fetching all embeddings: {e}")

        return list(self._embeddings.items())

    # ==================== Attendance Operations ====================

    async def record_attendance(
        self,
        student_id: str,
        status: str,
        similarity_score: float,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        device_id: Optional[str] = None,
        processing_time_ms: float = 0.0
    ) -> dict:
        """
        Record an attendance entry.

        Args:
            student_id: Student ID (or "unknown" for failed matches)
            status: Attendance status (success, failure, spoof_detected, etc.)
            similarity_score: Face matching similarity score
            latitude: GPS latitude
            longitude: GPS longitude
            device_id: Device identifier
            processing_time_ms: Total processing time

        Returns:
            Created attendance record
        """
        record_id = str(uuid4())
        now = datetime.utcnow().isoformat()

        # Get student name if matched
        student_name = None
        if student_id and student_id != "unknown":
            student = await self.get_student(student_id)
            if student:
                student_name = student.get("name")

        record = {
            "id": record_id,
            "student_id": student_id,
            "student_name": student_name,
            "timestamp": now,
            "status": status,
            "similarity_score": similarity_score,
            "latitude": latitude,
            "longitude": longitude,
            "device_id": device_id,
            "processing_time_ms": processing_time_ms
        }

        if self.client:
            try:
                self.client.table("attendance_records").insert(record).execute()
                logger.info(f"Recorded attendance in Supabase: {student_id} - {status}")
                return record
            except Exception as e:
                logger.error(f"Error recording attendance in Supabase: {e}")

        # In-memory storage
        self._attendance.append(record)
        logger.info(f"Recorded attendance in memory: {student_id} - {status}")

        return record

    async def get_attendance_records(
        self,
        student_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """Get attendance records with optional filters."""
        if self.client:
            try:
                query = self.client.table("attendance_records").select("*")

                if student_id:
                    query = query.eq("student_id", student_id)
                if status:
                    query = query.eq("status", status)
                if start_date:
                    query = query.gte("timestamp", start_date.isoformat())
                if end_date:
                    query = query.lte("timestamp", end_date.isoformat())

                result = query.order(
                    "timestamp", desc=True
                ).range(offset, offset + limit - 1).execute()

                return result.data

            except Exception as e:
                logger.error(f"Error fetching attendance records: {e}")

        # In-memory filtering
        records = self._attendance.copy()

        if student_id:
            records = [r for r in records if r["student_id"] == student_id]
        if status:
            records = [r for r in records if r["status"] == status]
        if start_date:
            records = [r for r in records if r["timestamp"] >= start_date.isoformat()]
        if end_date:
            records = [r for r in records if r["timestamp"] <= end_date.isoformat()]

        # Sort by timestamp descending
        records.sort(key=lambda x: x["timestamp"], reverse=True)

        return records[offset:offset + limit]

    async def get_attendance_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get attendance statistics."""
        records = await self.get_attendance_records(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )

        total = len(records)
        if total == 0:
            return {
                "total_records": 0,
                "success_count": 0,
                "failure_count": 0,
                "spoof_count": 0,
                "success_rate": 0.0,
                "average_processing_time_ms": 0.0
            }

        success_count = sum(1 for r in records if r["status"] == "success")
        failure_count = sum(1 for r in records if r["status"] in ["failure", "no_match"])
        spoof_count = sum(1 for r in records if r["status"] == "spoof_detected")
        avg_processing_time = sum(r.get("processing_time_ms", 0) for r in records) / total

        return {
            "total_records": total,
            "success_count": success_count,
            "failure_count": failure_count,
            "spoof_count": spoof_count,
            "success_rate": success_count / total if total > 0 else 0.0,
            "average_processing_time_ms": avg_processing_time
        }

    async def get_today_attendance(self) -> List[dict]:
        """Get today's attendance records."""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return await self.get_attendance_records(start_date=today)

    # ==================== Demo Data Generation ====================

    async def generate_demo_data(self, count: int = 100) -> int:
        """
        Generate demo student records with random embeddings.
        Useful for testing vector search performance with 5,000 records.

        Args:
            count: Number of demo records to generate

        Returns:
            Number of records created
        """
        logger.info(f"Generating {count} demo student records...")

        departments = ["Computer Science", "Engineering", "Business", "Arts", "Science"]
        created = 0

        for i in range(count):
            student_id = f"DEMO{i:05d}"

            # Skip if already exists
            if student_id in self._students:
                continue

            # Generate random normalized embedding
            embedding = np.random.randn(512).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)

            await self.create_student(
                student_id=student_id,
                name=f"Demo Student {i}",
                embedding=embedding,
                email=f"demo{i}@example.com",
                department=departments[i % len(departments)],
                face_quality=0.8
            )
            created += 1

        logger.info(f"Generated {created} demo records")
        return created
