"""
Registration Router - Student Enrollment API.

Handles student registration with face capture and embedding generation.
"""

import logging
import time
from datetime import datetime
from typing import Optional
import numpy as np
import cv2
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.models.schemas import StudentResponse, FaceDetectionResult

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


@router.post("/register", response_model=StudentResponse)
async def register_student(
    student_id: str = Form(..., description="Unique student identifier"),
    name: str = Form(..., description="Student's full name"),
    email: Optional[str] = Form(None, description="Student email"),
    department: Optional[str] = Form(None, description="Department/Class"),
    image: UploadFile = File(..., description="Master selfie image")
):
    """
    Register a new student with their face.

    This endpoint:
    1. Captures a high-quality "Master Selfie"
    2. Detects and validates the face
    3. Generates a 512-D Face Vector (Embedding) using ArcFace
    4. Stores the Vector and Student ID in the database

    Requirements:
    - Single face in the image
    - Face quality score > 0.5
    - Image format: JPEG, PNG

    Returns:
        StudentResponse with registration details
    """
    start_time = time.time()
    services = get_services()

    # Validate services are available
    if not all(services.values()):
        raise HTTPException(
            status_code=503,
            detail="Services not initialized. Please try again."
        )

    # Read and decode image
    try:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image format. Please upload a JPEG or PNG image."
            )
    except Exception as e:
        logger.error(f"Error reading image: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error processing image: {str(e)}"
        )

    # Check if student already exists
    existing = await services["database"].get_student(student_id)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Student with ID '{student_id}' already registered. Use update endpoint to change."
        )

    # Detect face
    face_detection = services["face_detection"]
    result = face_detection.extract_and_align_face(img)

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="No face detected in the image. Please ensure your face is clearly visible."
        )

    aligned_face, detected_face = result

    # Check for multiple faces
    all_faces = face_detection.detect_faces(img)
    if len(all_faces) > 1:
        raise HTTPException(
            status_code=400,
            detail=f"Multiple faces detected ({len(all_faces)}). Please ensure only one person is in the image."
        )

    # Calculate face quality
    face_quality = face_detection.calculate_face_quality(img, detected_face)

    if face_quality < 0.4:
        raise HTTPException(
            status_code=400,
            detail=f"Face quality too low ({face_quality:.2f}). Please take a clearer photo with good lighting."
        )

    # Generate face embedding
    face_embedding = services["face_embedding"]
    embedding = face_embedding.get_embedding(aligned_face)

    if embedding is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate face embedding. Please try again with a different image."
        )

    # Store student in database
    try:
        student = await services["database"].create_student(
            student_id=student_id,
            name=name,
            embedding=embedding,
            email=email,
            department=department,
            face_quality=face_quality
        )
    except Exception as e:
        logger.error(f"Error storing student: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store student record: {str(e)}"
        )

    processing_time = (time.time() - start_time) * 1000

    logger.info(f"Registered student {student_id} in {processing_time:.2f}ms")

    return StudentResponse(
        id=student["id"],
        student_id=student_id,
        name=name,
        email=email,
        department=department,
        registered_at=datetime.fromisoformat(student["registered_at"]),
        face_quality_score=face_quality,
        message=f"Successfully registered! Face quality: {face_quality:.1%}"
    )


@router.put("/register/{student_id}")
async def update_student_face(
    student_id: str,
    image: UploadFile = File(..., description="New master selfie image")
):
    """
    Update a student's face embedding.

    Use this to re-enroll a student with a new photo.
    """
    start_time = time.time()
    services = get_services()

    # Check if student exists
    existing = await services["database"].get_student(student_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{student_id}' not found."
        )

    # Read and decode image
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image format.")

    # Detect and align face
    result = services["face_detection"].extract_and_align_face(img)
    if result is None:
        raise HTTPException(status_code=400, detail="No face detected in the image.")

    aligned_face, detected_face = result

    # Check face quality
    face_quality = services["face_detection"].calculate_face_quality(img, detected_face)
    if face_quality < 0.4:
        raise HTTPException(
            status_code=400,
            detail=f"Face quality too low ({face_quality:.2f})."
        )

    # Generate new embedding
    embedding = services["face_embedding"].get_embedding(aligned_face)
    if embedding is None:
        raise HTTPException(status_code=500, detail="Failed to generate embedding.")

    # Update database
    success = await services["database"].update_student_embedding(student_id, embedding)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update embedding.")

    processing_time = (time.time() - start_time) * 1000

    return {
        "status": "success",
        "student_id": student_id,
        "face_quality_score": face_quality,
        "processing_time_ms": processing_time,
        "message": "Face embedding updated successfully."
    }


@router.get("/register/{student_id}")
async def get_student(student_id: str):
    """Get student registration details."""
    services = get_services()

    student = await services["database"].get_student(student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{student_id}' not found."
        )

    return student


@router.delete("/register/{student_id}")
async def delete_student(student_id: str):
    """Delete a student registration."""
    services = get_services()

    existing = await services["database"].get_student(student_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{student_id}' not found."
        )

    success = await services["database"].delete_student(student_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete student.")

    return {
        "status": "success",
        "message": f"Student '{student_id}' deleted successfully."
    }


@router.get("/students")
async def list_students(
    department: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List all registered students."""
    services = get_services()

    students = await services["database"].list_students(
        department=department,
        limit=limit,
        offset=offset
    )

    total = await services["database"].get_student_count()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "students": students
    }


@router.post("/validate-face")
async def validate_face(
    image: UploadFile = File(..., description="Image to validate")
):
    """
    Validate a face image without registering.

    Use this to check if an image is suitable for registration.
    """
    services = get_services()

    # Read image
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return {
            "valid": False,
            "message": "Invalid image format."
        }

    # Detect face
    result = services["face_detection"].extract_and_align_face(img)

    if result is None:
        return {
            "valid": False,
            "message": "No face detected in the image.",
            "face_detected": False
        }

    aligned_face, detected_face = result

    # Check for multiple faces
    all_faces = services["face_detection"].detect_faces(img)

    # Calculate quality
    face_quality = services["face_detection"].calculate_face_quality(img, detected_face)

    # Run liveness check
    liveness_result = services["liveness"].check_liveness(
        img, detected_face.bbox
    )

    return {
        "valid": face_quality >= 0.4 and len(all_faces) == 1 and liveness_result.is_live,
        "face_detected": True,
        "num_faces": len(all_faces),
        "face_quality": face_quality,
        "detection_confidence": detected_face.confidence,
        "liveness": {
            "is_live": liveness_result.is_live,
            "confidence": liveness_result.confidence,
            "checks_passed": liveness_result.checks_passed,
            "checks_failed": liveness_result.checks_failed
        },
        "bbox": list(detected_face.bbox),
        "message": "Image is suitable for registration." if face_quality >= 0.4 else "Image quality too low."
    }
