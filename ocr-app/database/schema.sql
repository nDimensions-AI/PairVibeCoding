-- Create OCR Results Table
-- Run this SQL in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS ocr_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  image_name TEXT NOT NULL,
  extracted_text TEXT NOT NULL,
  confidence DECIMAL(5,2),
  processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index for faster queries by date
CREATE INDEX IF NOT EXISTS idx_ocr_results_created_at
ON ocr_results(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE ocr_results ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows anyone to read and insert
-- Adjust this based on your authentication requirements
CREATE POLICY "Enable read access for all users"
ON ocr_results FOR SELECT
USING (true);

CREATE POLICY "Enable insert access for all users"
ON ocr_results FOR INSERT
WITH CHECK (true);
