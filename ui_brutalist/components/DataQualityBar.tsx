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
  const qualityColor =
    detectionRate >= 80 ? "#ccff00" : detectionRate >= 60 ? "#ffcc00" : "#ff4444";
  const qualityLabel =
    detectionRate >= 80 ? "HIGH" : detectionRate >= 60 ? "MODERATE" : "LOW";

  return (
    <div className="border border-dim bg-steel px-4 py-2 flex flex-wrap items-center gap-6">
      <div className="flex items-center gap-2">
        <span className="label">dataset</span>
        <span className="text-white font-mono text-xs font-bold uppercase">{fighter}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="label">detection</span>
        <span className="font-mono font-bold text-xs" style={{ color: qualityColor }}>
          {qualityLabel} {detectionRate.toFixed(1)}%
        </span>
      </div>
      <div className="flex items-center gap-2">
        <span className="label">frames</span>
        <span className="text-white font-mono text-xs">{totalFrames.toLocaleString()}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="label">duration</span>
        <span className="text-white font-mono text-xs">
          {Math.floor(durationSeconds / 60)}m {Math.round(durationSeconds % 60)}s
        </span>
      </div>
      <div className="flex-1 hidden lg:block">
        <div className="meter-bar">
          <div
            className="h-full transition-all duration-500"
            style={{ width: `${detectionRate}%`, backgroundColor: qualityColor }}
          />
        </div>
      </div>
    </div>
  );
}
