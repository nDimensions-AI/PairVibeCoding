-- Face Attendance System - Database Schema
-- For Supabase PostgreSQL with pgvector extension

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ==================== Students Table ====================
-- Stores student information
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    department VARCHAR(100),
    face_quality DECIMAL(5, 4) DEFAULT 0,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id);
CREATE INDEX IF NOT EXISTS idx_students_department ON students(department);
CREATE INDEX IF NOT EXISTS idx_students_is_active ON students(is_active);

-- ==================== Face Embeddings Table ====================
-- Stores 512-dimensional face embeddings with pgvector
CREATE TABLE IF NOT EXISTS face_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id VARCHAR(50) UNIQUE NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    embedding vector(512) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create IVFFlat index for fast approximate nearest neighbor search
-- Optimized for 5,000+ vectors with <10ms search time
CREATE INDEX IF NOT EXISTS idx_face_embeddings_vector ON face_embeddings
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ==================== Attendance Records Table ====================
-- Logs all attendance attempts (success and failure)
CREATE TABLE IF NOT EXISTS attendance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id VARCHAR(50),
    student_name VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) NOT NULL CHECK (status IN (
        'success',
        'failure',
        'spoof_detected',
        'no_face_detected',
        'multiple_faces',
        'no_match'
    )),
    similarity_score DECIMAL(5, 4) DEFAULT 0,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    device_id VARCHAR(100),
    processing_time_ms DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for attendance queries
CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON attendance_records(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_timestamp ON attendance_records(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance_records(status);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance_records(DATE(timestamp));

-- ==================== Vector Similarity Search Function ====================
-- Function to find matching face embeddings using cosine similarity
CREATE OR REPLACE FUNCTION match_face_embedding(
    query_embedding vector(512),
    match_threshold FLOAT DEFAULT 0.55,  -- Cosine distance threshold (1 - similarity)
    match_count INT DEFAULT 1
)
RETURNS TABLE (
    student_id VARCHAR(50),
    distance FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        fe.student_id,
        (fe.embedding <=> query_embedding)::FLOAT as distance
    FROM face_embeddings fe
    JOIN students s ON fe.student_id = s.student_id
    WHERE s.is_active = TRUE
    AND (fe.embedding <=> query_embedding) < match_threshold
    ORDER BY fe.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ==================== Row Level Security (RLS) ====================
-- Enable RLS on all tables
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE face_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_records ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (adjust for production)
-- Students table policies
CREATE POLICY "Allow public read access to students" ON students
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert to students" ON students
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update to students" ON students
    FOR UPDATE USING (true);

CREATE POLICY "Allow public delete from students" ON students
    FOR DELETE USING (true);

-- Face embeddings table policies
CREATE POLICY "Allow public read access to face_embeddings" ON face_embeddings
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert to face_embeddings" ON face_embeddings
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update to face_embeddings" ON face_embeddings
    FOR UPDATE USING (true);

CREATE POLICY "Allow public delete from face_embeddings" ON face_embeddings
    FOR DELETE USING (true);

-- Attendance records table policies
CREATE POLICY "Allow public read access to attendance_records" ON attendance_records
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert to attendance_records" ON attendance_records
    FOR INSERT WITH CHECK (true);

-- ==================== Helper Views ====================
-- View for daily attendance summary
CREATE OR REPLACE VIEW daily_attendance_summary AS
SELECT
    DATE(timestamp) as date,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN status = 'spoof_detected' THEN 1 ELSE 0 END) as spoof_attempts,
    SUM(CASE WHEN status IN ('failure', 'no_match') THEN 1 ELSE 0 END) as failed,
    AVG(processing_time_ms) as avg_processing_time_ms,
    AVG(CASE WHEN status = 'success' THEN similarity_score ELSE NULL END) as avg_match_score
FROM attendance_records
GROUP BY DATE(timestamp)
ORDER BY DATE(timestamp) DESC;

-- View for student attendance summary
CREATE OR REPLACE VIEW student_attendance_summary AS
SELECT
    s.student_id,
    s.name,
    s.department,
    COUNT(ar.id) as total_attendance,
    SUM(CASE WHEN ar.status = 'success' THEN 1 ELSE 0 END) as successful_attendance,
    MAX(ar.timestamp) as last_attendance,
    AVG(ar.similarity_score) as avg_match_score
FROM students s
LEFT JOIN attendance_records ar ON s.student_id = ar.student_id
GROUP BY s.student_id, s.name, s.department;

-- ==================== Triggers ====================
-- Trigger to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_students_updated_at
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_face_embeddings_updated_at
    BEFORE UPDATE ON face_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ==================== Sample Queries ====================
-- Find matching face (for reference, not executed)
-- SELECT * FROM match_face_embedding(
--     '[0.1, 0.2, ...]'::vector(512),  -- 512-D embedding
--     0.55,  -- Distance threshold (1 - 0.45 similarity)
--     1      -- Return top 1 match
-- );

-- Get today's attendance
-- SELECT * FROM attendance_records
-- WHERE DATE(timestamp) = CURRENT_DATE
-- ORDER BY timestamp DESC;

-- Get attendance rate by department
-- SELECT
--     s.department,
--     COUNT(DISTINCT ar.student_id) as attended_today,
--     COUNT(DISTINCT s.student_id) as total_students
-- FROM students s
-- LEFT JOIN attendance_records ar
--     ON s.student_id = ar.student_id
--     AND DATE(ar.timestamp) = CURRENT_DATE
-- GROUP BY s.department;
