"use client";

import { MovementPatterns } from "@/lib/types";

interface MovementPanelProps {
  data: MovementPatterns;
}

const LATERAL_MAP = {
  left: { label: "Left-biased", icon: "←" },
  right: { label: "Right-biased", icon: "→" },
  balanced: { label: "Balanced", icon: "↔" },
};

const DISTANCE_BADGE: Record<string, string> = {
  "clinch-seeker": "badge-warning",
  "mid-range": "badge-blue",
  boxer: "badge-success",
};

export default function MovementPanel({ data }: MovementPanelProps) {
  const lateral = LATERAL_MAP[data.lateral_movement_preference];
  const pressurePct = data.pressure_index * 100;
  const pressureFill =
    data.pressure_index > 0.7 ? "meter-fill-danger" : data.pressure_index > 0.4 ? "meter-fill-warning" : "meter-fill-blue";

  return (
    <div className="card p-5">
      <div className="mb-4">
        <p className="section-title mb-0.5">Movement Telemetry</p>
      </div>

      <div className="space-y-0">
        <div className="stat-row">
          <span className="data-label">Footwork</span>
          <span className="data-value text-xs">{data.footwork_style}</span>
        </div>

        <div className="stat-row">
          <span className="data-label">Lateral bias</span>
          <span className="text-sm font-semibold text-cb-text">
            {lateral.icon} {lateral.label}
          </span>
        </div>

        <div className="stat-row">
          <span className="data-label">Distance management</span>
          <span className={DISTANCE_BADGE[data.distance_management] || "badge-neutral"}>
            {data.distance_management}
          </span>
        </div>

        <div className="pt-3">
          <div className="flex items-center justify-between mb-1.5">
            <span className="data-label">Pressure index</span>
            <span className="font-mono text-xs font-semibold text-cb-text">
              {data.pressure_index.toFixed(2)}
            </span>
          </div>
          <div className="meter-track w-full">
            <div className={pressureFill} style={{ width: `${pressurePct}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
}
