# OCR Text Extraction App

A full-stack Next.js application that extracts text from images using Tesseract.js OCR technology and stores the results in a Supabase database.

## Features

- **Image Upload**: Upload images in various formats (PNG, JPG, GIF)
- **OCR Processing**: Extract text from images using Tesseract.js
- **Confidence Scoring**: View confidence levels for each extraction
- **Database Storage**: Store all extraction results in Supabase
- **Extraction History**: View past OCR results with timestamps
- **Responsive Design**: Modern UI with dark mode support
- **Real-time Updates**: Automatically refresh history after new extractions

## Tech Stack

- **Frontend**: Next.js 14 (App Router), React, TypeScript, Tailwind CSS
- **OCR Engine**: Tesseract.js 5.0
- **Database**: Supabase (PostgreSQL)
- **API**: Next.js API Routes
- **Styling**: Tailwind CSS with dark mode

## Prerequisites

Before you begin, ensure you have:

- Node.js 18+ installed
- A Supabase account ([sign up free](https://supabase.com))
- npm or yarn package manager

## Setup Instructions

### 1. Clone and Install

```bash
cd ocr-app
npm install
```

### 2. Set Up Supabase

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for the database to be ready
3. Go to **Settings** > **API** and copy:
   - Project URL
   - Anon/Public API Key

### 3. Create Database Table

1. In your Supabase dashboard, go to **SQL Editor**
2. Run the SQL script from `database/schema.sql`:

```sql
-- Create OCR Results Table
CREATE TABLE IF NOT EXISTS ocr_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  image_name TEXT NOT NULL,
  extracted_text TEXT NOT NULL,
  confidence DECIMAL(5,2),
  processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index for faster queries
CREATE INDEX IF NOT EXISTS idx_ocr_results_created_at
ON ocr_results(created_at DESC);

-- Enable Row Level Security
ALTER TABLE ocr_results ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Enable read access for all users"
ON ocr_results FOR SELECT
USING (true);

CREATE POLICY "Enable insert access for all users"
ON ocr_results FOR INSERT
WITH CHECK (true);
```

### 4. Configure Environment Variables

Create a `.env.local` file in the root directory:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` and add your Supabase credentials:

```env
NEXT_PUBLIC_SUPABASE_URL=your-supabase-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 5. Run the Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. **Upload an Image**: Click the upload area or drag and drop an image
2. **Extract Text**: Click "Extract Text" to process the image
3. **View Results**: See the extracted text with confidence score
4. **Check History**: View all past extractions in the history panel

## Project Structure

```
ocr-app/
├── app/
│   ├── api/
│   │   └── ocr/
│   │       ├── route.ts          # OCR processing endpoint
│   │       └── history/
│   │           └── route.ts      # History retrieval endpoint
│   ├── globals.css               # Global styles
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Home page
├── components/
│   ├── ImageUpload.tsx           # Image upload component
│   └── OCRHistory.tsx            # History display component
├── database/
│   └── schema.sql                # Database schema
├── lib/
│   └── supabase.ts               # Supabase client configuration
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── README.md
```

## API Endpoints

### POST /api/ocr
Processes an image and extracts text.

**Request**: FormData with `image` file
**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "text": "Extracted text...",
    "confidence": 95.5,
    "imageName": "example.jpg"
  }
}
```

### GET /api/ocr/history
Retrieves the 50 most recent OCR results.

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "image_name": "example.jpg",
      "extracted_text": "Text...",
      "confidence": 95.5,
      "processed_at": "2025-01-01T12:00:00Z",
      "created_at": "2025-01-01T12:00:00Z"
    }
  ]
}
```

## Database Schema

### ocr_results Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| image_name | TEXT | Original filename |
| extracted_text | TEXT | OCR result |
| confidence | DECIMAL | Confidence score (0-100) |
| processed_at | TIMESTAMP | Processing time |
| created_at | TIMESTAMP | Record creation time |

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import your repository in [Vercel](https://vercel.com)
3. Add environment variables in Vercel dashboard
4. Deploy

### Other Platforms

The app can be deployed to any platform supporting Next.js:
- Netlify
- Railway
- AWS Amplify
- Self-hosted

## Troubleshooting

### OCR Not Working
- Ensure the image is clear and text is readable
- Try images with higher resolution
- Check browser console for errors

### Database Connection Issues
- Verify Supabase credentials in `.env.local`
- Check that the database table exists
- Ensure RLS policies are set correctly

### Build Errors
- Delete `node_modules` and `.next` folders
- Run `npm install` again
- Clear npm cache: `npm cache clean --force`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for learning and development.

## Support

For issues or questions, please open an issue on GitHub.

## Acknowledgments

- [Tesseract.js](https://tesseract.projectnaptha.com/) for OCR functionality
- [Supabase](https://supabase.com) for database and backend services
- [Next.js](https://nextjs.org) for the React framework
- [Tailwind CSS](https://tailwindcss.com) for styling
