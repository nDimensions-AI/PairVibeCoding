"""
Reports Router - Attendance Reporting API.

Provides endpoints for generating attendance reports and statistics.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Query

from app.models.schemas import AttendanceReportResponse, StatsResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def get_services():
    """Get service instances from main app."""
    from app.main import get_service
    return {
        "database": get_service("database")
    }


@router.get("/reports/attendance")
async def get_attendance_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    student_id: Optional[str] = Query(None, description="Filter by student ID"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Generate an attendance report with optional filters.

    Returns attendance records with summary statistics.
    """
    services = get_services()
    db = services["database"]

    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    # Get records
    records = await db.get_attendance_records(
        student_id=student_id,
        start_date=start_dt,
        end_date=end_dt,
        status=status,
        limit=limit,
        offset=offset
    )

    # Calculate statistics
    total = len(records)
    success_count = sum(1 for r in records if r["status"] == "success")
    spoof_count = sum(1 for r in records if r["status"] == "spoof_detected")

    return {
        "total_records": total,
        "records": records,
        "success_rate": success_count / total if total > 0 else 0.0,
        "spoof_attempts": spoof_count,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "filters": {
            "student_id": student_id,
            "department": department,
            "status": status
        }
    }


@router.get("/reports/stats")
async def get_system_stats():
    """
    Get overall system statistics.

    Returns metrics like total students, attendance counts, and performance stats.
    """
    services = get_services()
    db = services["database"]

    # Get counts
    total_students = await db.get_student_count()
    attendance_stats = await db.get_attendance_stats()
    today_records = await db.get_today_attendance()

    return {
        "total_students": total_students,
        "total_attendance_records": attendance_stats["total_records"],
        "today_attendance": len(today_records),
        "today_unique_students": len(set(r["student_id"] for r in today_records if r["student_id"] != "unknown")),
        "success_rate": attendance_stats["success_rate"],
        "spoof_detection_count": attendance_stats["spoof_count"],
        "average_processing_time_ms": attendance_stats["average_processing_time_ms"]
    }


@router.get("/reports/daily-summary")
async def get_daily_summary(
    days: int = Query(7, ge=1, le=30, description="Number of days to include")
):
    """
    Get daily attendance summary for the past N days.
    """
    services = get_services()
    db = services["database"]

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    records = await db.get_attendance_records(
        start_date=start_date,
        end_date=end_date,
        limit=10000
    )

    # Group by date
    daily_stats = {}
    for record in records:
        date = record["timestamp"][:10]  # Extract date part
        if date not in daily_stats:
            daily_stats[date] = {
                "date": date,
                "total": 0,
                "success": 0,
                "failed": 0,
                "spoof": 0,
                "unique_students": set()
            }
        daily_stats[date]["total"] += 1
        if record["status"] == "success":
            daily_stats[date]["success"] += 1
            if record["student_id"]:
                daily_stats[date]["unique_students"].add(record["student_id"])
        elif record["status"] == "spoof_detected":
            daily_stats[date]["spoof"] += 1
        else:
            daily_stats[date]["failed"] += 1

    # Convert to list and clean up
    summary = []
    for date in sorted(daily_stats.keys(), reverse=True):
        stats = daily_stats[date]
        summary.append({
            "date": stats["date"],
            "total_attempts": stats["total"],
            "successful": stats["success"],
            "failed": stats["failed"],
            "spoof_attempts": stats["spoof"],
            "unique_students": len(stats["unique_students"]),
            "success_rate": stats["success"] / stats["total"] if stats["total"] > 0 else 0.0
        })

    return {
        "period": {
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "days": days
        },
        "summary": summary
    }


@router.get("/reports/student/{student_id}")
async def get_student_report(student_id: str):
    """
    Get attendance report for a specific student.
    """
    services = get_services()
    db = services["database"]

    # Get student info
    student = await db.get_student(student_id)
    if not student:
        return {"error": f"Student '{student_id}' not found."}

    # Get attendance records
    records = await db.get_attendance_records(
        student_id=student_id,
        limit=1000
    )

    # Calculate stats
    total = len(records)
    successful = sum(1 for r in records if r["status"] == "success")

    # Get date range
    if records:
        first_attendance = min(r["timestamp"] for r in records)
        last_attendance = max(r["timestamp"] for r in records)
    else:
        first_attendance = None
        last_attendance = None

    return {
        "student": student,
        "attendance_summary": {
            "total_attempts": total,
            "successful": successful,
            "success_rate": successful / total if total > 0 else 0.0,
            "first_attendance": first_attendance,
            "last_attendance": last_attendance
        },
        "recent_records": records[:50]  # Last 50 records
    }


@router.post("/reports/demo-data")
async def generate_demo_data(count: int = Query(100, ge=1, le=5000)):
    """
    Generate demo student records for testing.

    This creates fake students with random embeddings to test
    the system's performance with large datasets.
    """
    services = get_services()
    db = services["database"]

    created = await db.generate_demo_data(count)

    total_students = await db.get_student_count()

    return {
        "status": "success",
        "created": created,
        "total_students": total_students,
        "message": f"Generated {created} demo students. Total: {total_students}"
    }
