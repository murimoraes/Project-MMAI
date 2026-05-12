import { NextResponse } from "next/server";
import { readdir, readFile } from "fs/promises";
import path from "path";

const REPORTS_DIR = path.join(process.cwd(), "..", "data_processed", "reports");

export async function GET() {
  try {
    const files = await readdir(REPORTS_DIR);
    const jsonFiles = files.filter((f) => f.endsWith(".json"));

    const reports: Record<string, unknown> = {};

    for (const file of jsonFiles) {
      const content = await readFile(path.join(REPORTS_DIR, file), "utf-8");
      const key = file.replace(".json", "");
      reports[key] = JSON.parse(content);
    }

    return NextResponse.json({ reports, count: jsonFiles.length });
  } catch {
    return NextResponse.json(
      { reports: {}, count: 0, note: "No reports generated yet. Run brain/pattern_recognition.py first." },
      { status: 200 }
    );
  }
}
