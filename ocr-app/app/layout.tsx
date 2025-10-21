import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OCR Text Extraction App",
  description: "Extract text from images using OCR and store in database",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
