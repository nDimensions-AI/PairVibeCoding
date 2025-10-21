'use client';

import { OCRResult } from '@/lib/supabase';

interface OCRHistoryProps {
  history: OCRResult[];
  loading: boolean;
}

export default function OCRHistory({ history, loading }: OCRHistoryProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800 dark:text-white">
        Extraction History
      </h2>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 dark:text-gray-300 mt-4">Loading...</p>
        </div>
      ) : history.length === 0 ? (
        <div className="text-center py-8">
          <svg
            className="w-16 h-16 text-gray-300 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p className="text-gray-500 dark:text-gray-400">
            No extraction history yet
          </p>
          <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
            Upload an image to get started
          </p>
        </div>
      ) : (
        <div className="space-y-4 max-h-[600px] overflow-y-auto">
          {history.map((item) => (
            <div
              key={item.id}
              className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-gray-800 dark:text-white truncate flex-1">
                  {item.image_name}
                </h3>
                {item.confidence && (
                  <span className="text-sm text-blue-600 dark:text-blue-400 ml-2 flex-shrink-0">
                    {item.confidence.toFixed(1)}%
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                {formatDate(item.created_at)}
              </p>
              <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded border border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap line-clamp-4">
                  {item.extracted_text}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
