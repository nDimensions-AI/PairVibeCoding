"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class AttendanceStatus(str, Enum):
    """Attendance marking status."""
    SUCCESS = "success"
    FAILURE = "failure"
    SPOOF_DETECTED = "spoof_detected"
    NO_FACE_DETECTED = "no_face_detected"
    MULTIPLE_FACES = "multiple_faces"
    NO_MATCH = "no_match"


class StudentCreate(BaseModel):
    """Schema for student registration request."""
    student_id: str = Field(..., min_length=1, max_length=50, description="Unique student identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Student full name")
    email: Optional[str] = Field(None, max_length=255, description="Student email")
    department: Optional[str] = Field(None, max_length=100, description="Department/Class")
    # Image will be sent as file upload, not in JSON body


class StudentResponse(BaseModel):
    """Schema for student registration response."""
    id: str
    student_id: str
    name: str
    email: Optional[str] = None
    department: Optional[str] = None
    registered_at: datetime
    face_quality_score: float = Field(..., ge=0, le=1, description="Quality score of captured face")
    message: str


class FaceDetectionResult(BaseModel):
    """Result of face detection in an image."""
    face_detected: bool
    num_faces: int
    face_bbox: Optional[List[float]] = Field(None, description="Bounding box [x, y, width, height]")
    face_landmarks: Optional[List[List[float]]] = Field(None, description="Facial landmarks")
    detection_confidence: float = Field(..., ge=0, le=1)
    face_quality: float = Field(..., ge=0, le=1, description="Face quality score")


class LivenessResult(BaseModel):
    """Result of liveness detection."""
    is_live: bool
    confidence: float = Field(..., ge=0, le=1)
    spoof_type: Optional[str] = Field(None, description="Type of spoof if detected")
    checks_passed: List[str] = Field(default_factory=list, description="List of passed liveness checks")


class MatchResult(BaseModel):
    """Result of face matching against database."""
    matched: bool
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    similarity_score: float = Field(..., ge=0, le=1)
    search_time_ms: float = Field(..., description="Time taken to search in milliseconds")


class AttendanceRequest(BaseModel):
    """Schema for attendance marking request metadata."""
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="GPS latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="GPS longitude")
    device_id: Optional[str] = Field(None, max_length=100, description="Device identifier")
    # Image will be sent as file upload


class AttendanceResponse(BaseModel):
    """Schema for attendance marking response."""
    status: AttendanceStatus
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    timestamp: datetime
    message: str
    face_detection: FaceDetectionResult
    liveness: LivenessResult
    match: Optional[MatchResult] = None
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")


class AttendanceRecord(BaseModel):
    """Schema for attendance record from database."""
    id: str
    student_id: str
    student_name: str
    timestamp: datetime
    status: AttendanceStatus
    similarity_score: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    device_id: Optional[str] = None


class AttendanceReportRequest(BaseModel):
    """Schema for attendance report request."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    student_id: Optional[str] = None
    department: Optional[str] = None
    status: Optional[AttendanceStatus] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


class AttendanceReportResponse(BaseModel):
    """Schema for attendance report response."""
    total_records: int
    records: List[AttendanceRecord]
    success_rate: float = Field(..., ge=0, le=1)
    spoof_attempts: int
    period: dict


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    services: dict
    version: str = "1.0.0"


class StatsResponse(BaseModel):
    """Schema for system statistics response."""
    total_students: int
    total_attendance_records: int
    today_attendance: int
    average_processing_time_ms: float
    match_accuracy: float
    spoof_detection_rate: float
