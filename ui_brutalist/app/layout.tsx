import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TELEMETRY FIGHT LAB // MMA ANALYZER",
  description: "Combat intelligence platform — fight footage telemetry",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-asphalt text-white font-mono">
        {children}
      </body>
    </html>
  );
}
