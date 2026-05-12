"use client";

import { MovementPatterns } from "@/lib/types";

interface MovementPanelProps {
  data: MovementPatterns;
}

function PressureMeter({ value }: { value: number }) {
  const pct = value * 100;
  const color = value > 0.7 ? "#ff4444" : value > 0.4 ? "#ccff00" : "#888888";
  return (
    <div>
      <div className="flex justify-between items-baseline mb-1">
        <span className="label">pressure index</span>
        <span className="font-mono font-bold" style={{ color }}>
          {value.toFixed(2)}
        </span>
      </div>
      <div className="meter-bar w-full">
        <div className="h-full transition-all duration-500" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}

const LATERAL_MAP = {
  left: { label: "SOUTH-SOUTH-WEST", indicator: "←" },
  right: { label: "SOUTH-SOUTH-EAST", indicator: "→" },
  balanced: { label: "BALANCED", indicator: "↔" },
};

export default function MovementPanel({ data }: MovementPanelProps) {
  const lateral = LATERAL_MAP[data.lateral_movement_preference];

  return (
    <div className="panel p-4">
      <div className="section-header">MOVEMENT TELEMETRY</div>

      <div className="space-y-3">
        <div className="stat-row">
          <span className="label">footwork</span>
          <span className="value text-xs">{data.footwork_style.toUpperCase()}</span>
        </div>

        <div className="stat-row">
          <span className="label">lateral bias</span>
          <span className="text-neon font-mono font-bold">
            {lateral.indicator} {data.lateral_movement_preference.toUpperCase()}
          </span>
        </div>

        <div className="stat-row">
          <span className="label">distance mgmt</span>
          <span className="value uppercase">{data.distance_management}</span>
        </div>

        <div className="pt-2">
          <PressureMeter value={data.pressure_index} />
        </div>
      </div>
    </div>
  );
}
