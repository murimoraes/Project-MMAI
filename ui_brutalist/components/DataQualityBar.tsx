"use client";

interface DataQualityBarProps {
  detectionRate: number;
  totalFrames: number;
  durationSeconds: number;
  fighter: string;
}

export default function DataQualityBar({
  detectionRate,
  totalFrames,
  durationSeconds,
  fighter,
}: DataQualityBarProps) {
  const quality =
    detectionRate >= 80 ? "High" : detectionRate >= 60 ? "Moderate" : "Low";
  const qualityClass =
    detectionRate >= 80 ? "badge-success" : detectionRate >= 60 ? "badge-warning" : "badge-danger";
  const fillClass =
    detectionRate >= 80 ? "meter-fill-success" : detectionRate >= 60 ? "meter-fill-warning" : "meter-fill-danger";

  const minutes = Math.floor(durationSeconds / 60);
  const seconds = Math.round(durationSeconds % 60);

  return (
    <div className="card px-5 py-3 flex flex-wrap items-center gap-5">
      <div className="flex items-center gap-2">
        <span className="data-label">Dataset</span>
        <span className="text-sm font-semibold text-cb-text">{fighter}</span>
      </div>

      <div className="flex items-center gap-2">
        <span className="data-label">Detection</span>
        <span className={qualityClass}>{quality} — {detectionRate.toFixed(1)}%</span>
      </div>

      <div className="flex items-center gap-2">
        <span className="data-label">Frames</span>
        <span className="font-mono text-xs text-cb-text">{totalFrames.toLocaleString()}</span>
      </div>

      <div className="flex items-center gap-2">
        <span className="data-label">Duration</span>
        <span className="font-mono text-xs text-cb-text">{minutes}m {seconds}s</span>
      </div>

      <div className="flex-1 hidden lg:block min-w-[120px]">
        <div className="meter-track">
          <div className={fillClass} style={{ width: `${detectionRate}%` }} />
        </div>
      </div>
    </div>
  );
}
