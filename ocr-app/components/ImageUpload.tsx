'use client';

import { useState, useRef } from 'react';

interface ImageUploadProps {
  onSuccess: () => void;
}

interface OCRResponse {
  success: boolean;
  data?: {
    id: string;
    text: string;
    confidence: number;
    imageName: string;
  };
  error?: string;
}

export default function ImageUpload({ onSuccess }: ImageUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OCRResponse['data'] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);

      const response = await fetch('/api/ocr', {
        method: 'POST',
        body: formData,
      });

      const data: OCRResponse = await response.json();

      if (data.success && data.data) {
        setResult(data.data);
        onSuccess();
      } else {
        setError(data.error || 'Failed to process image');
      }
    } catch (err) {
      setError('An error occurred while processing the image');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800 dark:text-white">
        Upload Image
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer inline-flex flex-col items-center"
          >
            <svg
              className="w-12 h-12 text-gray-400 mb-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <span className="text-sm text-gray-600 dark:text-gray-300">
              Click to upload or drag and drop
            </span>
            <span className="text-xs text-gray-500 mt-1">
              PNG, JPG, GIF up to 10MB
            </span>
          </label>
        </div>

        {preview && (
          <div className="mt-4">
            <img
              src={preview}
              alt="Preview"
              className="max-h-64 mx-auto rounded-lg shadow-md"
            />
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-2 text-center">
              {selectedFile?.name}
            </p>
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={!selectedFile || loading}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
          >
            {loading ? 'Processing...' : 'Extract Text'}
          </button>
          {selectedFile && (
            <button
              type="button"
              onClick={handleReset}
              className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
            >
              Reset
            </button>
          )}
        </div>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-200 rounded-lg">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-6 p-4 bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-lg">
          <h3 className="font-semibold text-green-800 dark:text-green-200 mb-2">
            Extraction Successful!
          </h3>
          <div className="text-sm text-green-700 dark:text-green-300 mb-3">
            Confidence: {result.confidence.toFixed(2)}%
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded border border-green-200 dark:border-green-700">
            <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
              {result.text}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
