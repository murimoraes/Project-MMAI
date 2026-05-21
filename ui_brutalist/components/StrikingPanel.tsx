"use client";

import { StrikingTendencies } from "@/lib/types";

interface StrikingPanelProps {
  data: StrikingTendencies;
}

const FREQ_MAP = { low: 20, medium: 55, high: 88 };
const FREQ_BADGE: Record<string, string> = {
  low: "badge-neutral",
  medium: "badge-blue",
  high: "badge-success",
};
const COMBO_BADGE: Record<string, string> = {
  single: "badge-neutral",
  "2-3": "badge-blue",
  "4+": "badge-warning",
};

export default function StrikingPanel({ data }: StrikingPanelProps) {
  const jabPct = FREQ_MAP[data.jab_frequency];
  const powerPct = data.power_hand_usage;

  return (
    <div className="card p-5">
      <div className="mb-4">
        <p className="section-title mb-0.5">Striking Vectors</p>
      </div>

      <div className="space-y-0">
        <div className="stat-row">
          <span className="data-label">Jab frequency</span>
          <span className={FREQ_BADGE[data.jab_frequency] || "badge-neutral"}>
            {data.jab_frequency}
          </span>
        </div>

        <div className="pt-2 pb-3 border-b border-cb-border">
          <div className="flex items-center justify-between mb-1.5">
            <span className="data-label">Jab rate</span>
            <span className="font-mono text-xs text-cb-muted">{jabPct}%</span>
          </div>
          <div className="meter-track">
            <div className="meter-fill-blue" style={{ width: `${jabPct}%` }} />
          </div>
        </div>

        <div className="pt-2 pb-3 border-b border-cb-border">
          <div className="flex items-center justify-between mb-1.5">
            <span className="data-label">Power hand usage</span>
            <span className="font-mono text-xs text-cb-text font-semibold">{powerPct}%</span>
          </div>
          <div className="meter-track">
            <div className="meter-fill-blue" style={{ width: `${powerPct}%` }} />
          </div>
        </div>

        <div className="stat-row">
          <span className="data-label">Combination length</span>
          <span className={COMBO_BADGE[data.combination_length] || "badge-neutral"}>
            {data.combination_length} strikes
          </span>
        </div>

        <div className="pt-3">
          <p className="data-label mb-2">Entry patterns</p>
          <div className="space-y-1.5">
            {data.entry_patterns.map((pattern, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className="text-cb-blue font-mono text-xs mt-0.5">›</span>
                <span className="text-xs text-cb-text leading-relaxed">{pattern}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
