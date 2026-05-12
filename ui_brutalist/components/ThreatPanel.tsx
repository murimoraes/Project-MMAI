"use client";

import { ThreatAssessment } from "@/lib/types";

interface ThreatPanelProps {
  data: ThreatAssessment;
  fighter: string;
}

export default function ThreatPanel({ data, fighter }: ThreatPanelProps) {
  const level = data.overall_threat_level;
  const threatColor =
    level >= 8 ? "#ff4444" : level >= 6 ? "#ffcc00" : level >= 4 ? "#ccff00" : "#888888";

  return (
    <div className="panel p-4">
      <div className="section-header">THREAT ASSESSMENT</div>

      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="label block">threat level</span>
          <span className="font-display font-black text-4xl" style={{ color: threatColor }}>
            {level}
            <span className="text-dim text-lg font-mono font-normal">/10</span>
          </span>
        </div>
        <div className="grid grid-cols-5 gap-1">
          {Array.from({ length: 10 }).map((_, i) => (
            <div
              key={i}
              className="w-4 h-6 border border-dim"
              style={{
                backgroundColor: i < level ? threatColor : "transparent",
                opacity: i < level ? 1 : 0.3,
              }}
            />
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <span className="label block mb-1">primary weapon</span>
          <span className="text-white font-mono text-xs">{data.primary_weapon}</span>
        </div>

        <div className="border-t border-dim pt-3">
          <span className="label block mb-1">danger zone</span>
          <span className="text-red-400 font-mono text-xs">{data.danger_zone}</span>
        </div>
      </div>
    </div>
  );
}
