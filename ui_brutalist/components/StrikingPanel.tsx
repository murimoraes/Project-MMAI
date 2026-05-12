"use client";

import { StrikingTendencies } from "@/lib/types";

interface StrikingPanelProps {
  data: StrikingTendencies;
}

const FREQ_MAP = { low: 20, medium: 55, high: 88 };
const COMBO_MAP = { single: 1, "2-3": 2, "4+": 3 };

export default function StrikingPanel({ data }: StrikingPanelProps) {
  const jabPct = FREQ_MAP[data.jab_frequency];
  const powerPct = data.power_hand_usage;

  return (
    <div className="panel p-4">
      <div className="section-header">STRIKING VECTORS</div>

      <div className="space-y-3">
        <div>
          <div className="flex justify-between items-baseline mb-1">
            <span className="label">jab frequency</span>
            <span className="value-neon uppercase">{data.jab_frequency}</span>
          </div>
          <div className="meter-bar w-full">
            <div className="meter-fill" style={{ width: `${jabPct}%` }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between items-baseline mb-1">
            <span className="label">power hand usage</span>
            <span className="value-neon">{powerPct}%</span>
          </div>
          <div className="meter-bar w-full">
            <div className="meter-fill" style={{ width: `${powerPct}%` }} />
          </div>
        </div>

        <div className="stat-row">
          <span className="label">combination length</span>
          <span className="value uppercase">{data.combination_length} strikes</span>
        </div>

        <div className="pt-2">
          <span className="label block mb-2">entry patterns</span>
          <div className="space-y-1">
            {data.entry_patterns.map((pattern, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="text-dim font-mono">{">"}</span>
                <span className="text-white font-mono text-xs">{pattern}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
