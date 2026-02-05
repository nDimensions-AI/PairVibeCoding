# Face Attendance System

A high-speed, high-accuracy proof-of-concept (POC) mobile application for marking attendance using Computer Vision. Designed for 5,000+ students with sub-second processing times.

## Features

### Core Functionality

- **User Registration (Enrollment)**
  - Capture high-quality "Master Selfie"
  - Generate 512-D Face Vector (Embedding) using InsightFace (ArcFace)
  - Store vectors in database with pgvector for efficient similarity search

- **Attendance Marking (Verification)**
  - Real-time face detection via MediaPipe
  - Passive liveness detection (anti-spoofing)
  - Vector comparison using Cosine Similarity
  - GPS location and device logging

- **Reporting**
  - Success/Failure logging with timestamps
  - Daily attendance summaries
  - Student attendance history
  - Performance analytics

### Anti-Spoofing Measures

The system implements multiple passive liveness detection techniques:

1. **Texture Analysis (LBP)** - Detects printed photos
2. **Color Analysis** - Detects screen replay attacks
3. **Reflection Analysis** - Detects glossy surfaces
4. **Frequency Analysis** - Detects moire patterns from screens
5. **Sharpness Analysis** - Detects artificial enhancement

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit (Demo) / Flutter (Mobile) |
| Backend | FastAPI (Python) |
| Face Detection | Google MediaPipe |
| Face Embedding | InsightFace (ArcFace) |
| Vector Search | pgvector on Supabase |
| Database | PostgreSQL (Supabase) |

## Performance Benchmarks

| Metric | Target | Description |
|--------|--------|-------------|
| Match Accuracy | >99.5% | Minimize false positives |
| Processing Time | <1.5s | Camera scan to result |
| Search Time | <10ms | Vector search across 5,000 identities |
| Embedding Size | 512-D | ArcFace standard |

## Project Structure

```
face-attendance/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic models
│   │   ├── services/
│   │   │   ├── face_detection.py    # MediaPipe face detection
│   │   │   ├── face_embedding.py    # InsightFace/ArcFace
│   │   │   ├── liveness.py          # Anti-spoofing
│   │   │   └── database.py          # Supabase operations
│   │   └── routers/
│   │       ├── registration.py      # Student enrollment
│   │       ├── attendance.py        # Attendance marking
│   │       └── reports.py           # Reporting endpoints
│   ├── config.py
│   └── requirements.txt
├── frontend/
│   ├── app.py                   # Streamlit application
│   └── requirements.txt
├── database/
│   └── schema.sql               # PostgreSQL + pgvector schema
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- Supabase account (or use in-memory demo mode)

### 1. Clone and Setup

```bash
cd face-attendance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
pip install -r frontend/requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 3. Setup Database (Supabase)

1. Create a new Supabase project
2. Enable the pgvector extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Run the schema from `database/schema.sql` in the SQL editor

### 4. Run the Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 5. Run the Frontend

```bash
cd frontend
streamlit run app.py
```

The demo UI will be available at `http://localhost:8501`

## API Endpoints

### Registration

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/register` | Register new student with face |
| PUT | `/api/v1/register/{student_id}` | Update student's face |
| GET | `/api/v1/register/{student_id}` | Get student details |
| DELETE | `/api/v1/register/{student_id}` | Delete student |
| GET | `/api/v1/students` | List all students |
| POST | `/api/v1/validate-face` | Validate face image |

### Attendance

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/attendance` | Mark attendance (1:N matching) |
| POST | `/api/v1/attendance/verify` | Verify specific student (1:1) |
| GET | `/api/v1/attendance/today` | Today's attendance |
| GET | `/api/v1/attendance/history` | Attendance history |

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/reports/attendance` | Attendance report with filters |
| GET | `/api/v1/reports/stats` | System statistics |
| GET | `/api/v1/reports/daily-summary` | Daily attendance summary |
| GET | `/api/v1/reports/student/{id}` | Individual student report |
| POST | `/api/v1/reports/demo-data` | Generate demo students |

## API Usage Examples

### Register a Student

```bash
curl -X POST "http://localhost:8000/api/v1/register" \
  -F "student_id=STU001" \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "department=Computer Science" \
  -F "image=@photo.jpg"
```

### Mark Attendance

```bash
curl -X POST "http://localhost:8000/api/v1/attendance" \
  -F "image=@face.jpg" \
  -F "latitude=37.7749" \
  -F "longitude=-122.4194"
```

### Response Example

```json
{
  "status": "success",
  "student_id": "STU001",
  "student_name": "John Doe",
  "timestamp": "2024-01-15T10:30:00Z",
  "message": "Attendance marked successfully! Welcome, John Doe.",
  "face_detection": {
    "face_detected": true,
    "num_faces": 1,
    "detection_confidence": 0.98,
    "face_quality": 0.85
  },
  "liveness": {
    "is_live": true,
    "confidence": 0.92,
    "checks_passed": ["texture", "color", "reflection", "frequency", "sharpness"]
  },
  "match": {
    "matched": true,
    "student_id": "STU001",
    "similarity_score": 0.87,
    "search_time_ms": 5.2
  },
  "processing_time_ms": 1245.8
}
```

## Demo Mode

The system can run without Supabase using in-memory storage:

1. Leave `SUPABASE_URL` and `SUPABASE_KEY` empty in `.env`
2. Generate demo students: `POST /api/v1/reports/demo-data?count=1000`
3. Test the system with the Streamlit UI

## Security Considerations

### Success Criteria

1. **Identity Lock**: A person cannot mark attendance for another person
2. **Anti-Spoof**: Laptop photos of a person are rejected
3. **Scale**: Instant matching even with 5,000+ records

### Threshold Tuning

- **Face Recognition Threshold** (default: 0.45)
  - Higher = stricter, fewer false positives, more false negatives
  - Lower = lenient, more false positives, fewer false negatives

- **Liveness Threshold** (default: 0.5)
  - Higher = stricter anti-spoofing
  - Lower = more permissive

## Extending for Mobile (Flutter)

The backend is designed to work with any frontend. For Flutter:

1. Use `http` or `dio` package for API calls
2. Use `camera` package for image capture
3. Use `geolocator` for GPS
4. Convert images to bytes and send as multipart form data

Example Flutter code:

```dart
import 'package:dio/dio.dart';

Future<void> markAttendance(File image) async {
  final dio = Dio();
  final formData = FormData.fromMap({
    'image': await MultipartFile.fromFile(image.path),
    'latitude': position.latitude,
    'longitude': position.longitude,
  });

  final response = await dio.post(
    'http://your-api/api/v1/attendance',
    data: formData,
  );

  // Handle response
}
```

## Troubleshooting

### InsightFace Model Download

On first run, InsightFace downloads model files (~500MB). Ensure:
- Stable internet connection
- Sufficient disk space
- Write permissions in the working directory

### Memory Issues

For systems with limited RAM:
- Use `buffalo_s` model instead of `buffalo_l`
- Reduce image size before processing
- Process one image at a time

### GPU Acceleration

For faster processing on GPU:
```bash
pip install onnxruntime-gpu
```

Then configure providers in `face_embedding.py`:
```python
providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
```

## License

This project is for educational and demonstration purposes.

## Acknowledgments

- [InsightFace](https://github.com/deepinsight/insightface) for face recognition
- [MediaPipe](https://mediapipe.dev/) for face detection
- [Supabase](https://supabase.com/) for database and pgvector
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Streamlit](https://streamlit.io/) for the demo UI
