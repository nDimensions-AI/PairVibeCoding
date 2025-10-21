import { NextRequest, NextResponse } from 'next/server';
import { createWorker } from 'tesseract.js';
import { supabase } from '@/lib/supabase';
import { v4 as uuidv4 } from 'uuid';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('image') as File;

    if (!file) {
      return NextResponse.json(
        { error: 'No image file provided' },
        { status: 400 }
      );
    }

    // Convert file to buffer for Tesseract
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Initialize Tesseract worker
    const worker = await createWorker('eng');

    // Perform OCR
    const { data } = await worker.recognize(buffer);

    // Extract text and confidence
    const extractedText = data.text;
    const confidence = data.confidence;

    // Terminate worker
    await worker.terminate();

    // Save to database
    const { data: dbData, error: dbError } = await supabase
      .from('ocr_results')
      .insert([
        {
          id: uuidv4(),
          image_name: file.name,
          extracted_text: extractedText,
          confidence: confidence,
          processed_at: new Date().toISOString(),
        },
      ])
      .select()
      .single();

    if (dbError) {
      console.error('Database error:', dbError);
      return NextResponse.json(
        { error: 'Failed to save to database', details: dbError.message },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      data: {
        id: dbData.id,
        text: extractedText,
        confidence: confidence,
        imageName: file.name,
      },
    });
  } catch (error) {
    console.error('OCR processing error:', error);
    return NextResponse.json(
      { error: 'Failed to process image', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
