"use client";

import { ThreatAssessment } from "@/lib/types";

interface ThreatPanelProps {
  data: ThreatAssessment;
  fighter: string;
}

export default function ThreatPanel({ data, fighter }: ThreatPanelProps) {
  const level = data.overall_threat_level;
  const threatBadge =
    level >= 8 ? "badge-danger" : level >= 6 ? "badge-warning" : level >= 4 ? "badge-blue" : "badge-neutral";
  const threatLabel =
    level >= 8 ? "Critical" : level >= 6 ? "High" : level >= 4 ? "Moderate" : "Low";

  const pips = Array.from({ length: 10 });

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <p className="section-title">Threat Assessment</p>
        <span className={threatBadge}>{threatLabel}</span>
      </div>

      <div className="flex items-end gap-4 mb-4">
        <div>
          <p className="data-label mb-1">Threat level</p>
          <p className="text-4xl font-bold text-cb-text">
            {level}
            <span className="text-lg font-normal text-cb-muted">/10</span>
          </p>
        </div>

        <div className="flex gap-1 pb-1">
          {pips.map((_, i) => {
            const active = i < level;
            const color =
              i >= 7 ? "#DA3633" : i >= 5 ? "#F5A623" : "#0052FF";
            return (
              <div
                key={i}
                className="w-3 h-5 rounded-sm transition-all duration-300"
                style={{
                  backgroundColor: active ? color : "rgba(255,255,255,0.06)",
                  opacity: active ? 1 : 1,
                }}
              />
            );
          })}
        </div>
      </div>

      <div className="space-y-0">
        <div className="stat-row">
          <span className="data-label">Primary weapon</span>
          <span className="text-xs font-medium text-cb-text max-w-[55%] text-right">{data.primary_weapon}</span>
        </div>
        <div className="pt-3">
          <p className="data-label mb-1.5">Danger zone</p>
          <p className="text-xs text-cb-danger leading-relaxed">{data.danger_zone}</p>
        </div>
      </div>
    </div>
  );
}
