"use client";

import { GuardSignature } from "@/lib/types";

interface GuardPanelProps {
  data: GuardSignature;
  fighter: string;
}

const STANCE_BADGE: Record<string, string> = {
  orthodox: "badge-blue",
  southpaw: "badge-warning",
  switch: "badge-neutral",
};

const ACTIVITY_BADGE: Record<string, string> = {
  passive: "badge-neutral",
  active: "badge-blue",
  hyperactive: "badge-success",
};

const REAR_BADGE: Record<string, string> = {
  tight: "badge-success",
  extended: "badge-warning",
  dropped: "badge-danger",
};

function Meter({ value, max = 1 }: { value: number; max?: number }) {
  const pct = Math.min((value / max) * 100, 100);
  const fillClass =
    pct >= 70 ? "meter-fill-danger" : pct >= 40 ? "meter-fill-warning" : "meter-fill-success";
  return (
    <div className="meter-track w-full mt-1.5">
      <div className={fillClass} style={{ width: `${pct}%` }} />
    </div>
  );
}

export default function GuardPanel({ data, fighter }: GuardPanelProps) {
  const chinRisk =
    data.chin_exposure_index > 0.5 ? "Critical" : data.chin_exposure_index > 0.3 ? "Moderate" : "Low";
  const chinBadge =
    chinRisk === "Critical" ? "badge-danger" : chinRisk === "Moderate" ? "badge-warning" : "badge-success";

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="section-title mb-0.5">Guard Signature</p>
          <p className="text-xs text-cb-muted">{fighter}</p>
        </div>
        <span className={STANCE_BADGE[data.dominant_stance] || "badge-neutral"}>
          {data.dominant_stance}
        </span>
      </div>

      <div className="space-y-0">
        <div className="stat-row">
          <span className="data-label">Guard height</span>
          <span className="data-value capitalize">{data.guard_height}</span>
        </div>

        <div className="stat-row">
          <span className="data-label">Lead hand</span>
          <span className={ACTIVITY_BADGE[data.lead_hand_activity] || "badge-neutral"}>
            {data.lead_hand_activity}
          </span>
        </div>

        <div className="stat-row">
          <span className="data-label">Rear hand</span>
          <span className={REAR_BADGE[data.rear_hand_position] || "badge-neutral"}>
            {data.rear_hand_position}
          </span>
        </div>

        <div className="pt-3">
          <div className="flex items-center justify-between mb-1">
            <span className="data-label">Chin exposure</span>
            <span className={chinBadge}>{chinRisk} — {data.chin_exposure_index.toFixed(2)}</span>
          </div>
          <Meter value={data.chin_exposure_index} />
        </div>
      </div>
    </div>
  );
}
