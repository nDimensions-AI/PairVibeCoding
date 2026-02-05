"""
Attendance Router - Face Verification API.

Handles attendance marking through face recognition with liveness detection.
"""

import logging
import time
from datetime import datetime
from typing import Optional
import numpy as np
import cv2
from fastapi import APIRouter, File, UploadFile, Form, HTTPException

from app.models.schemas import (
    AttendanceResponse,
    AttendanceStatus,
    FaceDetectionResult,
    LivenessResult,
    MatchResult
)

logger = logging.getLogger(__name__)
router = APIRouter()


def get_services():
    """Get service instances from main app."""
    from app.main import get_service
    return {
        "face_detection": get_service("face_detection"),
        "face_embedding": get_service("face_embedding"),
        "liveness": get_service("liveness"),
        "database": get_service("database")
    }


@router.post("/attendance", response_model=AttendanceResponse)
async def mark_attendance(
    image: UploadFile = File(..., description="Live face image for attendance"),
    latitude: Optional[float] = Form(None, description="GPS latitude"),
    longitude: Optional[float] = Form(None, description="GPS longitude"),
    device_id: Optional[str] = Form(None, description="Device identifier")
):
    """
    Mark attendance using face recognition.

    This endpoint performs:
    1. Real-time face detection via MediaPipe
    2. Liveness Check: Passive anti-spoofing to detect photos/screens
    3. Vector Comparison: Cosine Similarity matching against the database
    4. Attendance Logging: Success/Failure, Timestamp, and GPS location

    Performance Targets:
    - Processing Time: <1.5 seconds
    - Match Accuracy: >99.5%
    - Search Time: <10ms for 5,000 identities

    Returns:
        AttendanceResponse with detailed results
    """
    start_time = time.time()
    services = get_services()

    # Initialize response components
    face_detection_result = FaceDetectionResult(
        face_detected=False,
        num_faces=0,
        face_bbox=None,
        face_landmarks=None,
        detection_confidence=0.0,
        face_quality=0.0
    )
    liveness_result = LivenessResult(
        is_live=False,
        confidence=0.0,
        spoof_type=None,
        checks_passed=[]
    )
    match_result = None

    # Validate services
    if not all(services.values()):
        processing_time = (time.time() - start_time) * 1000
        return AttendanceResponse(
            status=AttendanceStatus.FAILURE,
            timestamp=datetime.utcnow(),
            message="Services not initialized. Please try again.",
            face_detection=face_detection_result,
            liveness=liveness_result,
            processing_time_ms=processing_time
        )

    # Read and decode image
    try:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            processing_time = (time.time() - start_time) * 1000
            return AttendanceResponse(
                status=AttendanceStatus.FAILURE,
                timestamp=datetime.utcnow(),
                message="Invalid image format.",
                face_detection=face_detection_result,
                liveness=liveness_result,
                processing_time_ms=processing_time
            )
    except Exception as e:
        logger.error(f"Error reading image: {e}")
        processing_time = (time.time() - start_time) * 1000
        return AttendanceResponse(
            status=AttendanceStatus.FAILURE,
            timestamp=datetime.utcnow(),
            message=f"Error processing image: {str(e)}",
            face_detection=face_detection_result,
            liveness=liveness_result,
            processing_time_ms=processing_time
        )

    # Step 1: Face Detection
    detection_start = time.time()
    face_detection_service = services["face_detection"]
    result = face_detection_service.extract_and_align_face(img)

    if result is None:
        # No face detected
        processing_time = (time.time() - start_time) * 1000
        face_detection_result.face_detected = False

        # Log failed attempt
        await services["database"].record_attendance(
            student_id="unknown",
            status="no_face_detected",
            similarity_score=0.0,
            latitude=latitude,
            longitude=longitude,
            device_id=device_id,
            processing_time_ms=processing_time
        )

        return AttendanceResponse(
            status=AttendanceStatus.NO_FACE_DETECTED,
            timestamp=datetime.utcnow(),
            message="No face detected. Please ensure your face is clearly visible.",
            face_detection=face_detection_result,
            liveness=liveness_result,
            processing_time_ms=processing_time
        )

    aligned_face, detected_face = result

    # Check for multiple faces
    all_faces = face_detection_service.detect_faces(img)
    if len(all_faces) > 1:
        processing_time = (time.time() - start_time) * 1000
        face_detection_result.face_detected = True
        face_detection_result.num_faces = len(all_faces)

        await services["database"].record_attendance(
            student_id="unknown",
            status="multiple_faces",
            similarity_score=0.0,
            latitude=latitude,
            longitude=longitude,
            device_id=device_id,
            processing_time_ms=processing_time
        )

        return AttendanceResponse(
            status=AttendanceStatus.MULTIPLE_FACES,
            timestamp=datetime.utcnow(),
            message=f"Multiple faces detected ({len(all_faces)}). Only one person should be in frame.",
            face_detection=face_detection_result,
            liveness=liveness_result,
            processing_time_ms=processing_time
        )

    # Update face detection result
    face_quality = face_detection_service.calculate_face_quality(img, detected_face)
    face_detection_result = FaceDetectionResult(
        face_detected=True,
        num_faces=1,
        face_bbox=list(detected_face.bbox),
        face_landmarks=[list(lm) for lm in detected_face.landmarks] if detected_face.landmarks else None,
        detection_confidence=detected_face.confidence,
        face_quality=face_quality
    )
    detection_time = (time.time() - detection_start) * 1000
    logger.debug(f"Face detection took {detection_time:.2f}ms")

    # Step 2: Liveness Detection (Anti-Spoofing)
    liveness_start = time.time()
    liveness_service = services["liveness"]
    liveness_check = liveness_service.check_liveness(img, detected_face.bbox)

    liveness_result = LivenessResult(
        is_live=liveness_check.is_live,
        confidence=liveness_check.confidence,
        spoof_type=liveness_check.spoof_type.value if not liveness_check.is_live else None,
        checks_passed=liveness_check.checks_passed
    )
    liveness_time = (time.time() - liveness_start) * 1000
    logger.debug(f"Liveness check took {liveness_time:.2f}ms")

    if not liveness_check.is_live:
        processing_time = (time.time() - start_time) * 1000

        await services["database"].record_attendance(
            student_id="unknown",
            status="spoof_detected",
            similarity_score=0.0,
            latitude=latitude,
            longitude=longitude,
            device_id=device_id,
            processing_time_ms=processing_time
        )

        return AttendanceResponse(
            status=AttendanceStatus.SPOOF_DETECTED,
            timestamp=datetime.utcnow(),
            message=f"Spoof detected: {liveness_check.spoof_type.value}. Please use a live camera.",
            face_detection=face_detection_result,
            liveness=liveness_result,
            processing_time_ms=processing_time
        )

    # Step 3: Generate Face Embedding
    embedding_start = time.time()
    embedding_service = services["face_embedding"]
    query_embedding = embedding_service.get_embedding(aligned_face)

    if query_embedding is None:
        processing_time = (time.time() - start_time) * 1000
        return AttendanceResponse(
            status=AttendanceStatus.FAILURE,
            timestamp=datetime.utcnow(),
            message="Failed to process face. Please try again.",
            face_detection=face_detection_result,
            liveness=liveness_result,
            processing_time_ms=processing_time
        )

    embedding_time = (time.time() - embedding_start) * 1000
    logger.debug(f"Embedding generation took {embedding_time:.2f}ms")

    # Step 4: Vector Search (Face Matching)
    db_service = services["database"]
    matched_student_id, similarity_score, search_time = await db_service.find_matching_student(
        query_embedding=query_embedding,
        threshold=0.45  # Cosine similarity threshold
    )

    if matched_student_id is None:
        processing_time = (time.time() - start_time) * 1000

        match_result = MatchResult(
            matched=False,
            similarity_score=similarity_score,
            search_time_ms=search_time
        )

        await db_service.record_attendance(
            student_id="unknown",
            status="no_match",
            similarity_score=similarity_score,
            latitude=latitude,
            longitude=longitude,
            device_id=device_id,
            processing_time_ms=processing_time
        )

        return AttendanceResponse(
            status=AttendanceStatus.NO_MATCH,
            timestamp=datetime.utcnow(),
            message="Face not recognized. Please ensure you are registered.",
            face_detection=face_detection_result,
            liveness=liveness_result,
            match=match_result,
            processing_time_ms=processing_time
        )

    # Get student details
    student = await db_service.get_student(matched_student_id)
    student_name = student.get("name", "Unknown") if student else "Unknown"

    match_result = MatchResult(
        matched=True,
        student_id=matched_student_id,
        student_name=student_name,
        similarity_score=similarity_score,
        search_time_ms=search_time
    )

    # Step 5: Record Successful Attendance
    processing_time = (time.time() - start_time) * 1000

    await db_service.record_attendance(
        student_id=matched_student_id,
        status="success",
        similarity_score=similarity_score,
        latitude=latitude,
        longitude=longitude,
        device_id=device_id,
        processing_time_ms=processing_time
    )

    logger.info(f"Attendance marked for {matched_student_id} ({student_name}) "
                f"with similarity {similarity_score:.4f} in {processing_time:.2f}ms")

    return AttendanceResponse(
        status=AttendanceStatus.SUCCESS,
        student_id=matched_student_id,
        student_name=student_name,
        timestamp=datetime.utcnow(),
        message=f"Attendance marked successfully! Welcome, {student_name}.",
        face_detection=face_detection_result,
        liveness=liveness_result,
        match=match_result,
        processing_time_ms=processing_time
    )


@router.post("/attendance/verify")
async def verify_identity(
    student_id: str = Form(..., description="Student ID to verify"),
    image: UploadFile = File(..., description="Live face image")
):
    """
    Verify a specific student's identity (1:1 verification).

    Unlike the general attendance endpoint which searches all students (1:N),
    this endpoint verifies against a specific student's stored embedding.
    """
    start_time = time.time()
    services = get_services()

    # Get student's stored embedding
    stored_embedding = await services["database"].get_student_embedding(student_id)
    if stored_embedding is None:
        raise HTTPException(
            status_code=404,
            detail=f"Student '{student_id}' not found or has no registered face."
        )

    # Read image
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image format.")

    # Detect face
    result = services["face_detection"].extract_and_align_face(img)
    if result is None:
        return {
            "verified": False,
            "message": "No face detected.",
            "processing_time_ms": (time.time() - start_time) * 1000
        }

    aligned_face, detected_face = result

    # Liveness check
    liveness = services["liveness"].check_liveness(img, detected_face.bbox)
    if not liveness.is_live:
        return {
            "verified": False,
            "message": f"Spoof detected: {liveness.spoof_type.value}",
            "processing_time_ms": (time.time() - start_time) * 1000
        }

    # Generate embedding
    query_embedding = services["face_embedding"].get_embedding(aligned_face)
    if query_embedding is None:
        return {
            "verified": False,
            "message": "Failed to process face.",
            "processing_time_ms": (time.time() - start_time) * 1000
        }

    # Compare embeddings
    similarity = services["face_embedding"].compute_similarity(
        query_embedding, stored_embedding
    )

    processing_time = (time.time() - start_time) * 1000
    verified = similarity >= 0.45

    return {
        "verified": verified,
        "student_id": student_id,
        "similarity_score": similarity,
        "threshold": 0.45,
        "message": "Identity verified." if verified else "Identity not verified.",
        "processing_time_ms": processing_time
    }


@router.get("/attendance/today")
async def get_today_attendance():
    """Get today's attendance records."""
    services = get_services()
    records = await services["database"].get_today_attendance()
    return {
        "date": datetime.utcnow().date().isoformat(),
        "total": len(records),
        "records": records
    }


@router.get("/attendance/history")
async def get_attendance_history(
    student_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get attendance history with optional filters."""
    services = get_services()
    records = await services["database"].get_attendance_records(
        student_id=student_id,
        status=status,
        limit=limit,
        offset=offset
    )
    return {
        "total": len(records),
        "limit": limit,
        "offset": offset,
        "records": records
    }
