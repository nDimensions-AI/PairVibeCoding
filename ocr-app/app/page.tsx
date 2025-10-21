'use client';

import { useState, useEffect } from 'react';
import ImageUpload from '@/components/ImageUpload';
import OCRHistory from '@/components/OCRHistory';
import type { OCRResult } from '@/lib/supabase';

export default function Home() {
  const [history, setHistory] = useState<OCRResult[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchHistory = async () => {
    try {
      const response = await fetch('/api/ocr/history');
      const result = await response.json();
      if (result.success) {
        setHistory(result.data);
      }
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleUploadSuccess = () => {
    fetchHistory();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            OCR Text Extraction
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Upload an image to extract text using advanced OCR technology
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <ImageUpload onSuccess={handleUploadSuccess} />
          </div>

          <div>
            <OCRHistory history={history} loading={loading} />
          </div>
        </div>
      </div>
    </div>
  );
}
