"use client";

import { GuardSignature } from "@/lib/types";

interface GuardPanelProps {
  data: GuardSignature;
  fighter: string;
}

const STANCE_COLOR = {
  orthodox: "text-white",
  southpaw: "text-neon",
  switch: "text-yellow-400",
};

const ACTIVITY_COLOR = {
  passive: "text-ghost",
  active: "text-white",
  hyperactive: "text-neon",
};

function Meter({ value, max = 1 }: { value: number; max?: number }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="meter-bar w-full mt-1">
      <div className="meter-fill" style={{ width: `${pct}%` }} />
    </div>
  );
}

export default function GuardPanel({ data, fighter }: GuardPanelProps) {
  const chinRisk = data.chin_exposure_index > 0.5 ? "CRITICAL" : data.chin_exposure_index > 0.3 ? "MODERATE" : "LOW";
  const chinColor = chinRisk === "CRITICAL" ? "text-red-400" : chinRisk === "MODERATE" ? "text-yellow-400" : "text-neon";

  return (
    <div className="panel p-4">
      <div className="section-header">GUARD SIGNATURE // {fighter.toUpperCase()}</div>

      <div className="space-y-3">
        <div className="stat-row">
          <span className="label">stance</span>
          <span className={`font-mono font-bold uppercase text-sm ${STANCE_COLOR[data.dominant_stance]}`}>
            {data.dominant_stance}
          </span>
        </div>

        <div className="stat-row">
          <span className="label">guard height</span>
          <span className="value uppercase">{data.guard_height}</span>
        </div>

        <div className="stat-row">
          <span className="label">lead hand</span>
          <span className={`font-mono font-bold uppercase text-sm ${ACTIVITY_COLOR[data.lead_hand_activity]}`}>
            {data.lead_hand_activity}
          </span>
        </div>

        <div className="stat-row">
          <span className="label">rear hand</span>
          <span className={`value uppercase ${data.rear_hand_position === "dropped" ? "text-red-400" : "text-white"}`}>
            {data.rear_hand_position}
          </span>
        </div>

        <div className="pt-2">
          <div className="flex justify-between items-baseline mb-1">
            <span className="label">chin exposure</span>
            <span className={`font-mono font-bold text-xs ${chinColor}`}>
              {chinRisk} [{data.chin_exposure_index.toFixed(2)}]
            </span>
          </div>
          <Meter value={data.chin_exposure_index} />
        </div>
      </div>
    </div>
  );
}
