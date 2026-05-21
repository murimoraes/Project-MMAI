import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Telemetry Fight Lab — MMA Analyzer",
  description: "Combat intelligence platform — fight footage telemetry",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-cb-bg text-cb-text font-sans">
        {children}
      </body>
    </html>
  );
}
